"""Entrypoint for the FastSME remote MCP server."""

import uvicorn

from fastsme_mcp.asgi import BearerAuthMiddleware
from fastsme_mcp.config import Settings
from fastsme_mcp.server import mcp


settings = Settings.from_env()
app = BearerAuthMiddleware(
    mcp.streamable_http_app(
        host=settings.host,
        stateless_http=True,
        json_response=True,
    ),
    settings.auth_secret,
)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
