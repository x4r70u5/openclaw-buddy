# Konfiguracja OpenClaw

Przewodnik instalacji i konfiguracji OpenClaw — runtime dla Twojego AI asystenta.

---

## Czym jest OpenClaw?

[OpenClaw](https://openclaw.dev) to framework do budowania AI agentów z dostępem do zewnętrznych narzędzi i kanałów komunikacji. Łączy model językowy (Claude, GPT, itp.) z Signal Messenger, umożliwiając stworzenie personalnego AI asystenta.

---

## Wymagania

- Node.js 18+ (zalecane: 20 LTS lub 22)
- npm lub yarn
- Konto u providera AI (Anthropic, OpenAI, lub OpenRouter)
- signal-cli skonfigurowany i działający (patrz [signal-cli-setup.md](signal-cli-setup.md))

---

## Krok 1: Instalacja Node.js

### Linux / macOS

```bash
# Przez nvm (zalecane)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 22
nvm use 22
node --version  # Powinno pokazać v22.x.x
```

### Windows

```powershell
# Przez winget
winget install OpenJS.NodeJS.LTS

# Lub pobierz instalator z https://nodejs.org/
```

---

## Krok 2: Instalacja OpenClaw

```bash
npm install -g openclaw

# Weryfikacja
openclaw --version
```

---

## Krok 3: Zainicjuj workspace

```bash
# Utwórz katalog dla asystenta
mkdir ~/moj-asystent
cd ~/moj-asystent

# Skopiuj pliki z szablonu
cp /ścieżka/do/openclaw-buddy/workspace/* .
```

---

## Krok 4: Skonfiguruj klucz API

### Anthropic Claude (rekomendowany)

```bash
# Pobierz klucz API z: https://console.anthropic.com/
openclaw config set apiKey "sk-ant-api03-TWOJ_KLUCZ"
openclaw config set model "anthropic/claude-opus-4"

# Lub przez zmienne środowiskowe
export ANTHROPIC_API_KEY="sk-ant-api03-TWOJ_KLUCZ"
```

### OpenAI

```bash
# Pobierz klucz API z: https://platform.openai.com/
openclaw config set apiKey "sk-TWOJ_KLUCZ"
openclaw config set model "openai/gpt-4o"
```

### OpenRouter (dostęp do wielu modeli przez jeden klucz)

```bash
# Pobierz klucz API z: https://openrouter.ai/
openclaw config set apiKey "sk-or-v1-TWOJ_KLUCZ"
openclaw config set model "openrouter/anthropic/claude-sonnet-4"
```

---

## Krok 5: Skonfiguruj Signal

```bash
# Wskaż daemon signal-cli
openclaw config set plugins.signal.account "+TWOJ_NUMER"
openclaw config set plugins.signal.daemonUrl "http://127.0.0.1:8080"
openclaw config set plugins.signal.enabled true
```

Lub edytuj bezpośrednio plik konfiguracyjny:

```json
// ~/.openclaw/config.json (lub %APPDATA%\openclaw\config.json na Windows)
{
  "model": "anthropic/claude-opus-4",
  "apiKey": "TWOJ_KLUCZ_API",
  "workspace": "/ścieżka/do/moj-asystent",
  "plugins": {
    "signal": {
      "enabled": true,
      "account": "+TWOJ_NUMER_TELEFONU",
      "daemonUrl": "http://127.0.0.1:8080"
    }
  }
}
```

---

## Krok 6: Pierwsze uruchomienie

```bash
# Sprawdź konfigurację
openclaw config show

# Sprawdź połączenie z Signal
openclaw gateway status

# Uruchom asystenta
openclaw start
```

Po uruchomieniu, wyślij wiadomość Signal na numer asystenta — powinien odpowiedzieć!

---

## Krok 7: Heartbeat (proaktywne sprawdzenia)

Heartbeat to mechanizm który regularnie "budzi" asystenta żeby wykonał checklistę z HEARTBEAT.md.

```bash
# Ustaw heartbeat co 30 minut
openclaw config set heartbeat.interval 1800
openclaw config set heartbeat.enabled true

# Opcjonalnie: specjalny model dla heartbeatów (tańszy)
openclaw config set heartbeat.model "anthropic/claude-haiku-3-5"
```

---

## Krok 8: Konfiguracja grup Signal

Jeśli chcesz żeby asystent działał w grupach Signal:

```bash
# Najpierw znajdź ID grupy (patrz signal-cli-setup.md)
# Potem dodaj grupę do OpenClaw:
openclaw config set plugins.signal.groups[0].id "TWOJE_GROUP_ID="
openclaw config set plugins.signal.groups[0].name "Moja Grupa"
```

---

## Uruchamianie jako usługa

### Linux (systemd)

```ini
# /etc/systemd/system/openclaw.service
[Unit]
Description=OpenClaw AI Assistant
After=network.target signal-cli.service

[Service]
Type=simple
User=twoja_nazwa_uzytkownika
WorkingDirectory=/home/twoja_nazwa_uzytkownika
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

## Przydatne Komendy

```bash
# Status Gateway (połączenie z Signal)
openclaw gateway status

# Wyświetl logi
openclaw logs

# Wyświetl logi na żywo
openclaw logs --follow

# Zatrzymaj asystenta
openclaw stop

# Restart
openclaw restart

# Pokaż konfigurację
openclaw config show

# Lista aktywnych sesji agenta
openclaw sessions list
```

---

## Rozwiązywanie Problemów

### "Cannot connect to gateway"
```bash
# Sprawdź czy signal-cli daemon działa
curl http://localhost:8080/api/v1/rpc -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"version","id":1}'

# Sprawdź konfigurację
openclaw config show | grep signal
```

### "API key invalid"
```bash
# Sprawdź klucz API
openclaw config show | grep apiKey

# Przetestuj bezpośrednio
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: TWOJ_KLUCZ" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

### Agent nie czyta plików workspace
```bash
# Sprawdź czy workspace jest prawidłowo skonfigurowany
openclaw config show | grep workspace

# Upewnij się że pliki są w katalogu workspace
ls ~/moj-asystent/
# Powinno pokazać: AGENTS.md, SOUL.md, USER.md, MEMORY.md, TOOLS.md, HEARTBEAT.md, IDENTITY.md
```

---

## Przydatne Linki

- [OpenClaw Dokumentacja](https://openclaw.dev)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Anthropic API Keys](https://console.anthropic.com/)
- [OpenRouter](https://openrouter.ai/)
- [awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents)
