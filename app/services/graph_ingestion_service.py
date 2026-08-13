import io
import csv
import json
from typing import Dict, Any, List
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


def _read_csv_dicts(file_content: bytes) -> tuple[List[str], List[Dict[str, Any]]]:
    text_content = file_content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text_content))
    columns = reader.fieldnames or []
    rows = [row for row in reader]
    return list(columns), rows


class GraphIngestionService:
    @staticmethod
    def preview_csv(file_content: bytes, mode: str = "nodes") -> Dict[str, Any]:
        """Parses CSV and returns column analysis and preview records."""
        try:
            cols, rows = _read_csv_dicts(file_content)
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")

        preview_rows = rows[:10]
        
        if mode == "nodes":
            required = ["label", "id", "name"]
        else:
            required = ["from_label", "from_id", "relationship_type", "to_label", "to_id"]
            
        missing = [c for c in required if c not in cols]
        
        return {
            "mode": mode,
            "total_rows": len(rows),
            "columns_found": cols,
            "missing_required_columns": missing,
            "is_valid": len(missing) == 0,
            "preview": preview_rows
        }

    @staticmethod
    def commit_nodes_csv(file_content: bytes) -> Dict[str, Any]:
        """Ingests nodes CSV into Neo4j using parameterized MERGE queries."""
        cols, rows = _read_csv_dicts(file_content)
        driver = get_neo4j_driver()
        
        created = 0
        errors = []
        
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            for idx, row in enumerate(rows):
                label = str(row.get("label", "")).strip()
                node_id = str(row.get("id", "")).strip()
                name = str(row.get("name", "")).strip()
                
                # Parse additional properties
                props = {}
                raw_props = row.get("properties")
                if raw_props:
                    try:
                        props = json.loads(raw_props) if isinstance(raw_props, str) else raw_props
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
            "total_processed": len(rows),
            "created_or_updated": created,
            "errors": errors
        }

    @staticmethod
    def commit_relationships_csv(file_content: bytes) -> Dict[str, Any]:
        """Ingests relationships CSV into Neo4j using parameterized MERGE."""
        cols, rows = _read_csv_dicts(file_content)
        driver = get_neo4j_driver()
        
        created = 0
        errors = []
        
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            for idx, row in enumerate(rows):
                from_label = str(row.get("from_label", "")).strip()
                from_id = str(row.get("from_id", "")).strip()
                rel_type = str(row.get("relationship_type", "")).strip().upper()
                to_label = str(row.get("to_label", "")).strip()
                to_id = str(row.get("to_id", "")).strip()
                
                from_pk = NODE_ID_MAP.get(from_label.lower(), "id")
                to_pk = NODE_ID_MAP.get(to_label.lower(), "id")
                
                query = f"""
                MATCH (a:{from_label} {{{from_pk}: $from_id}})
                MATCH (b:{to_label} {{{to_pk}: $to_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                RETURN count(r) AS created_count
                """
                try:
                    session.run(query, {"from_id": from_id, "to_id": to_id})
                    created += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
                    
        return {
            "mode": "relationships",
            "total_processed": len(rows),
            "created": created,
            "errors": errors
        }
