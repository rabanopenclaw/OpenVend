from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Header, HTTPException, status


def parse_scopes(header_value: str | None) -> set[str]:
    if not header_value:
        return set()
    return {
        scope.strip()
        for chunk in header_value.split(",")
        for scope in chunk.split()
        if scope.strip()
    }


def require_scope(scope: str) -> Callable[[str | None], None]:
    def dependency(
        scopes_header: Annotated[str | None, Header(alias="X-OpenVend-Scopes")] = None,
    ) -> None:
        scopes = parse_scopes(scopes_header)
        if not scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization scopes.",
            )
        if scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required scope is missing: {scope}",
            )

    return dependency


def actor_id(
    actor_header: Annotated[str | None, Header(alias="X-OpenVend-Actor-Id")] = None,
) -> str:
    return actor_header or "unknown"
