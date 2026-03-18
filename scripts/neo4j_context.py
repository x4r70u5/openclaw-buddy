#!/usr/bin/env python3
"""
neo4j_context.py - Load context from Neo4j Aura graph database.

Connects to Neo4j Aura and fetches recent facts, lessons, and events
to provide the AI assistant with condensed long-term context.

Usage:
    python -X utf8 neo4j_context.py
    python -X utf8 neo4j_context.py --limit 20
    python -X utf8 neo4j_context.py --verbose

Requirements:
    pip install neo4j
"""

import sys
import argparse
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION — Fill in your credentials here
# Or better: use environment variables (see below)
# ============================================================

import os

# Option 1: Hardcode credentials (NOT recommended for shared repos!)
# NEO4J_URI = "neo4j+s://YOUR_INSTANCE_ID.databases.neo4j.io"
# NEO4J_USER = "neo4j"
# NEO4J_PASSWORD = "YOUR_PASSWORD_HERE"

# Option 2: Environment variables (recommended)
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j+s://YOUR_INSTANCE_ID.databases.neo4j.io")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "YOUR_PASSWORD_HERE")

# How many items to fetch
DEFAULT_LIMIT = 15
# How many days back to look for recent items
RECENT_DAYS = 30

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


def fetch_recent_facts(session, limit=DEFAULT_LIMIT):
    """Fetch recent facts from the graph."""
    result = session.run("""
        MATCH (f:Fact)
        OPTIONAL MATCH (f)-[:ABOUT]->(p:Person)
        OPTIONAL MATCH (f)-[:TAGGED]->(t:Topic)
        RETURN f.content AS content,
               f.createdAt AS createdAt,
               f.importance AS importance,
               p.name AS person,
               collect(DISTINCT t.name) AS topics
        ORDER BY f.createdAt DESC
        LIMIT $limit
    """, limit=limit)
    return result.data()


def fetch_recent_lessons(session, limit=10):
    """Fetch lessons learned from the graph."""
    result = session.run("""
        MATCH (l:Lesson)
        RETURN l.content AS content,
               l.createdAt AS createdAt,
               l.category AS category
        ORDER BY l.createdAt DESC
        LIMIT $limit
    """, limit=limit)
    return result.data()


def fetch_recent_events(session, days=RECENT_DAYS):
    """Fetch recent events from the graph."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    result = session.run("""
        MATCH (e:Event)
        WHERE e.date >= $cutoff
        OPTIONAL MATCH (e)-[:INVOLVES]->(p:Person)
        RETURN e.title AS title,
               e.description AS description,
               e.date AS date,
               collect(DISTINCT p.name) AS people
        ORDER BY e.date DESC
        LIMIT 10
    """, cutoff=cutoff)
    return result.data()


def fetch_stats(session):
    """Fetch basic stats about the graph."""
    result = session.run("""
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
    """)
    return result.data()


def format_date(iso_date):
    """Format ISO date to readable string."""
    if not iso_date:
        return "?"
    try:
        dt = datetime.fromisoformat(str(iso_date).replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(iso_date)[:10]


def print_context(facts, lessons, events, verbose=False):
    """Print condensed context for the AI assistant."""
    print("=" * 60)
    print("📊 NEO4J CONTEXT SUMMARY")
    print("=" * 60)

    # Recent facts
    if facts:
        print(f"\n📌 RECENT FACTS ({len(facts)}):")
        for f in facts:
            date = format_date(f.get("createdAt"))
            content = f.get("content", "")
            person = f.get("person", "")
            topics = ", ".join(f.get("topics", []) or [])
            importance = f.get("importance", "")

            line = f"  [{date}]"
            if importance:
                line += f" [{importance.upper()}]"
            line += f" {content}"
            if person:
                line += f" (re: {person})"
            if topics and verbose:
                line += f" #{topics}"
            print(line)
    else:
        print("\n📌 RECENT FACTS: (none)")

    # Lessons learned
    if lessons:
        print(f"\n🎓 LESSONS LEARNED ({len(lessons)}):")
        for l in lessons:
            date = format_date(l.get("createdAt"))
            content = l.get("content", "")
            category = l.get("category", "")
            cat_str = f"[{category}] " if category else ""
            print(f"  [{date}] {cat_str}{content}")
    else:
        print("\n🎓 LESSONS LEARNED: (none)")

    # Recent events
    if events:
        print(f"\n📅 RECENT EVENTS ({len(events)}):")
        for e in events:
            date = format_date(e.get("date"))
            title = e.get("title", "")
            desc = e.get("description", "")
            people = ", ".join(e.get("people", []) or [])

            line = f"  [{date}] {title}"
            if people:
                line += f" ({people})"
            if desc and verbose:
                line += f"\n        {desc}"
            print(line)
    else:
        print("\n📅 RECENT EVENTS: (none)")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Load Neo4j context for AI assistant")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Max facts to fetch")
    parser.add_argument("--verbose", action="store_true", help="Show more details")
    parser.add_argument("--stats", action="store_true", help="Show graph stats only")
    args = parser.parse_args()

    driver = get_driver()

    try:
        with driver.session() as session:
            if args.stats:
                stats = fetch_stats(session)
                print("\n📊 Graph Statistics:")
                for s in stats:
                    print(f"  {s['label']}: {s['count']} nodes")
                return

            facts = fetch_recent_facts(session, args.limit)
            lessons = fetch_recent_lessons(session)
            events = fetch_recent_events(session)

            print_context(facts, lessons, events, verbose=args.verbose)

    except Exception as e:
        print(f"ERROR fetching context: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
