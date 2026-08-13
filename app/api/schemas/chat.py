from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Natural language graph question")
    session_id: Optional[str] = Field(default=None, description="UUID session identifier")


class GraphDataPayload(BaseModel):
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []


class ChatMetadata(BaseModel):
    intent: Optional[str] = None
    generated_cypher: Optional[str] = None
    is_valid_cypher: Optional[bool] = None
    retry_count: int = 0
    execution_time_ms: Optional[float] = None
    record_count: Optional[int] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    request_id: str
    graph_data: Optional[GraphDataPayload] = None
    metadata: Optional[ChatMetadata] = None


class SessionCreateRequest(BaseModel):
    title: Optional[str] = "New Knowledge Graph Chat"


class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str
