import pytest
from app.services.graph_mutation_service import GraphMutationService, PENDING_GRAPH_MUTATIONS


def test_graph_mutation_preview_and_cancel():
    preview = GraphMutationService.create_preview(
        action="create",
        node_label="Asset",
        node_id="TAG-9999",
        properties={"name": "Preview Asset", "cost": 1500.0},
        user_id=1
    )
    assert "action_id" in preview
    action_id = preview["action_id"]
    assert action_id in PENDING_GRAPH_MUTATIONS

    cancel_res = GraphMutationService.cancel_mutation(action_id)
    assert cancel_res["status"] == "cancelled"
    assert action_id not in PENDING_GRAPH_MUTATIONS
