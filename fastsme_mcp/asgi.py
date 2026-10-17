"""ASGI helpers for securing the remote MCP endpoint."""

from __future__ import annotations

import hmac
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.responses import JSONResponse


ASGIApp = Callable[[dict[str, Any], Callable[..., Awaitable[Any]], Callable[..., Awaitable[Any]]], Awaitable[None]]


class BearerAuthMiddleware:
    """Require a configured static bearer secret for MCP HTTP requests.

    This is an MVP deployment guard. User-level production access should move
    to OAuth 2.1 before write-capable tools are introduced.
    """

    def __init__(self, app: ASGIApp, secret: str | None):
        self.app = app
        self.secret = secret

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http" or not scope.get("path", "").startswith("/mcp") or not self.secret:
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        supplied = headers.get(b"authorization", b"").decode("latin-1")
        expected = f"Bearer {self.secret}"
        if not hmac.compare_digest(supplied, expected):
            response = JSONResponse(
                {"error": "unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
