import logging
from typing import Dict, Any, List
from app.database.neo4j_connection import get_neo4j_driver
from app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_INVENTORY_SCHEMA = """
Node Labels & Properties:
- :Asset {asset_tag, name, cost, status, serial_number, purchase_date}
- :Item {item_code, name, unit_of_measure}
- :Category {name}
- :Vendor {vendor_code, name, email, phone, city, country}
- :Site {site_code, name, city, country, timezone}
- :Location {location_code, name}
- :Customer {customer_code, name, email, city}
- :PurchaseOrder {po_number, order_date, status, total_amount}
- :SalesOrder {so_number, order_date, status, total_amount}

Relationships (Directional Triples):
- (:Vendor)-[:SUPPLIES]->(:Item)
- (:Asset)-[:INSTANCE_OF]->(:Item)
- (:Asset)-[:PURCHASED_FROM]->(:Vendor)
- (:Asset)-[:LOCATED_AT]->(:Location)
- (:Location)-[:BELONGS_TO]->(:Site)
- (:Item)-[:IN_CATEGORY]->(:Category)
- (:Vendor)-[:RECEIVED]->(:PurchaseOrder)
- (:PurchaseOrder)-[:CONTAINS {quantity, unit_price}]->(:Item)
- (:Customer)-[:PLACED]->(:SalesOrder)
- (:SalesOrder)-[:CONTAINS {quantity, unit_price}]->(:Item)
"""


def get_dynamic_neo4j_schema() -> str:
    """
    Introspects the live Neo4j database schema dynamically.
    Fetches node labels, relationship types, and schema relationships.
    Falls back to canonical inventory schema if database is unreachable.
    """
    try:
        driver = get_neo4j_driver()
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            # Fetch node labels
            labels_res = session.run("CALL db.labels()")
            labels = [r["label"] for r in labels_res]
            
            # Fetch relationship types
            rel_res = session.run("CALL db.relationshipTypes()")
            rels = [r["relationshipType"] for r in rel_res]
            
            # Fetch relationship patterns
            schema_res = session.run("""
                MATCH (a)-[r]->(b)
                RETURN DISTINCT labels(a)[0] AS source, type(r) AS relationship, labels(b)[0] AS target
                LIMIT 50
            """)
            patterns = [f"(:{r['source']})-[:{r['relationship']}]->(:{r['target']})" for r in schema_res if r['source'] and r['target']]
            
            if labels and rels:
                parts = [
                    f"Node Labels: {', '.join(labels)}",
                    f"Relationship Types: {', '.join(rels)}",
                    "Observed Graph Patterns:",
                    "\n".join(f"- {p}" for p in patterns) if patterns else "- (See canonical relationships)",
                    "\nCanonical Schema & Properties:",
                    DEFAULT_INVENTORY_SCHEMA
                ]
                return "\n\n".join(parts)
    except Exception as e:
        logger.warning(f"Could not retrieve live Neo4j schema ({e}). Using canonical schema.")
        
    return DEFAULT_INVENTORY_SCHEMA.strip()
