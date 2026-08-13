from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.api.schemas.mutations import (
    GraphMutationCreateRequest, GraphMutationPreviewResponse, GraphMutationExecutionResponse
)
from app.services.graph_mutation_service import GraphMutationService, PENDING_GRAPH_MUTATIONS
from app.security.rbac import Role, check_role_permission

router = APIRouter(prefix="/mutations", tags=["Graph Mutations"])


@router.post("/preview", response_model=GraphMutationPreviewResponse)
def preview_mutation(
    request: GraphMutationCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] == Role.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Viewer role cannot request graph mutations.")
        
    if request.action.lower() == "delete" and current_user["role"] != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Delete graph mutations require Admin role.")
        
    try:
        preview = GraphMutationService.create_preview(
            action=request.action,
            node_label=request.node_label,
            node_id=request.node_id,
            properties=request.properties,
            user_id=current_user["user_id"]
        )
        return GraphMutationPreviewResponse(**preview)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{action_id}/confirm", response_model=GraphMutationExecutionResponse)
def confirm_mutation(
    action_id: str,
    current_user: dict = Depends(get_current_user)
):
    if action_id not in PENDING_GRAPH_MUTATIONS:
        raise HTTPException(status_code=404, detail="Mutation request not found or expired.")
        
    mutation = PENDING_GRAPH_MUTATIONS[action_id]
    if mutation["action"] == "delete" and not check_role_permission(current_user["role"], Role.ADMIN):
        raise HTTPException(status_code=403, detail="Only Admins can confirm graph node deletion.")
        
    try:
        res = GraphMutationService.confirm_mutation(action_id)
        return GraphMutationExecutionResponse(**res)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mutation execution failed: {str(e)}")


@router.post("/{action_id}/cancel")
def cancel_mutation(action_id: str, current_user: dict = Depends(get_current_user)):
    return GraphMutationService.cancel_mutation(action_id)
