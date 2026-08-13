from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.api.deps import require_role_dep
from app.api.schemas.ingest import IngestPreviewResponse, IngestCommitResponse
from app.services.graph_ingestion_service import GraphIngestionService
from app.security.rbac import Role

router = APIRouter(prefix="/ingest", tags=["Graph CSV Ingestion"])


@router.post("/preview", response_model=IngestPreviewResponse)
async def preview_graph_csv(
    mode: str = Form(default="nodes"),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role_dep(Role.MANAGER))
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")
        
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 10MB limit.")
        
    try:
        preview = GraphIngestionService.preview_csv(contents, mode=mode)
        return IngestPreviewResponse(**preview)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/commit", response_model=IngestCommitResponse)
async def commit_graph_csv(
    mode: str = Form(default="nodes"),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role_dep(Role.MANAGER))
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")
        
    contents = await file.read()
    try:
        if mode == "nodes":
            res = GraphIngestionService.commit_nodes_csv(contents)
        else:
            res = GraphIngestionService.commit_relationships_csv(contents)
        return IngestCommitResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest graph CSV: {str(e)}")
