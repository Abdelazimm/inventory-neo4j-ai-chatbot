import uuid
import logging
from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage
from app.api.deps import get_current_user_optional
from app.api.schemas.chat import ChatRequest, ChatResponse, ChatMetadata, GraphDataPayload
from app.agents.graph import neo4j_agent_app
from app.services.session_service import GraphSessionService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    request_id = str(uuid.uuid4())
    user_id = current_user["user_id"] if current_user else None
    user_role = current_user["role"] if current_user else "viewer"
    
    # Manage session
    session_id = request.session_id
    if not session_id:
        new_session = GraphSessionService.create_session(user_id=user_id, title=request.message[:40])
        session_id = new_session["session_id"]
    else:
        existing = GraphSessionService.get_session(session_id=session_id)
        if not existing:
            GraphSessionService.create_session(user_id=user_id, title=request.message[:40])

    config = {"configurable": {"thread_id": session_id}}
    
    state_input = {
        "messages": [HumanMessage(content=request.message)],
        "question": request.message,
        "request_id": request_id,
        "session_id": session_id,
        "user_id": user_id,
        "user_role": user_role,
        "retries": 0,
        "model_name": settings.MODEL_NAME
    }
    
    try:
        final_state = neo4j_agent_app.invoke(state_input, config=config)
    except Exception as e:
        logger.error(f"Neo4j LangGraph execution failed: {str(e)}", exc_info=True)
        return ChatResponse(
            answer="I encountered an error querying the Neo4j Knowledge Graph. Please verify your connection or rephrase your question.",
            session_id=session_id,
            request_id=request_id,
            metadata=ChatMetadata(
                intent="unknown",
                retry_count=0,
                model=settings.MODEL_NAME
            )
        )
        
    answer = "I was unable to retrieve a response from the knowledge graph."
    if final_state and "messages" in final_state and len(final_state["messages"]) > 0:
        latest_msg = final_state["messages"][-1]
        answer = latest_msg.content

    # Extract graph visualization data
    raw_graph_data = final_state.get("graph_data")
    graph_payload = None
    if raw_graph_data and (len(raw_graph_data.get("nodes", [])) > 0 or len(raw_graph_data.get("edges", [])) > 0):
        graph_payload = GraphDataPayload(
            nodes=raw_graph_data.get("nodes", []),
            edges=raw_graph_data.get("edges", [])
        )

    cypher_result = final_state.get("cypher_result")
    rec_count = len(cypher_result) if isinstance(cypher_result, list) else None

    metadata = ChatMetadata(
        intent=final_state.get("intent"),
        generated_cypher=final_state.get("cypher_query"),
        is_valid_cypher=final_state.get("is_valid"),
        retry_count=final_state.get("retries", 0),
        execution_time_ms=final_state.get("execution_time_ms"),
        record_count=rec_count,
        model=settings.MODEL_NAME
    )
    
    return ChatResponse(
        answer=answer,
        session_id=session_id,
        request_id=request_id,
        graph_data=graph_payload,
        metadata=metadata
    )
