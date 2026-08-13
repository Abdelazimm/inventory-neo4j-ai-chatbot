from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user_optional
from app.api.schemas.chat import SessionCreateRequest, SessionResponse
from app.services.session_service import GraphSessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse)
def create_session(
    request: SessionCreateRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    user_id = current_user["user_id"] if current_user else None
    session = GraphSessionService.create_session(user_id=user_id, title=request.title or "New Knowledge Graph Chat")
    return SessionResponse(**session)


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    current_user: dict = Depends(get_current_user_optional)
):
    user_id = current_user["user_id"] if current_user else None
    sessions = GraphSessionService.list_sessions(user_id=user_id)
    return [SessionResponse(**s) for s in sessions]


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    user_id = current_user["user_id"] if current_user else None
    session = GraphSessionService.get_session(session_id=session_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return SessionResponse(**session)


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    user_id = current_user["user_id"] if current_user else None
    deleted = GraphSessionService.delete_session(session_id=session_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return {"status": "success", "message": f"Session '{session_id}' deleted successfully."}
