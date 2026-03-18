#!/usr/bin/env python3
"""
neo4j_add.py - Add facts, lessons, and events to Neo4j Aura.

Allows the AI assistant to persist information to the graph database
for long-term memory across sessions.

Usage:
    python -X utf8 neo4j_add.py fact "User prefers dark mode" --importance high
    python -X utf8 neo4j_add.py lesson "Always check the config before running" --category tooling
    python -X utf8 neo4j_add.py stats
    python -X utf8 neo4j_add.py search "dark mode"

Requirements:
    pip install neo4j
"""

import sys
import os
import argparse
from datetime import datetime, timezone

# ============================================================
# CONFIGURATION — Fill in your credentials here
# Or better: use environment variables
# ============================================================

NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j+s://YOUR_INSTANCE_ID.databases.neo4j.io")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "YOUR_PASSWORD_HERE")

# ============================================================


def get_driver():
    """Create and return Neo4j driver."""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        return driver
    except ImportError:
        print("ERROR: neo4j library not installed. Run: pip install neo4j", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot connect to Neo4j: {e}", file=sys.stderr)
        sys.exit(1)


def now_iso():
    """Return current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def add_fact(session, content, importance="normal", person=None, topics=None):
    """
    Add a fact to the graph.
    
    Args:
        content: The fact text
        importance: low / normal / high / critical
        person: Optional person this fact is about (name)
        topics: Optional list of topic tags
    """
    # Create the Fact node
    result = session.run("""
        CREATE (f:Fact {
            content: $content,
            importance: $importance,
            createdAt: $createdAt,
            id: randomUUID()
        })
        RETURN f.id AS id
    """, content=content, importance=importance, createdAt=now_iso())
    
    fact_id = result.single()["id"]
    
    # Link to Person if provided
    if person:
        session.run("""
            MERGE (p:Person {name: $name})
            WITH p
            MATCH (f:Fact {id: $fact_id})
            CREATE (f)-[:ABOUT]->(p)
        """, name=person, fact_id=fact_id)
    
    # Link to Topics if provided
    if topics:
        for topic in topics:
            session.run("""
                MERGE (t:Topic {name: $name})
                WITH t
                MATCH (f:Fact {id: $fact_id})
                MERGE (f)-[:TAGGED]->(t)
            """, name=topic.strip(), fact_id=fact_id)
    
    return fact_id


def add_lesson(session, content, category=None):
    """
    Add a lesson learned to the graph.
    
    Args:
        content: The lesson text
        category: Optional category (e.g., tooling, communication, workflow)
    """
    result = session.run("""
        CREATE (l:Lesson {
            content: $content,
            category: $category,
            createdAt: $createdAt,
            id: randomUUID()
        })
        RETURN l.id AS id
    """, content=content, category=category or "", createdAt=now_iso())
    
    return result.single()["id"]


def add_event(session, title, description=None, date=None, people=None):
    """
    Add an event to the graph.
    
    Args:
        title: Event title
        description: Optional longer description
        date: Optional ISO date (defaults to now)
        people: Optional list of person names involved
    """
    event_date = date or now_iso()
    
    result = session.run("""
        CREATE (e:Event {
            title: $title,
            description: $description,
            date: $date,
            createdAt: $createdAt,
            id: randomUUID()
        })
        RETURN e.id AS id
    """, title=title, description=description or "", date=event_date, createdAt=now_iso())
    
    event_id = result.single()["id"]
    
    # Link to People if provided
    if people:
        for person in people:
            session.run("""
                MERGE (p:Person {name: $name})
                WITH p
                MATCH (e:Event {id: $event_id})
                MERGE (e)-[:INVOLVES]->(p)
            """, name=person.strip(), event_id=event_id)
    
    return event_id


def get_stats(session):
    """Get basic statistics about the graph."""
    result = session.run("""
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
    """)
    return result.data()


def search_facts(session, query, limit=10):
    """Search facts by content (case-insensitive)."""
    result = session.run("""
        MATCH (f:Fact)
        WHERE toLower(f.content) CONTAINS toLower($query)
        OPTIONAL MATCH (f)-[:ABOUT]->(p:Person)
        RETURN f.content AS content,
               f.importance AS importance,
               f.createdAt AS createdAt,
               p.name AS person
        ORDER BY f.createdAt DESC
        LIMIT $limit
    """, query=query, limit=limit)
    return result.data()


def main():
    parser = argparse.ArgumentParser(
        description="Add information to Neo4j graph database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python neo4j_add.py fact "User prefers concise responses"
  python neo4j_add.py fact "User is working on Project X" --importance high --person "User Name"
  python neo4j_add.py fact "Signal groups have base64 encoding quirk" --topics tooling signal
  python neo4j_add.py lesson "Always read HEARTBEAT.md before doing proactive work" --category workflow
  python neo4j_add.py event "Had great conversation about AI" --people "Alice" "Bob"
  python neo4j_add.py stats
  python neo4j_add.py search "project X"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # fact command
    fact_parser = subparsers.add_parser("fact", help="Add a fact")
    fact_parser.add_argument("content", help="The fact text")
    fact_parser.add_argument("--importance", choices=["low", "normal", "high", "critical"],
                             default="normal", help="Importance level")
    fact_parser.add_argument("--person", help="Person this fact is about")
    fact_parser.add_argument("--topics", nargs="+", help="Topic tags")
    
    # lesson command
    lesson_parser = subparsers.add_parser("lesson", help="Add a lesson learned")
    lesson_parser.add_argument("content", help="The lesson text")
    lesson_parser.add_argument("--category", help="Category (e.g., tooling, communication)")
    
    # event command
    event_parser = subparsers.add_parser("event", help="Add an event")
    event_parser.add_argument("title", help="Event title")
    event_parser.add_argument("--description", help="Longer description")
    event_parser.add_argument("--date", help="ISO date (defaults to now)")
    event_parser.add_argument("--people", nargs="+", help="People involved")
    
    # stats command
    subparsers.add_parser("stats", help="Show graph statistics")
    
    # search command
    search_parser = subparsers.add_parser("search", help="Search facts by content")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    driver = get_driver()
    
    try:
        with driver.session() as session:
            
            if args.command == "fact":
                fact_id = add_fact(
                    session, args.content,
                    importance=args.importance,
                    person=args.person,
                    topics=args.topics
                )
                print(f"✅ Fact added (id: {fact_id[:8]}...)")
                print(f"   Content: {args.content}")
                print(f"   Importance: {args.importance}")
                if args.person:
                    print(f"   About: {args.person}")
                if args.topics:
                    print(f"   Topics: {', '.join(args.topics)}")
            
            elif args.command == "lesson":
                lesson_id = add_lesson(session, args.content, category=args.category)
                print(f"✅ Lesson added (id: {lesson_id[:8]}...)")
                print(f"   Content: {args.content}")
                if args.category:
                    print(f"   Category: {args.category}")
            
            elif args.command == "event":
                event_id = add_event(
                    session, args.title,
                    description=args.description,
                    date=args.date,
                    people=args.people
                )
                print(f"✅ Event added (id: {event_id[:8]}...)")
                print(f"   Title: {args.title}")
                if args.people:
                    print(f"   People: {', '.join(args.people)}")
            
            elif args.command == "stats":
                stats = get_stats(session)
                print("\n📊 Graph Statistics:")
                total = 0
                for s in stats:
                    if s["label"]:
                        print(f"  {s['label']:20} {s['count']:5} nodes")
                        total += s["count"]
                print(f"  {'TOTAL':20} {total:5} nodes")
            
            elif args.command == "search":
                results = search_facts(session, args.query, limit=args.limit)
                if results:
                    print(f"\n🔍 Found {len(results)} result(s) for '{args.query}':")
                    for r in results:
                        date = str(r.get("createdAt", ""))[:10]
                        importance = r.get("importance", "")
                        content = r.get("content", "")
                        person = r.get("person", "")
                        imp_str = f"[{importance.upper()}] " if importance != "normal" else ""
                        person_str = f" (re: {person})" if person else ""
                        print(f"  [{date}] {imp_str}{content}{person_str}")
                else:
                    print(f"No results found for '{args.query}'")
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
