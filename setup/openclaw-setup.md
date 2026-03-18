# OpenClaw Configuration

Installation and configuration guide for OpenClaw — the runtime for your AI assistant.

---

## What is OpenClaw?

[OpenClaw](https://openclaw.dev) is a framework for building AI agents with access to external tools and communication channels. It connects a language model (Claude, GPT, etc.) with Signal Messenger, enabling you to create a personal AI assistant.

---

## Requirements

- Node.js 18+ (recommended: 20 LTS or 22)
- npm or yarn
- Account with an AI provider (Anthropic, OpenAI, or OpenRouter)
- signal-cli configured and running (see [signal-cli-setup.md](signal-cli-setup.md))

---

## Step 1: Install Node.js

### Linux / macOS

```bash
# Via nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 22
nvm use 22
node --version  # Should show v22.x.x
```

### Windows

```powershell
# Via winget
winget install OpenJS.NodeJS.LTS

# Or download the installer from https://nodejs.org/
```

---

## Step 2: Install OpenClaw

```bash
npm install -g openclaw

# Verify
openclaw --version
```

---

## Step 3: Initialize workspace

```bash
# Create a directory for the assistant
mkdir ~/my-assistant
cd ~/my-assistant

# Copy files from the template
cp /path/to/openclaw-buddy/workspace/* .
```

---

## Step 4: Configure API key

### Anthropic Claude (recommended)

```bash
# Get your API key from: https://console.anthropic.com/
openclaw config set apiKey "sk-ant-api03-YOUR_KEY"
openclaw config set model "anthropic/claude-opus-4"

# Or via environment variables
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_KEY"
```

### OpenAI

```bash
# Get your API key from: https://platform.openai.com/
openclaw config set apiKey "sk-YOUR_KEY"
openclaw config set model "openai/gpt-4o"
```

### OpenRouter (access to many models through one key)

```bash
# Get your API key from: https://openrouter.ai/
openclaw config set apiKey "sk-or-v1-YOUR_KEY"
openclaw config set model "openrouter/anthropic/claude-sonnet-4"
```

---

## Step 5: Configure Signal

```bash
# Point to the signal-cli daemon
openclaw config set plugins.signal.account "+YOUR_NUMBER"
openclaw config set plugins.signal.daemonUrl "http://127.0.0.1:8080"
openclaw config set plugins.signal.enabled true
```

Or edit the configuration file directly:

```json
// ~/.openclaw/config.json (or %APPDATA%\openclaw\config.json on Windows)
{
  "model": "anthropic/claude-opus-4",
  "apiKey": "YOUR_API_KEY",
  "workspace": "/path/to/my-assistant",
  "plugins": {
    "signal": {
      "enabled": true,
      "account": "+YOUR_PHONE_NUMBER",
      "daemonUrl": "http://127.0.0.1:8080"
    }
  }
}
```

---

## Step 6: First launch

```bash
# Check configuration
openclaw config show

# Check Signal connection
openclaw gateway status

# Start the assistant
openclaw start
```

After starting, send a Signal message to the assistant's number — it should respond!

---

## Step 7: Heartbeat (proactive checks)

Heartbeat is a mechanism that regularly "wakes up" the assistant to run through the checklist from HEARTBEAT.md.

```bash
# Set heartbeat every 30 minutes
openclaw config set heartbeat.interval 1800
openclaw config set heartbeat.enabled true

# Optional: a specific model for heartbeats (cheaper)
openclaw config set heartbeat.model "anthropic/claude-haiku-3-5"
```

---

## Step 8: Configure Signal groups

If you want the assistant to work in Signal groups:

```bash
# First find the group ID (see signal-cli-setup.md)
# Then add the group to OpenClaw:
openclaw config set plugins.signal.groups[0].id "YOUR_GROUP_ID="
openclaw config set plugins.signal.groups[0].name "My Group"
```

---

## Running as a service

### Linux (systemd)

```ini
# /etc/systemd/system/openclaw.service
[Unit]
Description=OpenClaw AI Assistant
After=network.target signal-cli.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username
ExecStart=/usr/local/bin/openclaw start
Restart=on-failure
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable openclaw
sudo systemctl start openclaw
```

### Windows (Task Scheduler)

```powershell
$action = New-ScheduledTaskAction -Execute "openclaw" -Argument "start"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "OpenClaw" -Action $action -Trigger $trigger -RunLevel Highest
```

---

## Useful Commands

```bash
# Gateway status (Signal connection)
openclaw gateway status

# Show logs
openclaw logs

# Show live logs
openclaw logs --follow

# Stop the assistant
openclaw stop

# Restart
openclaw restart

# Show configuration
openclaw config show

# List active agent sessions
openclaw sessions list
```

---

## Troubleshooting

### "Cannot connect to gateway"
```bash
# Check if signal-cli daemon is running
curl http://localhost:8080/api/v1/rpc -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"version","id":1}'

# Check configuration
openclaw config show | grep signal
```

### "API key invalid"
```bash
# Check API key
openclaw config show | grep apiKey

# Test directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

### Agent doesn't read workspace files
```bash
# Check if workspace is properly configured
openclaw config show | grep workspace

# Make sure files are in the workspace directory
ls ~/my-assistant/
# Should show: AGENTS.md, SOUL.md, USER.md, MEMORY.md, TOOLS.md, HEARTBEAT.md, IDENTITY.md
```

---

## Useful Links

- [OpenClaw Documentation](https://openclaw.dev)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Anthropic API Keys](https://console.anthropic.com/)
- [OpenRouter](https://openrouter.ai/)
- [awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents)
