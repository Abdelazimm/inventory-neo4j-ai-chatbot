import time
from typing import List, Dict, Any, Tuple, Optional
from neo4j import Record
# pyrefly: ignore [missing-import]
from neo4j.graph import Node, Relationship, Path
from app.database.neo4j_connection import get_neo4j_driver
from app.config import settings


def serialize_neo4j_value(val: Any) -> Any:
    """Recursively serializes Neo4j driver objects into JSON-compatible python types."""
    if isinstance(val, Node):
        return {
            "__type__": "node",
            "id": val.element_id,
            "labels": list(val.labels),
            "properties": dict(val.items())
        }
    elif isinstance(val, Relationship):
        return {
            "__type__": "relationship",
            "id": val.element_id,
            "type": val.type,
            "start_node": val.start_node.element_id if hasattr(val, "start_node") else None,
            "end_node": val.end_node.element_id if hasattr(val, "end_node") else None,
            "properties": dict(val.items())
        }
    elif isinstance(val, Path):
        return {
            "__type__": "path",
            "nodes": [serialize_neo4j_value(n) for n in val.nodes],
            "relationships": [serialize_neo4j_value(r) for r in val.relationships]
        }
    elif isinstance(val, list):
        return [serialize_neo4j_value(v) for v in val]
    elif isinstance(val, dict):
        return {k: serialize_neo4j_value(v) for k, v in val.items()}
    return val


def extract_graph_elements(records: List[Dict[str, Any]]) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """Extracts unique nodes and edges from records for frontend graph visualization."""
    nodes_map: Dict[str, Dict[str, Any]] = {}
    edges_list: List[Dict[str, Any]] = []

    def inspect_element(elem: Any):
        if isinstance(elem, dict) and elem.get("__type__") == "node":
            node_id = str(elem["id"])
            if node_id not in nodes_map:
                labels = elem.get("labels", ["Entity"])
                props = elem.get("properties", {})
                display_name = props.get("name") or props.get("asset_tag") or props.get("vendor_code") or labels[0]
                nodes_map[node_id] = {
                    "id": node_id,
                    "label": display_name,
                    "group": labels[0],
                    "properties": props
                }
        elif isinstance(elem, dict) and elem.get("__type__") == "relationship":
            edges_list.append({
                "id": str(elem["id"]),
                "source": str(elem["start_node"]),
                "target": str(elem["end_node"]),
                "label": elem.get("type", "RELATED"),
                "properties": elem.get("properties", {})
            })
        elif isinstance(elem, dict) and elem.get("__type__") == "path":
            for n in elem.get("nodes", []):
                inspect_element(n)
            for r in elem.get("relationships", []):
                inspect_element(r)
        elif isinstance(elem, list):
            for item in elem:
                inspect_element(item)
        elif isinstance(elem, dict):
            for v in elem.values():
                inspect_element(v)

    for rec in records:
        inspect_element(rec)

    if len(nodes_map) > 0 or len(edges_list) > 0:
        return {
            "nodes": list(nodes_map.values()),
            "edges": edges_list
        }
    return None


def execute_cypher_query(query: str, limit: int = None) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]], float]:
    """
    Executes a validated read-only Cypher query against Neo4j.
    Returns:
    - Serialized list of record dictionaries
    - Extracted graph visualization payload (nodes & edges) if present
    - Execution latency in milliseconds
    """
    max_records = limit or settings.MAX_CYPHER_RECORDS
    clean_query = query.strip().rstrip(";")
    
    start_time = time.time()
    driver = get_neo4j_driver()
    
    with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = session.run(clean_query)
        raw_records = result.fetch(max_records)
        
        serialized_records = []
        for rec in raw_records:
            rec_dict = {}
            for key in rec.keys():
                rec_dict[key] = serialize_neo4j_value(rec[key])
            serialized_records.append(rec_dict)

    execution_time_ms = round((time.time() - start_time) * 1000, 2)
    graph_payload = extract_graph_elements(serialized_records)
    
    return serialized_records, graph_payload, execution_time_ms
