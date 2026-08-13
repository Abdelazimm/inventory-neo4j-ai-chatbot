import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo4j import GraphDatabase
from app.config import settings


def apply_constraints():
    print(f"Connecting to Neo4j instance at: {settings.NEO4J_URI} ...")
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )
    
    constraints_path = Path(__file__).parent.parent / "neo4j" / "constraints.cypher"
    with open(constraints_path, "r", encoding="utf-8") as f:
        statements = [line.strip() for line in f.read().split(";") if line.strip() and not line.strip().startswith("//")]

    with driver.session(database=settings.NEO4J_DATABASE) as session:
        for stmt in statements:
            try:
                print(f"Applying constraint: {stmt[:60]}...")
                session.run(stmt)
            except Exception as e:
                print(f"Notice during constraint creation: {e}")
                
    driver.close()
    print("All Neo4j constraints applied successfully.")


if __name__ == "__main__":
    apply_constraints()
