import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo4j import GraphDatabase
from app.config import settings


def seed_knowledge_graph():
    print(f"Connecting to Neo4j instance at: {settings.NEO4J_URI} (Database: {settings.NEO4J_DATABASE}) ...")
    try:
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        return

    seed_path = Path(__file__).parent.parent / "neo4j" / "seed.cypher"
    with open(seed_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into separate statements while ignoring comments
    raw_statements = content.split(";")
    statements = []
    for stmt in raw_statements:
        clean = "\n".join([line for line in stmt.splitlines() if not line.strip().startswith("//")]).strip()
        if clean:
            statements.append(clean)

    print(f"Executing {len(statements)} seed statements against Neo4j...")
    with driver.session(database=settings.NEO4J_DATABASE) as session:
        for idx, stmt in enumerate(statements, 1):
            try:
                session.run(stmt)
            except Exception as e:
                print(f"Error executing statement #{idx}: {e}\nStatement: {stmt}")
                raise

    driver.close()
    print("=" * 60)
    print("  INVENTORY KNOWLEDGE GRAPH SEED COMPLETED SUCCESSFULLY!")
    print("  Created Nodes: Asset, Item, Vendor, Location, Site, Customer, PurchaseOrder, SalesOrder, Category")
    print("  Created Relationships: SUPPLIES, PURCHASED_FROM, LOCATED_AT, BELONGS_TO, INSTANCE_OF, IN_CATEGORY, CONTAINS, PLACED, RECEIVED")
    print("=" * 60)


if __name__ == "__main__":
    seed_knowledge_graph()
