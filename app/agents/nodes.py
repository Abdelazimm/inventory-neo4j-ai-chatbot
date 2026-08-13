import json
import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.config import settings
from app.agents.state import Neo4jInventoryState
from app.agents.models import IntentResult, CypherGenerationResult, CypherCorrectionResult
from app.agents.schema import get_dynamic_neo4j_schema
from app.agents.validator import validate_cypher_query
from app.agents.executor import execute_cypher_query
from app.agents.prompts import (
    INTENT_SYSTEM_PROMPT, CHITCHAT_SYSTEM_PROMPT,
    CYPHER_GENERATOR_SYSTEM_PROMPT, CYPHER_CORRECTOR_SYSTEM_PROMPT,
    RESPONSE_SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)


def get_llm():
    return ChatOpenAI(
        model=settings.MODEL_NAME,
        temperature=settings.TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )


def intent_parser_node(state: Neo4jInventoryState) -> Dict[str, Any]:
    """Classifies user message intent into structured IntentResult."""
    question = state.get("question", "")
    recent_messages = state.get("messages", [])[-6:]
    
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(IntentResult)
        result: IntentResult = structured_llm.invoke(
            [SystemMessage(content=INTENT_SYSTEM_PROMPT)] +
            recent_messages +
            [HumanMessage(content=f"Classify message: '{question}'")]
        )
        return {
            "intent": result.intent,
            "intent_confidence": result.confidence,
            "error": None
        }
    except Exception as e:
        logger.warning(f"Neo4j intent parser heuristic fallback: {e}")
        q_lower = question.lower()
        if any(g in q_lower for g in ["hello", "hi", "hey", "good morning", "who are you", "what can you do"]):
            return {"intent": "chitchat", "intent_confidence": 0.9, "error": None}
        if any(m in q_lower for m in ["delete", "remove", "create node", "add vendor", "update asset", "detach delete"]):
            return {"intent": "mutation", "intent_confidence": 0.85, "error": None}
        return {"intent": "graph_query", "intent_confidence": 0.9, "error": None}


def chitchat_node(state: Neo4jInventoryState) -> Dict[str, Any]:
    """Handles general conversational chitchat."""
    question = state.get("question", "")
    recent_messages = state.get("messages", [])[-4:]
    
    try:
        llm = get_llm()
        response = llm.invoke(
            [SystemMessage(content=CHITCHAT_SYSTEM_PROMPT)] +
            recent_messages +
            [HumanMessage(content=question)]
        )
        content = response.content
    except Exception:
        content = "Hello! I am your AI Inventory Knowledge Graph Assistant. I can help analyze multi-hop supplier dependencies, asset tracking across sites, and graph relationships."
        
    return {
        "messages": [AIMessage(content=content)]
    }


def cypher_generator_node(state: Neo4jInventoryState) -> Dict[str, Any]:
    """Generates structured Cypher query based on dynamic schema."""
    question = state.get("question", "")
    schema = get_dynamic_neo4j_schema()
    recent_messages = state.get("messages", [])[-6:]
    
    prompt = CYPHER_GENERATOR_SYSTEM_PROMPT.format(schema=schema)
    
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(CypherGenerationResult)
        result: CypherGenerationResult = structured_llm.invoke(
            [SystemMessage(content=prompt)] +
            recent_messages +
            [HumanMessage(content=question)]
        )
        query = result.query
    except Exception:
        try:
            llm = get_llm()
            resp = llm.invoke(
                [SystemMessage(content=prompt + "\nReturn ONLY the raw Cypher query, no markdown.")] +
                recent_messages +
                [HumanMessage(content=question)]
            )
            query = resp.content.strip()
        except Exception:
            query = "MATCH (a:Asset) RETURN a.asset_tag AS AssetTag, a.name AS AssetName LIMIT 5;"
            
    return {
        "cypher_query": query,
        "is_valid": None,
        "validation_error": None,
        "execution_error": None,
        "error": None
    }


def cypher_validator_node(state: Neo4jInventoryState) -> Dict[str, Any]:
    """Validates the generated Cypher query for AST safety and read-only compliance."""
    query = state.get("cypher_query", "")
    is_valid, validation_error = validate_cypher_query(query)
    
    return {
        "is_valid": is_valid,
        "validation_error": validation_error,
        "error": validation_error if not is_valid else None
    }


def cypher_executor_node(state: Neo4jInventoryState) -> Dict[str, Any]:
    """Executes the validated Cypher query against Neo4j."""
    query = state.get("cypher_query", "")
    
    if not state.get("is_valid", False):
        return {
            "error": state.get("validation_error", "Cypher validation failed."),
            "execution_error": state.get("validation_error", "Cypher validation failed.")
        }
        
    try:
        records, graph_data, exec_time = execute_cypher_query(query)
        return {
            "cypher_result": records,
            "graph_data": graph_data,
            "execution_time_ms": exec_time,
            "execution_error": None,
            "error": None
        }
    except Exception as e:
        return {
            "execution_error": str(e),
            "error": str(e),
            "retries": state.get("retries", 0) + 1
        }


def cypher_corrector_node(state: Neo4jInventoryState) -> Dict[str, Any]:
    """Corrects a failed Cypher query using graph schema diagnostic."""
    schema = get_dynamic_neo4j_schema()
    query = state.get("cypher_query", "")
    error_msg = state.get("error", "Unknown Cypher error")
    question = state.get("question", "")
    recent_messages = state.get("messages", [])[-4:]
    
    prompt = CYPHER_CORRECTOR_SYSTEM_PROMPT.format(
        schema=schema,
        cypher_query=query,
        error=error_msg
    )
    
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(CypherCorrectionResult)
        result: CypherCorrectionResult = structured_llm.invoke(
            [SystemMessage(content=prompt)] +
            recent_messages +
            [HumanMessage(content=f"Fix Cypher query for: {question}")]
        )
        fixed_query = result.query
    except Exception:
        try:
            llm = get_llm()
            resp = llm.invoke(
                [SystemMessage(content=prompt + "\nReturn ONLY the fixed raw Cypher query.")] +
                recent_messages +
                [HumanMessage(content=f"Fix Cypher query for: {question}")]
            )
            fixed_query = resp.content.strip()
        except Exception:
            fixed_query = "MATCH (a:Asset) RETURN a.asset_tag, a.name LIMIT 5;"
            
    return {
        "cypher_query": fixed_query,
        "is_valid": None,
        "validation_error": None,
        "error": None
    }


def final_response_node(state: Neo4jInventoryState) -> Dict[str, Any]:
    """Synthesizes grounded conversational answer from graph records."""
    question = state.get("question", "")
    cypher_result = state.get("cypher_result", [])
    recent_messages = state.get("messages", [])[-4:]
    
    result_str = json.dumps(cypher_result, default=str) if isinstance(cypher_result, (list, dict)) else str(cypher_result)
    
    prompt = f"{RESPONSE_SYSTEM_PROMPT}\n\nUser Question: {question}\n\nGraph Database Results:\n{result_str}"
    
    try:
        llm = get_llm()
        response = llm.invoke(
            [SystemMessage(content=prompt)] +
            recent_messages +
            [HumanMessage(content=f"Synthesize answer for: {question}")]
        )
        content = response.content
    except Exception:
        if not cypher_result:
            content = "No matching records or relationship paths were found in the knowledge graph."
        else:
            content = f"Here are the retrieved graph results:\n{result_str}"
            
    return {
        "messages": [AIMessage(content=content)]
    }


def error_response_node(state: Neo4jInventoryState) -> Dict[str, Any]:
    """Provides a graceful failure message."""
    error_msg = state.get("error", "Unable to complete graph query.")
    
    if "forbidden" in error_msg.lower() or "read-only" in error_msg.lower():
        msg = f"Security Notice: The requested graph operation could not be performed. {error_msg}"
    else:
        msg = "I was unable to retrieve the requested graph relationship after multiple attempts. Please try rephrasing your question."
        
    return {
        "messages": [AIMessage(content=msg)]
    }
