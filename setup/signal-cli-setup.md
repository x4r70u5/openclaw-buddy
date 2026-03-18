# Konfiguracja signal-cli

Przewodnik instalacji i konfiguracji signal-cli jako daemon HTTP dla OpenClaw.

---

## Czym jest signal-cli?

[signal-cli](https://github.com/AsamK/signal-cli) to nieoficjalny klient wiersza poleceń dla Signal Messenger. 
Pozwala na wysyłanie/odbieranie wiadomości Signal przez API — bez interfejsu graficznego.

OpenClaw używa signal-cli w trybie **HTTP daemon** na porcie 8080.

---

## Wymagania

- Java 21+ (JDK lub JRE)
- Numer telefonu do rejestracji w Signal
  - **Zalecane**: dedykowany numer (nie Twój główny!)
  - Może to być numer z eSIM, VoIP (np. JustVoip), lub zwykły numer prepaid

---

## Krok 1: Pobierz signal-cli

### Linux / macOS

```bash
# Sprawdź najnowszą wersję na: https://github.com/AsamK/signal-cli/releases
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
# Pobierz plik JAR (działa na wszystkich platformach z Javą)
$VERSION = "0.13.7"
$URL = "https://github.com/AsamK/signal-cli/releases/download/v$VERSION/signal-cli-$VERSION.tar.gz"

# Lub pobierz ręcznie i wypakuj
# Plik: signal-cli-{VERSION}.tar.gz
# Zawiera: signal-cli-{VERSION}/lib/*.jar

# Uruchamianie przez wrapper (utwórz plik signal-cli.bat):
# java -jar C:\signal-cli\lib\signal-cli-{VERSION}-all.jar %*
```

### Docker (najprostszy sposób)

```bash
docker pull bbernhard/signal-cli-rest-api
docker run -d \
  --name signal-cli \
  -p 8080:8080 \
  -v /path/to/signal-data:/home/.local/share/signal-cli \
  bbernhard/signal-cli-rest-api
```

---

## Krok 2: Zarejestruj numer telefonu

### Opcja A: Nowy numer (rejestracja)

```bash
# Zarejestruj numer telefonu
# Format: +KRAJ_KOD_NUMER (np. +48572699999)
signal-cli -a +TWOJ_NUMER register

# Otrzymasz SMS z kodem weryfikacyjnym
signal-cli -a +TWOJ_NUMER verify KOD_Z_SMS
```

### Opcja B: Połącz z istniejącym kontem Signal (link)

```bash
# Wygeneruj link do połączenia
signal-cli link --name "MojAsystent"
# Wyświetli się link: tsdevice://?uuid=...
# Zeskanuj QR kod w aplikacji Signal na telefonie:
# Ustawienia → Połączone urządzenia → + Połącz nowe urządzenie
```

---

## Krok 3: Przetestuj podstawowe działanie

```bash
# Wyślij testową wiadomość do siebie
signal-cli -a +TWOJ_NUMER send -m "Hej, to ja — signal-cli!" +TWOJ_NUMER

# Odbierz wiadomości (raz)
signal-cli -a +TWOJ_NUMER receive

# Listuj grupy
signal-cli -a +TWOJ_NUMER listGroups
```

---

## Krok 4: Uruchom jako daemon HTTP

Signal-cli w trybie daemon wystawia REST API — OpenClaw z niego korzysta.

```bash
# Uruchom daemon HTTP na porcie 8080
signal-cli -a +TWOJ_NUMER daemon --http 127.0.0.1:8080

# Lub bez bindowania do konkretnego adresu (UWAGA: dostępny z sieci!)
signal-cli -a +TWOJ_NUMER daemon --http 0.0.0.0:8080
```

### Ważne: Uruchamiaj tylko na localhost!

Daemon HTTP nie ma uwierzytelniania. Zawsze binduj do `127.0.0.1`, nie `0.0.0.0`.

---

## Krok 5: Przetestuj daemon HTTP

```bash
# Sprawdź wersję
curl -s http://localhost:8080/api/v1/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"version","id":1}'

# Wyślij wiadomość testową (podmień numer!)
curl -X POST http://localhost:8080/api/v1/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "send",
    "id": 1,
    "params": {
      "account": "+TWOJ_NUMER",
      "recipient": ["+TWOJ_NUMER"],
      "message": "Test z signal-cli HTTP API!"
    }
  }'
```

### Windows — curl w PowerShell

```powershell
# Na Windows curl może mieć problemy z JSON. Użyj Invoke-WebRequest:
$body = @{
    jsonrpc = "2.0"
    method = "send"
    id = 1
    params = @{
        account = "+TWOJ_NUMER"
        recipient = @("+TWOJ_NUMER")
        message = "Test z PowerShell!"
    }
} | ConvertTo-Json -Depth 5

$headers = @{"Content-Type" = "application/json"}
Invoke-WebRequest -Uri "http://localhost:8080/api/v1/rpc" -Method POST -Headers $headers -Body $body
```

---

## Krok 6: Uruchamianie jako usługa systemowa

### Linux (systemd)

```ini
# /etc/systemd/system/signal-cli.service
[Unit]
Description=signal-cli daemon
After=network.target

[Service]
Type=simple
User=signal
ExecStart=/usr/local/bin/signal-cli -a +TWOJ_NUMER daemon --http 127.0.0.1:8080
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
# Utwórz zadanie które startuje przy logowaniu
$action = New-ScheduledTaskAction -Execute "java" `
  -Argument "-jar C:\signal-cli\lib\signal-cli-0.13.7-all.jar -a +TWOJ_NUMER daemon --http 127.0.0.1:8080"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "signal-cli" -Action $action -Trigger $trigger -RunLevel Highest
```

---

## Krok 7: Pobierz ID grup

Jeśli asystent ma działać w grupach Signal:

```bash
# Przez CLI
signal-cli -a +TWOJ_NUMER listGroups

# Przez HTTP daemon
curl -X POST http://localhost:8080/api/v1/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"listGroups","id":1,"params":{"account":"+TWOJ_NUMER"}}'
```

Skopiuj wartość `id` dla każdej grupy — będziesz jej potrzebował w TOOLS.md.

---

## Krok 8: Konfiguracja w OpenClaw

W pliku konfiguracyjnym OpenClaw (zwykle `~/.openclaw/config.json`):

```json
{
  "plugins": {
    "signal": {
      "enabled": true,
      "account": "+TWOJ_NUMER",
      "daemonUrl": "http://127.0.0.1:8080"
    }
  }
}
```

---

## Rozwiązywanie Problemów

### Problem: "Could not connect to signal-cli daemon"
- Sprawdź czy daemon działa: `curl http://localhost:8080/api/v1/rpc -d '{"jsonrpc":"2.0","method":"version","id":1}'`
- Sprawdź port: `netstat -an | grep 8080`

### Problem: "Registration failed" 
- Sprawdź czy numer jest prawidłowy (format +KRAJKOD)
- Spróbuj metodą voice zamiast SMS: `signal-cli register --voice`

### Problem: Grupy nie działają
- Sprawdź czy ID grupy jest w prawidłowym formacie (base64)
- OpenClaw może modyfikować wielkie litery w base64 — użyj bezpośredniego wywołania RPC (patrz TOOLS.md)

### Problem: Wiadomości nie dochodzą do agenta
- Sprawdź logi OpenClaw: `openclaw logs`
- Sprawdź czy numer jest powiązany z kontem: `signal-cli -a +TWOJ_NUMER listIdentities`

---

## Przydatne Linki

- [signal-cli Releases](https://github.com/AsamK/signal-cli/releases)
- [signal-cli Wiki](https://github.com/AsamK/signal-cli/wiki)
- [signal-cli REST API Docker](https://github.com/bbernhard/signal-cli-rest-api)
- [OpenClaw Dokumentacja](https://openclaw.dev)
