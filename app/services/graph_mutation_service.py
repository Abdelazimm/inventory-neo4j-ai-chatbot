import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.database.neo4j_connection import get_neo4j_driver
from app.config import settings

PENDING_GRAPH_MUTATIONS: Dict[str, Dict[str, Any]] = {}

ID_FIELD_LOOKUP = {
    "asset": "asset_tag",
    "vendor": "vendor_code",
    "item": "item_code",
    "site": "site_code",
    "location": "location_code",
    "customer": "customer_code",
    "purchaseorder": "po_number",
    "salesorder": "so_number"
}


class GraphMutationService:
    @staticmethod
    def create_preview(action: str, node_label: str, node_id: Optional[Any], properties: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        action_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        mutation_data = {
            "action_id": action_id,
            "action": action.lower(),
            "node_label": node_label.capitalize(),
            "node_id": node_id,
            "properties": properties,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        PENDING_GRAPH_MUTATIONS[action_id] = mutation_data
        
        summary = f"Please confirm {action.upper()} on {node_label} (ID: {node_id})"
        if action.lower() == "delete":
            summary = f"CAUTION: You are about to DETACH DELETE {node_label} '{node_id}' and all its relationships."
            
        return {
            "action_id": action_id,
            "action": action,
            "node_label": node_label,
            "node_id": node_id,
            "properties": properties,
            "summary": summary,
            "expires_at": expires_at.isoformat()
        }

    @staticmethod
    def confirm_mutation(action_id: str) -> Dict[str, Any]:
        if action_id not in PENDING_GRAPH_MUTATIONS:
            raise ValueError("Graph mutation request not found or has expired.")
            
        mutation = PENDING_GRAPH_MUTATIONS[action_id]
        action = mutation["action"]
        node_label = mutation["node_label"]
        node_id = mutation["node_id"]
        props = mutation["properties"]
        
        pk_prop = ID_FIELD_LOOKUP.get(node_label.lower(), "id")
        driver = get_neo4j_driver()
        
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            if action == "create":
                props[pk_prop] = node_id
                query = f"MERGE (n:{node_label} {{{pk_prop}: $node_id}}) SET n += $props RETURN n"
                session.run(query, {"node_id": node_id, "props": props})
                msg = f"Successfully created node ({node_label}:{node_id})"
            elif action == "update":
                query = f"MATCH (n:{node_label} {{{pk_prop}: $node_id}}) SET n += $props RETURN n"
                res = session.run(query, {"node_id": node_id, "props": props})
                if not res.peek():
                    raise ValueError(f"Node ({node_label}:{node_id}) not found.")
                msg = f"Successfully updated node ({node_label}:{node_id})"
            elif action == "delete":
                query = f"MATCH (n:{node_label} {{{pk_prop}: $node_id}}) DETACH DELETE n"
                session.run(query, {"node_id": node_id})
                msg = f"Successfully deleted node ({node_label}:{node_id}) and detached relationships"
            else:
                raise ValueError(f"Unknown mutation action: '{action}'")

        del PENDING_GRAPH_MUTATIONS[action_id]
        return {"status": "success", "message": msg}

    @staticmethod
    def cancel_mutation(action_id: str) -> Dict[str, str]:
        if action_id in PENDING_GRAPH_MUTATIONS:
            del PENDING_GRAPH_MUTATIONS[action_id]
            return {"status": "cancelled", "message": "Graph mutation request cancelled."}
        return {"status": "not_found", "message": "Mutation request not found."}
