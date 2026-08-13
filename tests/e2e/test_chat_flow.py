import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from app.agents.models import IntentResult, CypherGenerationResult


def test_health_and_auth_flow(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    login_res = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_chitchat_graph_chat(client):
    with patch("app.agents.nodes.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentResult(intent="chitchat", confidence=0.95)
        mock_llm.with_structured_output.return_value = mock_structured
        mock_llm.invoke.return_value = AIMessage(content="Hello! I am your Inventory Knowledge Graph Assistant.")
        mock_get_llm.return_value = mock_llm

        res = client.post("/chat", json={"message": "Hello!"})
        assert res.status_code == 200
        data = res.json()
        assert "knowledge graph" in data["answer"].lower() or "hello" in data["answer"].lower()
        assert data["metadata"]["intent"] == "chitchat"


def test_graph_query_flow(client, admin_token):
    with patch("app.agents.nodes.get_llm") as mock_get_llm, \
         patch("app.agents.nodes.execute_cypher_query") as mock_exec:
        
        mock_llm = MagicMock()
        mock_intent = MagicMock()
        mock_intent.invoke.return_value = IntentResult(intent="graph_query", confidence=0.99)
        mock_cypher = MagicMock()
        mock_cypher.invoke.return_value = CypherGenerationResult(
            query="MATCH (v:Vendor {name: 'TechSupply Inc'})-[:SUPPLIES]->(i:Item) RETURN v.name, i.name;",
            operation="read"
        )
        mock_llm.with_structured_output.side_effect = [mock_intent, mock_cypher]
        mock_llm.invoke.return_value = AIMessage(content="TechSupply Inc supplies ThinkPad laptops and monitors.")
        mock_get_llm.return_value = mock_llm

        mock_exec.return_value = (
            [{"v.name": "TechSupply Inc", "i.name": "ThinkPad T14"}],
            {"nodes": [{"id": "1", "label": "TechSupply Inc", "group": "Vendor"}], "edges": []},
            15.5
        )

        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/chat", json={"message": "What items are supplied by TechSupply Inc?"}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "TechSupply" in data["answer"]
        assert data["metadata"]["is_valid_cypher"] is True
        assert data["graph_data"] is not None
