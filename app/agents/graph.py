import sqlite3
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from app.agents.state import Neo4jInventoryState
from app.agents.nodes import (
    intent_parser_node,
    chitchat_node,
    cypher_generator_node,
    cypher_validator_node,
    cypher_executor_node,
    cypher_corrector_node,
    final_response_node,
    error_response_node
)
from app.config import settings


def route_by_intent(state: Neo4jInventoryState) -> Literal["chitchat", "cypher_generator"]:
    intent = state.get("intent", "graph_query")
    if intent == "chitchat":
        return "chitchat"
    return "cypher_generator"


def route_after_validation(state: Neo4jInventoryState) -> Literal["cypher_executor", "cypher_corrector", "error_response"]:
    if not state.get("is_valid", False):
        val_error = state.get("validation_error", "")
        if any(sec in val_error.lower() for sec in ["forbidden", "only read-only", "detected", "multiple"]):
            return "error_response"
            
        retries = state.get("retries", 0)
        if retries < 3:
            return "cypher_corrector"
        return "error_response"
    return "cypher_executor"


def route_after_execution(state: Neo4jInventoryState) -> Literal["final_response", "cypher_corrector", "error_response"]:
    error = state.get("execution_error") or state.get("error")
    if error is None:
        return "final_response"
    
    retries = state.get("retries", 0)
    if retries < 3:
        return "cypher_corrector"
    return "error_response"


def build_neo4j_graph(checkpointer=None):
    workflow = StateGraph(Neo4jInventoryState)
    
    # Add Nodes
    workflow.add_node("intent_parser", intent_parser_node)
    workflow.add_node("chitchat", chitchat_node)
    workflow.add_node("cypher_generator", cypher_generator_node)
    workflow.add_node("cypher_validator", cypher_validator_node)
    workflow.add_node("cypher_executor", cypher_executor_node)
    workflow.add_node("cypher_corrector", cypher_corrector_node)
    workflow.add_node("final_response", final_response_node)
    workflow.add_node("error_response", error_response_node)
    
    # Set Entry Point
    workflow.set_entry_point("intent_parser")
    
    # Intent Branching
    workflow.add_conditional_edges(
        "intent_parser",
        route_by_intent,
        {
            "chitchat": "chitchat",
            "cypher_generator": "cypher_generator"
        }
    )
    
    workflow.add_edge("chitchat", END)
    
    # Generator -> Validator
    workflow.add_edge("cypher_generator", "cypher_validator")
    
    # Validator -> (Executor | Corrector | ErrorResponse)
    workflow.add_conditional_edges(
        "cypher_validator",
        route_after_validation,
        {
            "cypher_executor": "cypher_executor",
            "cypher_corrector": "cypher_corrector",
            "error_response": "error_response"
        }
    )
    
    # Executor -> (FinalResponse | Corrector | ErrorResponse)
    workflow.add_conditional_edges(
        "cypher_executor",
        route_after_execution,
        {
            "final_response": "final_response",
            "cypher_corrector": "cypher_corrector",
            "error_response": "error_response"
        }
    )
    
    # Corrector -> Validator (Always re-validate corrected queries!)
    workflow.add_edge("cypher_corrector", "cypher_validator")
    
    # Terminal edges
    workflow.add_edge("final_response", END)
    workflow.add_edge("error_response", END)
    
    return workflow.compile(checkpointer=checkpointer)


# Setup persistent SQLite checkpointer for session state
try:
    checkpointer_conn = sqlite3.connect(settings.CHECKPOINTS_DB_PATH, check_same_thread=False)
    sqlite_saver = SqliteSaver(checkpointer_conn)
    sqlite_saver.setup()
    neo4j_agent_app = build_neo4j_graph(checkpointer=sqlite_saver)
except Exception:
    neo4j_agent_app = build_neo4j_graph()
