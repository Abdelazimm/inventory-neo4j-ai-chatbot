from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class IngestPreviewResponse(BaseModel):
    mode: str
    total_rows: int
    columns_found: List[str]
    missing_required_columns: List[str]
    is_valid: bool
    preview: List[Dict[str, Any]]


class IngestCommitResponse(BaseModel):
    mode: str
    total_processed: int
    created_or_updated: Optional[int] = 0
    created: Optional[int] = 0
    errors: List[str]
