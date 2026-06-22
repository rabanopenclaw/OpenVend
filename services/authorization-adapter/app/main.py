from __future__ import annotations

import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

SERVICE_NAME = "authorization-adapter"
API_PREFIX = "/api/v1/authz"


class Settings(BaseModel):
    environment: str = Field(default="development")
    token_secret: str = Field(default="replace-with-dev-secret")
    dev_auth_enabled: bool = Field(default=False)
    demo_identity_id: str = Field(default="dev-admin")
    demo_email: str = Field(default="admin@example.com")
    demo_display_name: str = Field(default="OpenVend Admin")
    demo_role: str = Field(default="owner")


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime


class ReadinessResponse(BaseModel):
    status: str
    service: str
    checks: dict[str, str]


class PermissionSet(BaseModel):
    roles: list[str]
    scopes: list[str]


class Principal(BaseModel):
    identity_id: str
    email: str
    display_name: str
    auth_strategy: str
    permissions: PermissionSet


class TokenCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=80)
    scopes: list[str] = Field(min_length=1)
    expires_in_days: int = Field(default=30, ge=1, le=365)


class TokenCreateResponse(BaseModel):
    token: str
    token_type: str = "agent"
    name: str
    scopes: list[str]
    expires_at: datetime
    audit_event: dict[str, str]


class PermissionCatalog(BaseModel):
    roles: dict[str, list[str]]
    default_role: str


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    return Settings(
        environment=os.getenv("OPENVEND_ENV", "development"),
        token_secret=os.getenv("AUTHZ_SERVICE_TOKEN_SECRET", "replace-with-dev-secret"),
        dev_auth_enabled=env_flag("AUTHZ_DEV_AUTH_ENABLED"),
        demo_identity_id=os.getenv("AUTHZ_DEMO_IDENTITY_ID", "dev-admin"),
        demo_email=os.getenv("AUTHZ_DEMO_EMAIL", "admin@example.com"),
        demo_display_name=os.getenv("AUTHZ_DEMO_DISPLAY_NAME", "OpenVend Admin"),
        demo_role=os.getenv("AUTHZ_DEMO_ROLE", "owner"),
    )


ROLE_SCOPES: dict[str, list[str]] = {
    "owner": [
        "contacts:read",
        "contacts:write",
        "inventory:read",
        "inventory:write",
        "orders:read",
        "orders:write",
        "reports:read",
        "exports:write",
        "agent:read",
        "agent:write",
        "admin:read",
        "admin:write",
    ],
    "operator": [
        "contacts:read",
        "contacts:write",
        "inventory:read",
        "orders:read",
        "reports:read",
    ],
    "agent": [
        "contacts:read",
        "inventory:read",
        "orders:read",
        "reports:read",
    ],
}


def current_principal(
    settings: Annotated[Settings, Depends(get_settings)],
    identity_id: Annotated[str | None, Header(alias="X-OpenVend-Identity-Id")] = None,
    email: Annotated[str | None, Header(alias="X-OpenVend-Email")] = None,
    display_name: Annotated[str | None, Header(alias="X-OpenVend-Display-Name")] = None,
) -> Principal:
    if settings.environment.lower() == "production" and settings.dev_auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Development identity headers are disabled in production.",
        )

    if not settings.dev_auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authenticated principal provider is configured.",
        )

    if settings.demo_role not in ROLE_SCOPES:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Configured demo role is unknown: {settings.demo_role}",
        )

    roles = [settings.demo_role]
    scopes = sorted({scope for role in roles for scope in ROLE_SCOPES[role]})
    return Principal(
        identity_id=identity_id or settings.demo_identity_id,
        email=email or settings.demo_email,
        display_name=display_name or settings.demo_display_name,
        auth_strategy="dev-header" if identity_id else "dev-demo-principal",
        permissions=PermissionSet(roles=roles, scopes=scopes),
    )


def require_scope(principal: Principal, scope: str) -> None:
    if scope not in principal.permissions.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Required scope is missing: {scope}",
        )


app = FastAPI(
    title="OpenVend Authorization Adapter",
    version="0.1.0",
    summary="ERP authorization, roles, scopes, and agent-token foundation.",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE_NAME, timestamp=datetime.now(UTC))


@app.get("/ready", response_model=ReadinessResponse, tags=["system"])
def ready(settings: Annotated[Settings, Depends(get_settings)]) -> ReadinessResponse:
    is_production = settings.environment.lower() == "production"
    has_placeholder_secret = settings.token_secret == "replace-with-dev-secret"
    checks = {
        "configuration": "ok",
        "token_secret": "placeholder" if has_placeholder_secret else "ok",
        "dev_auth": "enabled" if settings.dev_auth_enabled else "disabled",
        "identity_provider": "kratos-configured-upstream",
    }

    if is_production and (has_placeholder_secret or settings.dev_auth_enabled):
        checks["configuration"] = "invalid-production-config"
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=checks)

    return ReadinessResponse(status="ready", service=SERVICE_NAME, checks=checks)


@app.get("/me", response_model=Principal, tags=["identity"])
def me(principal: Annotated[Principal, Depends(current_principal)]) -> Principal:
    return principal


@app.get("/permissions", response_model=PermissionCatalog, tags=["authorization"])
def permissions(principal: Annotated[Principal, Depends(current_principal)]) -> PermissionCatalog:
    require_scope(principal, "admin:read")
    return PermissionCatalog(roles=ROLE_SCOPES, default_role="operator")


@app.post(
    "/tokens",
    response_model=TokenCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tokens"],
)
def create_token(
    request: TokenCreateRequest,
    principal: Annotated[Principal, Depends(current_principal)],
) -> TokenCreateResponse:
    require_scope(principal, "agent:write")
    unknown_scopes = sorted(set(request.scopes) - set(principal.permissions.scopes))
    if unknown_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Requested scopes exceed current principal permissions.",
                "scopes": unknown_scopes,
            },
        )

    expires_at = datetime.now(UTC) + timedelta(days=request.expires_in_days)
    token = f"ov_agent_{secrets.token_urlsafe(32)}"
    return TokenCreateResponse(
        token=token,
        name=request.name,
        scopes=request.scopes,
        expires_at=expires_at,
        audit_event={
            "actor": principal.identity_id,
            "action": "agent_token.create",
            "token_name": request.name,
        },
    )
