import pytest
from fastapi import HTTPException

from app.main import (
    ROLE_SCOPES,
    PermissionSet,
    Principal,
    Settings,
    TokenCreateRequest,
    create_token,
    current_principal,
    health,
    me,
    permissions,
    ready,
)


def test_health() -> None:
    response = health()

    assert response.status == "ok"
    assert response.service == "authorization-adapter"


def test_ready_reports_configuration() -> None:
    response = ready(Settings())

    assert response.status == "ready"
    assert "token_secret" in response.checks


def test_me_returns_demo_principal() -> None:
    principal = current_principal(Settings(dev_auth_enabled=True))
    response = me(principal)

    assert response.identity_id == "dev-admin"
    assert "admin:write" in response.permissions.scopes


def test_me_requires_configured_auth_provider() -> None:
    with pytest.raises(HTTPException) as exc:
        current_principal(Settings())

    assert exc.value.status_code == 401


def test_me_accepts_forwarded_identity_headers() -> None:
    principal = current_principal(
        Settings(dev_auth_enabled=True),
        identity_id="kratos-123",
        email="owner@example.test",
        display_name="Owner",
    )

    assert principal.identity_id == "kratos-123"
    assert principal.email == "owner@example.test"
    assert principal.display_name == "Owner"


def test_dev_identity_headers_are_rejected_in_production() -> None:
    with pytest.raises(HTTPException) as exc:
        current_principal(Settings(environment="production", dev_auth_enabled=True))

    assert exc.value.status_code == 503


def test_permissions_catalog_exposes_owner_role() -> None:
    principal = Principal(
        identity_id="dev-admin",
        email="admin@example.com",
        display_name="OpenVend Admin",
        auth_strategy="test",
        permissions=PermissionSet(roles=["owner"], scopes=ROLE_SCOPES["owner"]),
    )

    catalog = permissions(principal)

    assert catalog.default_role == "operator"
    assert catalog.roles["owner"] == ROLE_SCOPES["owner"]


def test_ready_rejects_production_placeholder_secrets() -> None:
    with pytest.raises(HTTPException) as exc:
        ready(Settings(environment="production"))

    assert exc.value.status_code == 503
    assert exc.value.detail["configuration"] == "invalid-production-config"


def test_create_agent_token_with_allowed_scope() -> None:
    principal = Principal(
        identity_id="dev-admin",
        email="admin@example.com",
        display_name="OpenVend Admin",
        auth_strategy="test",
        permissions=PermissionSet(roles=["owner"], scopes=ROLE_SCOPES["owner"]),
    )

    response = create_token(
        TokenCreateRequest(name="Codex local", scopes=["contacts:read"], expires_in_days=7),
        principal,
    )

    assert response.token.startswith("ov_agent_")
    assert response.audit_event["action"] == "agent_token.create"


def test_create_agent_token_requires_agent_write_scope() -> None:
    principal = Principal(
        identity_id="operator",
        email="operator@example.com",
        display_name="Operator",
        auth_strategy="test",
        permissions=PermissionSet(roles=["operator"], scopes=ROLE_SCOPES["operator"]),
    )

    with pytest.raises(HTTPException) as exc:
        create_token(
            TokenCreateRequest(name="Codex local", scopes=["contacts:read"], expires_in_days=7),
            principal,
        )

    assert exc.value.status_code == 403


def test_create_agent_token_rejects_unknown_scope() -> None:
    principal = Principal(
        identity_id="dev-admin",
        email="admin@example.com",
        display_name="OpenVend Admin",
        auth_strategy="test",
        permissions=PermissionSet(roles=["owner"], scopes=ROLE_SCOPES["owner"]),
    )

    with pytest.raises(HTTPException) as exc:
        create_token(
            TokenCreateRequest(name="Too much", scopes=["database:drop"], expires_in_days=7),
            principal,
        )

    assert exc.value.status_code == 403
