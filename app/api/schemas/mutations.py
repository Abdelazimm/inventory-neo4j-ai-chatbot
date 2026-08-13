from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class GraphMutationCreateRequest(BaseModel):
    action: str = Field(..., description="'create', 'update', or 'delete'")
    node_label: str = Field(..., description="e.g. 'Asset', 'Vendor', 'Item', 'Site'")
    node_id: Optional[Union[str, int]] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphMutationPreviewResponse(BaseModel):
    action_id: str
    action: str
    node_label: str
    node_id: Optional[Union[str, int]] = None
    properties: Dict[str, Any]
    summary: str
    expires_at: str


class GraphMutationExecutionResponse(BaseModel):
    status: str
    message: str
