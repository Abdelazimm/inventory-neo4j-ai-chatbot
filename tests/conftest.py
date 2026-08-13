import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.security.auth import create_access_token


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_token():
    return create_access_token({"sub": "admin", "role": "admin", "user_id": 1})


@pytest.fixture
def manager_token():
    return create_access_token({"sub": "manager", "role": "manager", "user_id": 2})


@pytest.fixture
def viewer_token():
    return create_access_token({"sub": "viewer", "role": "viewer", "user_id": 3})
