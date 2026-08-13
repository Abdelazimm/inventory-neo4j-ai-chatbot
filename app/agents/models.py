from typing import Literal, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class IntentResult(BaseModel):
    """Structured classification of user intent for Neo4j knowledge graph."""
    intent: Literal["graph_query", "chitchat", "mutation", "unknown"] = Field(
        description="The primary intent of the user message."
    )
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Confidence score between 0.0 and 1.0."
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Brief reasoning for the classification."
    )


class CypherGenerationResult(BaseModel):
    """Structured Cypher generation output."""
    query: str = Field(
        description="The generated raw Cypher query string to be executed."
    )
    operation: Literal["read"] = Field(
        default="read",
        description="Operation type, must be 'read' for analytical graph queries."
    )
    thought_process: Optional[str] = Field(
        default=None,
        description="Internal query planning notes."
    )


class CypherCorrectionResult(BaseModel):
    """Structured Cypher correction output."""
    query: str = Field(
        description="The corrected Cypher query string."
    )
    explanation_of_fix: Optional[str] = Field(
        default=None,
        description="Explanation of what was corrected."
    )


class GraphMutationRequest(BaseModel):
    """Structured intent request for Neo4j graph mutations."""
    action: Literal["create", "update", "delete"]
    node_label: str = Field(description="Target node label, e.g. Asset, Vendor, Item, Site")
    node_id: Optional[Union[str, int]] = Field(default=None, description="Unique identifier (e.g. asset_tag, vendor_code)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Properties to set")
    relationships: Optional[Dict[str, Any]] = Field(default=None, description="Optional target relationship to link")
    confirmation_required: bool = Field(default=True)
