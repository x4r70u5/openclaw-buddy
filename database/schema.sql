-- =============================================================
-- schema.sql - SQLite Schema for AI Assistant Local Database
-- =============================================================
-- 
-- This schema defines the local SQLite database structure for
-- storing Signal messages, knowledge base, and assistant state.
--
-- Usage:
--   sqlite3 memory/assistant.db < schema.sql
--
-- Or in Python:
--   import sqlite3
--   conn = sqlite3.connect("memory/assistant.db")
--   with open("database/schema.sql") as f:
--       conn.executescript(f.read())
-- =============================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- =============================================================
-- Signal Messages
-- Stores all Signal messages for context and search
-- =============================================================
CREATE TABLE IF NOT EXISTS signal_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       INTEGER NOT NULL UNIQUE,   -- Signal timestamp (ms)
    sender          TEXT NOT NULL,              -- Phone number or name
    sender_uuid     TEXT,                       -- Signal UUID (stable identifier)
    group_id        TEXT,                       -- NULL for DMs
    message         TEXT NOT NULL,
    attachments     TEXT,                       -- JSON array of attachment paths
    quoted_message  INTEGER,                    -- FK to quoted message timestamp
    is_outgoing     INTEGER NOT NULL DEFAULT 0, -- 0=incoming, 1=outgoing (our messages)
    read_at         INTEGER,                    -- When we read it (ms)
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now') * 1000)
);

CREATE INDEX IF NOT EXISTS idx_signal_messages_timestamp ON signal_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_signal_messages_sender ON signal_messages(sender);
CREATE INDEX IF NOT EXISTS idx_signal_messages_group ON signal_messages(group_id);

-- =============================================================
-- Knowledge Base
-- Local storage for facts and information (alternative to Neo4j)
-- =============================================================
CREATE TABLE IF NOT EXISTS knowledge_base (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content         TEXT NOT NULL,
    category        TEXT,                       -- e.g., 'fact', 'lesson', 'preference'
    importance      TEXT DEFAULT 'normal',      -- low / normal / high / critical
    source          TEXT,                       -- Where this came from
    tags            TEXT,                       -- JSON array of tags
    person          TEXT,                       -- Person this is about (if any)
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now') * 1000),
    updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now') * 1000),
    expires_at      INTEGER                     -- NULL = never expires
);

CREATE INDEX IF NOT EXISTS idx_kb_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_kb_importance ON knowledge_base(importance);
CREATE INDEX IF NOT EXISTS idx_kb_person ON knowledge_base(person);

-- Full-text search on knowledge base
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_base_fts USING fts5(
    content,
    tags,
    person,
    content=knowledge_base,
    content_rowid=id
);

-- =============================================================
-- Conversations
-- Tracks conversation threads for context
-- =============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    channel         TEXT NOT NULL,              -- e.g., 'signal', 'signal_group_XXX'
    participant     TEXT NOT NULL,              -- Phone number or group ID
    last_message_at INTEGER,
    message_count   INTEGER DEFAULT 0,
    summary         TEXT,                       -- AI-generated summary of conversation
    summary_updated_at INTEGER,
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now') * 1000)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_conversations_channel_participant 
    ON conversations(channel, participant);

-- =============================================================
-- Assistant State
-- Key-value store for assistant configuration and state
-- =============================================================
CREATE TABLE IF NOT EXISTS assistant_state (
    key             TEXT PRIMARY KEY,
    value           TEXT NOT NULL,
    updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now') * 1000)
);

-- Default state values
INSERT OR IGNORE INTO assistant_state (key, value) VALUES
    ('heartbeat_last_check', '0'),
    ('heartbeat_last_email_check', '0'),
    ('heartbeat_last_calendar_check', '0'),
    ('heartbeat_last_news_check', '0'),
    ('last_proactive_message', '0'),
    ('setup_complete', '0');

-- =============================================================
-- Reminders
-- Scheduled reminders for the assistant to send
-- =============================================================
CREATE TABLE IF NOT EXISTS reminders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient       TEXT NOT NULL,              -- Phone number or group ID
    message         TEXT NOT NULL,
    scheduled_for   INTEGER NOT NULL,           -- Unix timestamp (ms)
    is_group        INTEGER NOT NULL DEFAULT 0,
    sent_at         INTEGER,                    -- NULL = not sent yet
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now') * 1000)
);

CREATE INDEX IF NOT EXISTS idx_reminders_scheduled ON reminders(scheduled_for) 
    WHERE sent_at IS NULL;

-- =============================================================
-- Search helper view: recent messages with conversation context
-- =============================================================
CREATE VIEW IF NOT EXISTS recent_messages AS
SELECT 
    m.timestamp,
    m.sender,
    m.group_id,
    m.message,
    m.is_outgoing,
    CASE 
        WHEN m.group_id IS NOT NULL THEN 'group:' || m.group_id
        ELSE 'dm:' || m.sender
    END AS conversation_key,
    datetime(m.timestamp / 1000, 'unixepoch') AS sent_at_human
FROM signal_messages m
ORDER BY m.timestamp DESC;

-- =============================================================
-- Trigger: update knowledge_base updated_at on change
-- =============================================================
CREATE TRIGGER IF NOT EXISTS trg_kb_updated_at
    AFTER UPDATE ON knowledge_base
BEGIN
    UPDATE knowledge_base 
    SET updated_at = strftime('%s','now') * 1000
    WHERE id = NEW.id;
END;
