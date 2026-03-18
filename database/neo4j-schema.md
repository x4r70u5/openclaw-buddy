# Neo4j Graph Schema

Schemat grafu wiedzy dla AI asystenta. Używaj tego jako referencji przy pisaniu zapytań Cypher.

---

## Typy Węzłów (Node Labels)

### `Fact`
Fakty i informacje zebrane przez asystenta.

| Właściwość | Typ | Opis |
|-----------|-----|------|
| `id` | String | UUID (generowany przez `randomUUID()`) |
| `content` | String | Treść faktu |
| `importance` | String | `low`, `normal`, `high`, `critical` |
| `createdAt` | String | ISO 8601 timestamp |
| `source` | String | Skąd pochodzi fakt (opcjonalne) |

### `Lesson`
Wnioski i lekcje wyciągnięte przez asystenta.

| Właściwość | Typ | Opis |
|-----------|-----|------|
| `id` | String | UUID |
| `content` | String | Treść lekcji |
| `category` | String | np. `tooling`, `communication`, `workflow` |
| `createdAt` | String | ISO 8601 timestamp |

### `Person`
Osoby wspomniane lub powiązane z faktami.

| Właściwość | Typ | Opis |
|-----------|-----|------|
| `name` | String | Imię lub pseudonim |
| `phone` | String | Numer telefonu (opcjonalne) |
| `relationship` | String | np. `owner`, `friend`, `colleague` |
| `createdAt` | String | ISO 8601 timestamp |

### `Event`
Zdarzenia i spotkania.

| Właściwość | Typ | Opis |
|-----------|-----|------|
| `id` | String | UUID |
| `title` | String | Tytuł zdarzenia |
| `description` | String | Dłuższy opis (opcjonalne) |
| `date` | String | ISO 8601 data zdarzenia |
| `createdAt` | String | Kiedy dodano do grafu |

### `Topic`
Tematy i tagi do kategoryzacji.

| Właściwość | Typ | Opis |
|-----------|-----|------|
| `name` | String | Nazwa tematu (unikalna) |
| `description` | String | Opis tematu (opcjonalne) |

---

## Relacje (Relationships)

| Relacja | Od → Do | Opis |
|---------|---------|------|
| `ABOUT` | Fact → Person | Fakt dotyczy tej osoby |
| `TAGGED` | Fact → Topic | Fakt jest otagowany tym tematem |
| `INVOLVES` | Event → Person | Zdarzenie dotyczy tej osoby |
| `KNOWS` | Person → Person | Osoby się znają |
| `RELATED_TO` | Fact → Fact | Fakty są ze sobą powiązane |
| `TRIGGERED` | Event → Lesson | Zdarzenie doprowadziło do tej lekcji |

---

## Przykładowe Zapytania Cypher

### Dodaj fakt

```cypher
CREATE (f:Fact {
    id: randomUUID(),
    content: "User prefers dark mode",
    importance: "normal",
    createdAt: datetime().epochMillis
})
```

### Dodaj fakt z powiązaniem do osoby

```cypher
MERGE (p:Person {name: "Alice"})
CREATE (f:Fact {
    id: randomUUID(),
    content: "Alice is a senior developer",
    importance: "high",
    createdAt: datetime().epochMillis
})
CREATE (f)-[:ABOUT]->(p)
```

### Pobierz ostatnie fakty (kontekst)

```cypher
MATCH (f:Fact)
OPTIONAL MATCH (f)-[:ABOUT]->(p:Person)
OPTIONAL MATCH (f)-[:TAGGED]->(t:Topic)
RETURN f.content, f.importance, p.name AS about,
       collect(DISTINCT t.name) AS topics
ORDER BY f.createdAt DESC
LIMIT 15
```

### Szukaj faktów po treści

```cypher
MATCH (f:Fact)
WHERE toLower(f.content) CONTAINS toLower("dark mode")
RETURN f.content, f.importance, f.createdAt
ORDER BY f.createdAt DESC
LIMIT 10
```

### Pobierz wszystko o konkretnej osobie

```cypher
MATCH (p:Person {name: "Alice"})
OPTIONAL MATCH (f:Fact)-[:ABOUT]->(p)
OPTIONAL MATCH (e:Event)-[:INVOLVES]->(p)
RETURN p, collect(DISTINCT f) AS facts, collect(DISTINCT e) AS events
```

### Lekcje z ostatnich 30 dni

```cypher
MATCH (l:Lesson)
WHERE l.createdAt >= datetime() - duration('P30D')
RETURN l.content, l.category, l.createdAt
ORDER BY l.createdAt DESC
```

### Statystyki grafu

```cypher
MATCH (n)
RETURN labels(n)[0] AS label, count(n) AS count
ORDER BY count DESC
```

### Powiązane fakty (znajdź powiązania przez tematy)

```cypher
MATCH (f1:Fact)-[:TAGGED]->(t:Topic)<-[:TAGGED]-(f2:Fact)
WHERE f1 <> f2
RETURN f1.content, t.name, f2.content
LIMIT 20
```

---

## Indeksy (zalecane)

Uruchom te zapytania w Neo4j Browser po stworzeniu instancji:

```cypher
-- Unikalny index na Person.name
CREATE CONSTRAINT person_name_unique IF NOT EXISTS
    FOR (p:Person) REQUIRE p.name IS UNIQUE;

-- Unikalny index na Topic.name
CREATE CONSTRAINT topic_name_unique IF NOT EXISTS
    FOR (t:Topic) REQUIRE t.name IS UNIQUE;

-- Index na dacie dla faktów i lekcji
CREATE INDEX fact_created_at IF NOT EXISTS FOR (f:Fact) ON (f.createdAt);
CREATE INDEX lesson_created_at IF NOT EXISTS FOR (l:Lesson) ON (l.createdAt);
CREATE INDEX event_date IF NOT EXISTS FOR (e:Event) ON (e.date);

-- Index na ważności faktów
CREATE INDEX fact_importance IF NOT EXISTS FOR (f:Fact) ON (f.importance);
```

---

## Tips

- **Merge vs Create**: Użyj `MERGE` dla węzłów które powinny być unikalne (Person, Topic), `CREATE` dla faktów i zdarzeń
- **UUID**: Zawsze generuj `randomUUID()` dla ID faktów/lekcji/eventów
- **Timestamps**: Przechowuj jako ISO string (`datetime().epochMillis` lub Python `datetime.now().isoformat()`)
- **Backup**: Neo4j Aura automatycznie robi backup, ale możesz też eksportować przez APOC
