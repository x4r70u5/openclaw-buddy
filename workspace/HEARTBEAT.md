# HEARTBEAT.md - Proactive Checks

<!--
INSTRUCTIONS:
This file is a checklist for the assistant during heartbeats.
A heartbeat is a periodic "pulse" — OpenClaw sends a message to the assistant
at regular intervals (e.g. every 30 minutes) and the assistant runs this checklist.

If nothing important is happening → respond HEARTBEAT_OK
If something needs attention → send a message to the user

RULE: Don't spam! Only write when you have something worth saying.
Silent heartbeats (HEARTBEAT_OK) are fine and encouraged.

Customize this list to your needs — remove/add sections.
-->

---

## Heartbeat Rules

**When to message the user:**
- An important email arrived
- Upcoming meeting (< 2h)
- Found something interesting/urgent
- More than 8h since last conversation and you have something worth saying

**When to stay silent (HEARTBEAT_OK):**
- Late night (23:00-08:00) unless urgent
- User is clearly busy
- Nothing new since last check
- Last check was < 30 minutes ago

---

## Checklist

### 📧 Email (if Gmail configured)
<!-- Uncomment and customize when Gmail is configured -->
<!--
Check unread emails:
```python
python /path/to/check_gmail.py
```
- Look for: urgent emails, from important senders
- Ignore: newsletters, promotions, automated notifications
- Alert threshold: emails from specific people or containing "urgent/ASAP"
-->

### 📅 Calendar (if Google Calendar configured)
<!-- Uncomment when Calendar is configured -->
<!--
Check upcoming events:
```python
python /path/to/check_calendar.py
```
- Alert on: meetings within 2h, agenda changes
- Ignore: all-day events unless something important
-->

### 🤖 AI News (1-2x daily)
<!--
Quick check on what's new in AI:
- Brave Search: "AI news today site:techcrunch.com OR site:theverge.com"
- Or RSS from favorite blogs
- Send to user if something truly interesting
- Don't spam daily — only for real breakthroughs
-->

### 🦋 Bluesky/Social (if configured)
<!-- Uncomment when social media are configured -->
<!--
Check notifications, respond to mentions:
```python
python /path/to/check_bsky.py
```
-->

### 🧠 Memory Maintenance (every few days)
<!--
Periodically (not every heartbeat!):
1. Review recent memory/YYYY-MM-DD.md files
2. Identify what's worth moving to MEMORY.md
3. Update MEMORY.md
4. Clean up outdated entries
-->

---

## Check State

<!--
NOTE (Windows): curl may have issues with JSON on Windows PowerShell.
Instead of curl, use Invoke-WebRequest or Python scripts.

PowerShell example:
$headers = @{"Content-Type"="application/json"}
$body = '{"query": "AI news"}'
Invoke-WebRequest -Uri "https://api.example.com" -Method POST -Headers $headers -Body $body
-->

The assistant can track last checks in the file:
`memory/heartbeat-state.json`

```json
{
  "lastChecks": {
    "email": null,
    "calendar": null,
    "news": null,
    "social": null,
    "memoryMaintenance": null
  },
  "notes": "The assistant can leave notes here between heartbeats"
}
```

---

*Edit this file when you want to change what the assistant checks proactively.*
