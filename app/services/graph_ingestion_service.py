import io
import json
from typing import Dict, Any, List
import pandas as pd
from app.database.neo4j_connection import get_neo4j_driver
from app.config import settings

NODE_ID_MAP = {
    "asset": "asset_tag",
    "vendor": "vendor_code",
    "item": "item_code",
    "site": "site_code",
    "location": "location_code",
    "customer": "customer_code",
    "purchaseorder": "po_number",
    "salesorder": "so_number",
    "category": "name"
}


class GraphIngestionService:
    @staticmethod
    def preview_csv(file_content: bytes, mode: str = "nodes") -> Dict[str, Any]:
        """Parses CSV and returns column analysis and preview records."""
        try:
            df = pd.read_csv(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")

        preview_rows = df.head(10).fillna("").to_dict(orient="records")
        cols = list(df.columns)
        
        if mode == "nodes":
            required = ["label", "id", "name"]
        else:
            required = ["from_label", "from_id", "relationship_type", "to_label", "to_id"]
            
        missing = [c for c in required if c not in cols]
        
        return {
            "mode": mode,
            "total_rows": len(df),
            "columns_found": cols,
            "missing_required_columns": missing,
            "is_valid": len(missing) == 0,
            "preview": preview_rows
        }

    @staticmethod
    def commit_nodes_csv(file_content: bytes) -> Dict[str, Any]:
        """Ingests nodes CSV into Neo4j using parameterized MERGE queries."""
        df = pd.read_csv(io.BytesIO(file_content))
        driver = get_neo4j_driver()
        
        created = 0
        updated = 0
        errors = []
        
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            for idx, row in df.iterrows():
                label = str(row["label"]).strip()
                node_id = str(row["id"]).strip()
                name = str(row.get("name", "")).strip()
                
                # Parse additional properties
                props = {}
                if "properties" in row and pd.notna(row["properties"]):
                    try:
                        props = json.loads(str(row["properties"])) if isinstance(row["properties"], str) else row["properties"]
                    except Exception:
                        pass
                props["name"] = name
                
                id_prop = NODE_ID_MAP.get(label.lower(), "id")
                props[id_prop] = node_id
                
                query = f"""
                MERGE (n:{label} {{{id_prop}: $node_id}})
                SET n += $props
                RETURN n
                """
                try:
                    session.run(query, {"node_id": node_id, "props": props})
                    created += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
                    
        return {
            "mode": "nodes",
            "total_processed": len(df),
            "created_or_updated": created,
            "errors": errors
        }

    @staticmethod
    def commit_relationships_csv(file_content: bytes) -> Dict[str, Any]:
        """Ingests relationships CSV into Neo4j using parameterized MERGE."""
        df = pd.read_csv(io.BytesIO(file_content))
        driver = get_neo4j_driver()
        
        created = 0
        errors = []
        
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            for idx, row in df.iterrows():
                from_label = str(row["from_label"]).strip()
                from_id = str(row["from_id"]).strip()
                rel_type = str(row["relationship_type"]).strip().upper()
                to_label = str(row["to_label"]).strip()
                to_id = str(row["to_id"]).strip()
                
                from_pk = NODE_ID_MAP.get(from_label.lower(), "id")
                to_pk = NODE_ID_MAP.get(to_label.lower(), "id")
                
                query = f"""
                MATCH (a:{from_label} {{{from_pk}: $from_id}})
                MATCH (b:{to_label} {{{to_pk}: $to_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                RETURN count(r) AS created_count
                """
                try:
                    res = session.run(query, {"from_id": from_id, "to_id": to_id})
                    created += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
                    
        return {
            "mode": "relationships",
            "total_processed": len(df),
            "created": created,
            "errors": errors
        }
