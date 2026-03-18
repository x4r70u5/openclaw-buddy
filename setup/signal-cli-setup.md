# signal-cli Configuration

Installation and configuration guide for signal-cli as an HTTP daemon for OpenClaw.

---

## What is signal-cli?

[signal-cli](https://github.com/AsamK/signal-cli) is an unofficial command-line client for Signal Messenger.
It allows sending/receiving Signal messages via API — without a graphical interface.

OpenClaw uses signal-cli in **HTTP daemon** mode on port 8080.

---

## Requirements

- Java 21+ (JDK or JRE)
- A phone number for Signal registration
  - **Recommended**: a dedicated number (not your main one!)
  - Can be an eSIM number, VoIP (e.g. JustVoip), or a regular prepaid number

---

## Step 1: Download signal-cli

### Linux / macOS

```bash
# Check the latest version at: https://github.com/AsamK/signal-cli/releases
VERSION="0.13.7"

# Linux x86_64
wget "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}-Linux-x86_64.tar.gz"
tar xzf "signal-cli-${VERSION}-Linux-x86_64.tar.gz"
sudo cp "signal-cli-${VERSION}/bin/signal-cli" /usr/local/bin/

# Verify
signal-cli --version
```

### Windows

```powershell
# Download the JAR file (works on all platforms with Java)
$VERSION = "0.13.7"
$URL = "https://github.com/AsamK/signal-cli/releases/download/v$VERSION/signal-cli-$VERSION.tar.gz"

# Or download manually and extract
# File: signal-cli-{VERSION}.tar.gz
# Contains: signal-cli-{VERSION}/lib/*.jar

# Run via wrapper (create a signal-cli.bat file):
# java -jar C:\signal-cli\lib\signal-cli-{VERSION}-all.jar %*
```

### Docker (easiest method)

```bash
docker pull bbernhard/signal-cli-rest-api
docker run -d \
  --name signal-cli \
  -p 8080:8080 \
  -v /path/to/signal-data:/home/.local/share/signal-cli \
  bbernhard/signal-cli-rest-api
```

---

## Step 2: Register your phone number

### Option A: New number (registration)

```bash
# Register the phone number
# Format: +COUNTRY_CODE_NUMBER (e.g. +48572699999)
signal-cli -a +YOUR_NUMBER register

# You'll receive an SMS with a verification code
signal-cli -a +YOUR_NUMBER verify CODE_FROM_SMS
```

### Option B: Link to an existing Signal account

```bash
# Generate a linking URI
signal-cli link --name "MyAssistant"
# A link will appear: tsdevice://?uuid=...
# Scan the QR code in the Signal app on your phone:
# Settings → Linked Devices → + Link New Device
```

---

## Step 3: Test basic functionality

```bash
# Send a test message to yourself
signal-cli -a +YOUR_NUMBER send -m "Hey, it's me — signal-cli!" +YOUR_NUMBER

# Receive messages (once)
signal-cli -a +YOUR_NUMBER receive

# List groups
signal-cli -a +YOUR_NUMBER listGroups
```

---

## Step 4: Run as HTTP daemon

Signal-cli in daemon mode exposes a REST API — OpenClaw uses it.

```bash
# Start HTTP daemon on port 8080
signal-cli -a +YOUR_NUMBER daemon --http 127.0.0.1:8080

# Or without binding to a specific address (WARNING: accessible from the network!)
signal-cli -a +YOUR_NUMBER daemon --http 0.0.0.0:8080
```

### Important: Only run on localhost!

The HTTP daemon has no authentication. Always bind to `127.0.0.1`, not `0.0.0.0`.

---

## Step 5: Test the HTTP daemon

```bash
# Check version
curl -s http://localhost:8080/api/v1/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"version","id":1}'

# Send a test message (replace the number!)
curl -X POST http://localhost:8080/api/v1/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "send",
    "id": 1,
    "params": {
      "account": "+YOUR_NUMBER",
      "recipient": ["+YOUR_NUMBER"],
      "message": "Test from signal-cli HTTP API!"
    }
  }'
```

### Windows — curl in PowerShell

```powershell
# On Windows curl may have issues with JSON. Use Invoke-WebRequest:
$body = @{
    jsonrpc = "2.0"
    method = "send"
    id = 1
    params = @{
        account = "+YOUR_NUMBER"
        recipient = @("+YOUR_NUMBER")
        message = "Test from PowerShell!"
    }
} | ConvertTo-Json -Depth 5

$headers = @{"Content-Type" = "application/json"}
Invoke-WebRequest -Uri "http://localhost:8080/api/v1/rpc" -Method POST -Headers $headers -Body $body
```

---

## Step 6: Run as a system service

### Linux (systemd)

```ini
# /etc/systemd/system/signal-cli.service
[Unit]
Description=signal-cli daemon
After=network.target

[Service]
Type=simple
User=signal
ExecStart=/usr/local/bin/signal-cli -a +YOUR_NUMBER daemon --http 127.0.0.1:8080
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable signal-cli
sudo systemctl start signal-cli
sudo systemctl status signal-cli
```

### Windows (Task Scheduler)

```powershell
# Create a task that starts at logon
$action = New-ScheduledTaskAction -Execute "java" `
  -Argument "-jar C:\signal-cli\lib\signal-cli-0.13.7-all.jar -a +YOUR_NUMBER daemon --http 127.0.0.1:8080"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "signal-cli" -Action $action -Trigger $trigger -RunLevel Highest
```

---

## Step 7: Get group IDs

If you want the assistant to work in Signal groups:

```bash
# Via CLI
signal-cli -a +YOUR_NUMBER listGroups

# Via HTTP daemon
curl -X POST http://localhost:8080/api/v1/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"listGroups","id":1,"params":{"account":"+YOUR_NUMBER"}}'
```

Copy the `id` value for each group — you'll need it in TOOLS.md.

---

## Step 8: Configuration in OpenClaw

In the OpenClaw configuration file (usually `~/.openclaw/config.json`):

```json
{
  "plugins": {
    "signal": {
      "enabled": true,
      "account": "+YOUR_NUMBER",
      "daemonUrl": "http://127.0.0.1:8080"
    }
  }
}
```

---

## Troubleshooting

### Problem: "Could not connect to signal-cli daemon"
- Check if the daemon is running: `curl http://localhost:8080/api/v1/rpc -d '{"jsonrpc":"2.0","method":"version","id":1}'`
- Check the port: `netstat -an | grep 8080`

### Problem: "Registration failed"
- Check if the number is valid (format +COUNTRYCODE)
- Try voice method instead of SMS: `signal-cli register --voice`

### Problem: Groups don't work
- Check if the group ID is in the correct format (base64)
- OpenClaw may modify uppercase letters in base64 — use a direct RPC call (see TOOLS.md)

### Problem: Messages don't reach the agent
- Check OpenClaw logs: `openclaw logs`
- Check if the number is linked to the account: `signal-cli -a +YOUR_NUMBER listIdentities`

---

## Useful Links

- [signal-cli Releases](https://github.com/AsamK/signal-cli/releases)
- [signal-cli Wiki](https://github.com/AsamK/signal-cli/wiki)
- [signal-cli REST API Docker](https://github.com/bbernhard/signal-cli-rest-api)
- [OpenClaw Documentation](https://openclaw.dev)
