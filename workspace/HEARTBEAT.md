# HEARTBEAT.md - Proaktywne Sprawdzenia

<!--
INSTRUKCJA:
Ten plik to checklist dla asystenta podczas heartbeatów.
Heartbeat to periodyczny "puls" — OpenClaw wysyła wiadomość do asystenta
co jakiś czas (np. co 30 minut) i asystent wykonuje tę checklistę.

Jeśli nic ważnego się nie dzieje → odpowiedz HEARTBEAT_OK
Jeśli coś wymaga uwagi → wyślij wiadomość do użytkownika

ZASADA: Nie spamuj! Tylko pisz gdy masz coś wartego powiedzenia.
Ciche heartbeaty (HEARTBEAT_OK) są w porządku i wskazane.

Dostosuj tę listę do swoich potrzeb — usuń/dodaj sekcje.
-->

---

## Zasady Heartbeatu

**Gdy pisać do użytkownika:**
- Ważny email przyszedł
- Nadchodzące spotkanie (< 2h)
- Coś ciekawego/pilnego znalazłeś
- Minęło > 8h od ostatniej rozmowy i masz coś wartego powiedzenia

**Gdy milczeć (HEARTBEAT_OK):**
- Późna noc (23:00-08:00) chyba że pilne
- Użytkownik jest wyraźnie zajęty
- Nic nowego od ostatniego sprawdzenia
- Sprawdzałeś < 30 minut temu

---

## Checklist

### 📧 Email (jeśli Gmail skonfigurowany)
<!-- Odkomentuj i dostosuj gdy Gmail jest skonfigurowany -->
<!--
Sprawdź nieprzeczytane emaile:
```python
python /ścieżka/do/check_gmail.py
```
- Szukaj: pilne emaile, od ważnych nadawców
- Ignoruj: newsletter, promocje, automated notifications
- Próg alertu: emaile od konkretnych osób lub z słowem "urgent/pilne/ASAP"
-->

### 📅 Kalendarz (jeśli Google Calendar skonfigurowany)  
<!-- Odkomentuj gdy Calendar jest skonfigurowany -->
<!--
Sprawdź nadchodzące wydarzenia:
```python
python /ścieżka/do/check_calendar.py
```
- Alertuj na: spotkania w ciągu 2h, zmiany w agendzie
- Ignoruj: całodniowe eventy chyba że coś ważnego
-->

### 🤖 Newsy AI (1-2x dziennie)
<!--
Szybkie sprawdzenie co nowego w świecie AI:
- Brave Search: "AI news today site:techcrunch.com OR site:theverge.com"
- Lub RSS z ulubionych blogów
- Wyślij do użytkownika jeśli coś naprawdę ciekawego
- Nie spamuj codziennie — tylko przy prawdziwych przełomach
-->

### 🦋 Bluesky/Social (jeśli skonfigurowane)
<!-- Odkomentuj gdy social media są skonfigurowane -->
<!--
Sprawdź powiadomienia, odpowiedz na mentions:
```python
python /ścieżka/do/check_bsky.py
```
-->

### 🧠 Utrzymanie Pamięci (co kilka dni)
<!--
Periodycznie (nie przy każdym heartbeat!):
1. Przejrzyj ostatnie memory/YYYY-MM-DD.md
2. Zidentyfikuj co warto przenieść do MEMORY.md
3. Zaktualizuj MEMORY.md
4. Wyczyść przestarzałe wpisy
-->

---

## Stan Sprawdzeń

<!--
UWAGA (Windows): curl może mieć problemy z JSON na Windows PowerShell.
Zamiast curl użyj Invoke-WebRequest lub skryptów Python.

Przykład PowerShell:
$headers = @{"Content-Type"="application/json"}
$body = '{"query": "AI news"}'
Invoke-WebRequest -Uri "https://api.example.com" -Method POST -Headers $headers -Body $body
-->

Asystent może śledzić ostatnie sprawdzenia w pliku:
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
  "notes": "Tutaj asystent może zostawić notatki między heartbeatami"
}
```

---

*Edytuj ten plik gdy chcesz zmienić co asystent sprawdza proaktywnie.*
