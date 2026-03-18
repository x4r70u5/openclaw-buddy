# 🤖 OpenClaw Buddy - Szablon AI Asystenta dla Signal

> Kompletny szablon do zbudowania własnego AI asystenta działającego przez Signal - na bazie OpenClaw + signal-cli.

---

## 💡 Co to jest?

**OpenClaw Buddy** to gotowy szkielet do stworzenia personalnego asystenta AI dostępnego przez Signal Messenger. Asystent:

- **Odpowiada na wiadomości Signal** - prywatne i grupowe
- **Pamięta kontekst** - przez pliki Markdown i opcjonalnie Neo4j (baza grafowa)
- **Działa proaktywnie** - sprawdza email, kalendarz, powiadomienia (heartbeat)
- **Ma osobowość** - konfigurowalną przez `SOUL.md`
- **Uczy się** - aktualizuje własne pliki, wyciąga wnioski z błędów

Przykład tego co możesz zbudować: asystent-kumpel który pisze do Ciebie przez Signal, pamięta Twoje preferencje, komentuje wiadomości ze świata AI i wysyła Ci powiadomienia gdy coś ważnego się dzieje.

---

## 📋 Wymagania

### Obowiązkowe

| Narzędzie | Wersja | Opis |
|-----------|--------|------|
| [OpenClaw](https://openclaw.dev) | latest | Główny runtime dla agenta AI |
| [signal-cli](https://github.com/AsamK/signal-cli) | 0.13+ | CLI klient Signal z trybem daemon HTTP |
| Java | 21+ | Wymagane przez signal-cli |
| Node.js | 18+ | Wymagane przez OpenClaw |
| Python | 3.10+ | Skrypty pomocnicze |

### Opcjonalne

| Narzędzie | Opis |
|-----------|------|
| [Neo4j Aura](https://neo4j.com/cloud/aura/) | Baza grafowa dla długoterminowej pamięci (free tier dostępny) |
| [atproto](https://pypi.org/project/atproto/) | Biblioteka Bluesky do postowania |
| Gmail OAuth | Dostęp do emaila przez API |

---

## 🚀 Instalacja krok po kroku

### Krok 1: Sklonuj ten szablon

```bash
git clone https://github.com/TWOJ_USERNAME/openclaw-buddy.git moj-asystent
cd moj-asystent
```

### Krok 2: Zainstaluj OpenClaw

```bash
npm install -g openclaw
openclaw --version
```

Szczegóły: [setup/openclaw-setup.md](setup/openclaw-setup.md)

### Krok 3: Skonfiguruj signal-cli

Pobierz, zainstaluj i uruchom signal-cli jako daemon HTTP na porcie 8080.

Szczegóły: [setup/signal-cli-setup.md](setup/signal-cli-setup.md)

### Krok 4: Skopiuj workspace do katalogu OpenClaw

```bash
# Znajdź katalog workspace OpenClaw (zwykle ~/clawd)
cp workspace/* ~/clawd/
```

### Krok 5: Dostosuj pliki konfiguracyjne

Edytuj w kolejności:

1. **`workspace/IDENTITY.md`** - nadaj asystentowi imię i osobowość
2. **`workspace/SOUL.md`** - zdefiniuj charakter i zasady działania
3. **`workspace/USER.md`** - opisz siebie (asystent będzie to czytał)
4. **`workspace/TOOLS.md`** - skonfiguruj grupy Signal i inne narzędzia
5. **`workspace/HEARTBEAT.md`** - ustaw co asystent ma sprawdzać proaktywnie
6. **`workspace/AGENTS.md`** - instrukcje dla agenta (możesz zostawić domyślne)

### Krok 6: (Opcjonalnie) Skonfiguruj Neo4j

```bash
# Zainstaluj bibliotekę
pip install neo4j

# Edytuj credentials w skryptach
nano scripts/neo4j_context.py
nano scripts/neo4j_add.py
```

### Krok 7: Uruchom!

```bash
# Upewnij się że signal-cli daemon działa
curl -X POST http://localhost:8080/api/v1/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"version","id":1}'

# Uruchom OpenClaw
openclaw start
```

---

## ⚙️ Konfiguracja modelu AI

OpenClaw wspiera wiele providerów:

```bash
# Anthropic Claude (rekomendowany)
openclaw config set model anthropic/claude-opus-4

# OpenAI GPT-4
openclaw config set model openai/gpt-4o

# OpenRouter (dostęp do wielu modeli)
openclaw config set model openrouter/anthropic/claude-sonnet-4
```

---

## 🎭 Personalizacja - Jak sprawić żeby to "żyło"

### 1. Nadaj imię i charakter

W `IDENTITY.md` i `SOUL.md` opisz kto jest Twój asystent. Nie rób kolejnego "pomocnego AI" - nadaj mu konkretną osobowość:
- Jakim językiem mówi? (formalny / luźny / śmieszny)
- Co go interesuje?
- Jakie ma "opinie"?
- Jak reaguje na różne sytuacje?

### 2. Opisz siebie

`USER.md` to profil Ciebie - asystent czyta go przy każdej sesji. Im więcej tam napiszesz, tym lepiej Cię "zna":
- Twoja praca, projekty, zainteresowania
- Jak lubisz być traktowany
- Czego NIE lubisz (ważne!)
- Ważne daty, osoby w Twoim życiu

### 3. Skonfiguruj heartbeat

`HEARTBEAT.md` to checklist który asystent wykonuje proaktywnie. Możesz ustawić by:
- Sprawdzał Twój email co kilka godzin
- Informował o nadchodzących spotkaniach
- Wyszukiwał ciekawe newsy z AI
- Pisał do Ciebie jeśli minęło dużo czasu

### 4. Pamięć długoterminowa

- **`MEMORY.md`** - asystent zapisuje tu ważne informacje między sesjami
- **Neo4j** (opcjonalne) - baza grafowa dla bardziej strukturalnej pamięci
- **`memory/YYYY-MM-DD.md`** - dzienne logi co się działo

### 5. Wskazówki

- ✅ Pisz do asystenta naturalnie - odpiszę w podobnym tonie
- ✅ Poprawiaj go gdy coś zrobi nie tak - uczy się
- ✅ Daj mu dostęp do narzędzi które lubisz (Bluesky, Gmail, etc.)
- ⚠️ Nie dawaj mu dostępu do kont które nie mogą "wysyłać dziwnych rzeczy"
- ⏳ Nie spodziewaj się perfekcji od razu - potrzeba kilku dni kalibracji

---

## 🗂️ Struktura projektu

```
openclaw-buddy/
├── README.md                    # Ten plik
├── workspace/                   # Pliki do skopiowania do ~/clawd/
│   ├── AGENTS.md               # Instrukcje dla agenta
│   ├── SOUL.md                 # Osobowość asystenta
│   ├── USER.md                 # Profil użytkownika
│   ├── MEMORY.md               # Długoterminowa pamięć
│   ├── TOOLS.md                # Konfiguracja narzędzi
│   ├── HEARTBEAT.md            # Proaktywne sprawdzenia
│   └── IDENTITY.md             # Tożsamość asystenta
├── scripts/                     # Skrypty pomocnicze Python
│   ├── neo4j_context.py        # Ładowanie kontekstu z Neo4j
│   └── neo4j_add.py            # Dodawanie faktów do Neo4j
├── database/                    # Schematy bazy danych
│   ├── schema.sql              # SQLite schema
│   └── neo4j-schema.md         # Neo4j schema i Cypher queries
├── setup/                       # Przewodniki instalacji
│   ├── signal-cli-setup.md     # Konfiguracja signal-cli
│   └── openclaw-setup.md       # Konfiguracja OpenClaw
└── examples/                    # Przykładowe skrypty
    ├── send_message.py         # Wysyłanie wiadomości Signal
    └── bsky_post.py            # Postowanie na Bluesky
```

---

## 🔧 Troubleshooting / FAQ

### signal-cli nie startuje

```bash
# Sprawdź czy Java 21+ jest zainstalowana
java -version

# Sprawdź czy port 8080 nie jest zajęty
netstat -an | grep 8080

# Uruchom z logami
signal-cli --verbose daemon --http 127.0.0.1:8080
```

### OpenClaw nie widzi Signala

Upewnij się że w konfiguracji OpenClaw masz ustawiony poprawny adres daemona:
```bash
# Sprawdź konfigurację
openclaw config show

# Signal-cli powinien działać pod
http://127.0.0.1:8080
```

### Asystent nie odpowiada na wiadomości

1. Sprawdź czy OpenClaw jest uruchomiony (`openclaw status`)
2. Sprawdź czy signal-cli daemon działa i odbiera wiadomości
3. Sprawdź logi OpenClaw w poszukiwaniu błędów
4. Wyślij testową wiadomość i sprawdź logi w czasie rzeczywistym

### Broken encoding / krzaczki w plikach (Windows)

Na Windows używaj zawsze:
```powershell
# Zamiast Invoke-RestMethod, używaj curl.exe
C:\Windows\System32\curl.exe -X POST ...

# Dla Python z emoji/polskimi znakami
python -X utf8 twój_skrypt.py
```

### Asystent "zapomina" między sesjami

To normalne — LLM nie ma stanu między sesjami. Dlatego istnieje system plików:
- Upewnij się że `AGENTS.md` nakazuje czytanie `memory/YYYY-MM-DD.md` na starcie
- Upewnij się że asystent zapisuje ważne rzeczy do plików podczas sesji
- Rozważ Neo4j dla strukturalnej pamięci długoterminowej

### Asystent odpowiada w złym języku lub tonie

Edytuj `SOUL.md` i `USER.md` — są to najważniejsze pliki wpływające na styl komunikacji. Bądź konkretny: zamiast "mów naturalnie" napisz dokładnie co Ci przeszkadza i jak chcesz żeby mówił.

### Zbyt wiele powiadomień / za mało powiadomień

Dostosuj `HEARTBEAT.md` — możesz zmienić częstotliwość sprawdzeń, dodać lub usunąć zadania. Pamiętaj: każdy heartbeat to call do API (koszt tokenów).

---

## 🔐 Bezpieczeństwo

- **Nigdy nie commituj** plików z prawdziwymi kluczami API, tokenami, ani numerami telefonów
- `.gitignore` w tym repozytorium wyklucza `TOOLS.md` i `*.pickle` - dodaj swoje sekrety tam
- signal-cli daemon domyślnie nasłuchuje tylko na `localhost` - nie wystawiaj go na zewnątrz
- Asystent ma dostęp do Twoich plików i wiadomości - traktuj to jak zaufany program

---

## 🤝 Kontrybucja

Pull requesty mile widziane! Szczególnie:
- Przykłady nowych narzędzi (Slack, Teams, Telegram)
- Szablony SOUL.md dla różnych osobowości
- Skrypty do nowych źródeł danych
- Poprawki dokumentacji

---

## 📄 Licencja

MIT - rób co chcesz, ale nie obwiniaj mnie jeśli Twój asystent postanowi wysłać dziwne wiadomości do Twoich znajomych. 😄

---

*Zbudowany z ❤️ i dużą ilością eksperymentów.*
