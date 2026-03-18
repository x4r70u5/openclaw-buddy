# 🤖 OpenClaw Buddy - AI Assistant Template for Signal

> A complete template for building your own AI assistant running on Signal — powered by OpenClaw + signal-cli.

---

## 💡 What is this?

**OpenClaw Buddy** is a ready-made skeleton for creating a personal AI assistant accessible through Signal Messenger. The assistant:

- **Responds to Signal messages** - both private and group
- **Remembers context** - via Markdown files and optionally Neo4j (graph database)
- **Acts proactively** - checks email, calendar, notifications (heartbeat)
- **Has personality** - configurable through `SOUL.md`
- **Learns** - updates its own files, draws conclusions from mistakes

Example of what you can build: a buddy-assistant that texts you on Signal, remembers your preferences, comments on AI news, and sends you notifications when something important happens.

---

## 📋 Requirements

### Required

| Tool | Version | Description |
|------|---------|-------------|
| [OpenClaw](https://openclaw.dev) | latest | Main runtime for the AI agent |
| [signal-cli](https://github.com/AsamK/signal-cli) | 0.13+ | Signal CLI client with HTTP daemon mode |
| Java | 21+ | Required by signal-cli |
| Node.js | 18+ | Required by OpenClaw |
| Python | 3.10+ | Helper scripts |

### Optional

| Tool | Description |
|------|-------------|
| [Neo4j Aura](https://neo4j.com/cloud/aura/) | Graph database for long-term memory (free tier available) |
| [atproto](https://pypi.org/project/atproto/) | Bluesky library for posting |
| Gmail OAuth | Email access via API |

---

## 🚀 Installation Step by Step

### Step 1: Clone this template

```bash
git clone https://github.com/YOUR_USERNAME/openclaw-buddy.git my-assistant
cd my-assistant
```

### Step 2: Install OpenClaw

```bash
npm install -g openclaw
openclaw --version
```

Details: [setup/openclaw-setup.md](setup/openclaw-setup.md)

### Step 3: Configure signal-cli

Download, install, and run signal-cli as an HTTP daemon on port 8080.

Details: [setup/signal-cli-setup.md](setup/signal-cli-setup.md)

### Step 4: Copy workspace to the OpenClaw directory

```bash
# Find the OpenClaw workspace directory (usually ~/clawd)
cp workspace/* ~/clawd/
```

### Step 5: Customize configuration files

Edit in order:

1. **`workspace/IDENTITY.md`** - give the assistant a name and personality
2. **`workspace/SOUL.md`** - define character and behavioral rules
3. **`workspace/USER.md`** - describe yourself (the assistant will read this)
4. **`workspace/TOOLS.md`** - configure Signal groups and other tools
5. **`workspace/HEARTBEAT.md`** - set up what the assistant should check proactively
6. **`workspace/AGENTS.md`** - agent instructions (you can leave defaults)

### Step 6: (Optional) Configure Neo4j

```bash
# Install the library
pip install neo4j

# Edit credentials in scripts
nano scripts/neo4j_context.py
nano scripts/neo4j_add.py
```

### Step 7: Launch!

```bash
# Make sure signal-cli daemon is running
curl -X POST http://localhost:8080/api/v1/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"version","id":1}'

# Start OpenClaw
openclaw start
```

---

## ⚙️ AI Model Configuration

OpenClaw supports multiple providers:

```bash
# Anthropic Claude (recommended)
openclaw config set model anthropic/claude-opus-4

# OpenAI GPT-4
openclaw config set model openai/gpt-4o

# OpenRouter (access to many models)
openclaw config set model openrouter/anthropic/claude-sonnet-4
```

---

## 🎭 Personalization - How to Make It "Come Alive"

### 1. Give it a name and character

In `IDENTITY.md` and `SOUL.md` describe who your assistant is. Don't make yet another "helpful AI" — give it a distinct personality:
- What language style does it use? (formal / casual / humorous)
- What are its interests?
- What "opinions" does it have?
- How does it react to different situations?

### 2. Describe yourself

`USER.md` is your profile — the assistant reads it at every session. The more you write here, the better it "knows" you:
- Your work, projects, interests
- How you like to be treated
- What you DON'T like (important!)
- Important dates, people in your life

### 3. Configure heartbeat

`HEARTBEAT.md` is a checklist the assistant runs proactively. You can set it to:
- Check your email every few hours
- Inform you about upcoming meetings
- Search for interesting AI news
- Text you if too much time has passed

### 4. Long-term memory

- **`MEMORY.md`** - the assistant saves important information here between sessions
- **Neo4j** (optional) - graph database for more structural memory
- **`memory/YYYY-MM-DD.md`** - daily logs of what happened

### 5. Tips

- ✅ Text the assistant naturally — it responds in a similar tone
- ✅ Correct it when it does something wrong — it learns
- ✅ Give it access to tools you like (Bluesky, Gmail, etc.)
- ⚠️ Don't give it access to accounts that can't "send weird things"
- ⏳ Don't expect perfection right away — it takes a few days of calibration

---

## 🗂️ Project Structure

```
openclaw-buddy/
├── README.md                    # This file
├── workspace/                   # Files to copy to ~/clawd/
│   ├── AGENTS.md               # Agent instructions
│   ├── SOUL.md                 # Assistant personality
│   ├── USER.md                 # User profile
│   ├── MEMORY.md               # Long-term memory
│   ├── TOOLS.md                # Tool configuration
│   ├── HEARTBEAT.md            # Proactive checks
│   └── IDENTITY.md             # Assistant identity
├── scripts/                     # Python helper scripts
│   ├── neo4j_context.py        # Load context from Neo4j
│   └── neo4j_add.py            # Add facts to Neo4j
├── database/                    # Database schemas
│   ├── schema.sql              # SQLite schema
│   └── neo4j-schema.md         # Neo4j schema and Cypher queries
├── setup/                       # Installation guides
│   ├── signal-cli-setup.md     # signal-cli configuration
│   └── openclaw-setup.md       # OpenClaw configuration
└── examples/                    # Example scripts
    ├── send_message.py         # Sending Signal messages
    └── bsky_post.py            # Posting to Bluesky
```

---

## 🔧 Troubleshooting / FAQ

### signal-cli won't start

```bash
# Check if Java 21+ is installed
java -version

# Check if port 8080 is in use
netstat -an | grep 8080

# Run with logs
signal-cli --verbose daemon --http 127.0.0.1:8080
```

### OpenClaw can't see Signal

Make sure the OpenClaw configuration has the correct daemon address:
```bash
# Check configuration
openclaw config show

# signal-cli should be running at
http://127.0.0.1:8080
```

### Assistant doesn't respond to messages

1. Check if OpenClaw is running (`openclaw status`)
2. Check if the signal-cli daemon is running and receiving messages
3. Check OpenClaw logs for errors
4. Send a test message and check logs in real time

### Broken encoding / garbled characters (Windows)

On Windows always use:
```powershell
# Instead of Invoke-RestMethod, use curl.exe
C:\Windows\System32\curl.exe -X POST ...

# For Python with emoji/special characters
python -X utf8 your_script.py
```

### Assistant "forgets" between sessions

This is normal — LLMs don't have state between sessions. That's why the file system exists:
- Make sure `AGENTS.md` instructs reading `memory/YYYY-MM-DD.md` at startup
- Make sure the assistant saves important things to files during sessions
- Consider Neo4j for structural long-term memory

### Assistant responds in the wrong language or tone

Edit `SOUL.md` and `USER.md` — these are the most important files affecting communication style. Be specific: instead of "talk naturally" write exactly what bothers you and how you want it to speak.

### Too many notifications / not enough notifications

Adjust `HEARTBEAT.md` — you can change check frequency, add or remove tasks. Remember: each heartbeat is an API call (token cost).

---

## 🔐 Security

- **Never commit** files with real API keys, tokens, or phone numbers
- `.gitignore` in this repository excludes `TOOLS.md` and `*.pickle` - add your secrets there
- signal-cli daemon listens only on `localhost` by default - don't expose it externally
- The assistant has access to your files and messages - treat it as a trusted program

---

## 🤝 Contributing

Pull requests are welcome! Especially:
- Examples of new tools (Slack, Teams, Telegram)
- SOUL.md templates for different personalities
- Scripts for new data sources
- Documentation improvements

---

## 📄 License

MIT - do what you want, but don't blame me if your assistant decides to send weird messages to your friends. 😄

---

*Built with ❤️ and a lot of experimentation.*
