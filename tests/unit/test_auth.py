import pytest
from app.security.auth import get_user_by_username, verify_password, create_access_token, decode_access_token
from app.security.rbac import Role, check_role_permission


def test_auth_users_and_passwords():
    admin = get_user_by_username("admin")
    assert admin is not None
    assert verify_password("admin123", admin["hashed_password"]) is True
    assert verify_password("wrong", admin["hashed_password"]) is False


def test_jwt_lifecycle():
    token = create_access_token({"sub": "admin", "role": "admin", "user_id": 1})
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded["sub"] == "admin"
    assert decoded["role"] == "admin"


def test_rbac_rules():
    assert check_role_permission("admin", Role.ADMIN) is True
    assert check_role_permission("manager", Role.ADMIN) is False
    assert check_role_permission("manager", Role.MANAGER) is True
    assert check_role_permission("viewer", Role.MANAGER) is False
