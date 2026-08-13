import pytest
from app.services.session_service import GraphSessionService


def test_graph_session_lifecycle():
    s1 = GraphSessionService.create_session(user_id=1, title="Test Session 1")
    assert s1["session_id"] is not None

    s2 = GraphSessionService.create_session(user_id=2, title="Test Session 2")
    assert s2["session_id"] != s1["session_id"]

    u1_sessions = GraphSessionService.list_sessions(user_id=1)
    u1_ids = [s["session_id"] for s in u1_sessions]
    assert s1["session_id"] in u1_ids
    assert s2["session_id"] not in u1_ids

    deleted = GraphSessionService.delete_session(s1["session_id"], user_id=1)
    assert deleted is True
    assert GraphSessionService.get_session(s1["session_id"]) is None
