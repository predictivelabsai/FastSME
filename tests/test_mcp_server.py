"""MCP contract tests using mocked FastSME product APIs."""

from __future__ import annotations

import asyncio
from datetime import date

import httpx
import pytest
from mcp import Client
from starlette.testclient import TestClient

from fastsme_mcp.asgi import BearerAuthMiddleware
from fastsme_mcp.client import ProductGateway, ProductNotConfiguredError
from fastsme_mcp.config import ProductConfig, Settings
from fastsme_mcp.server import build_server


def settings(configured: bool = True) -> Settings:
    key = "test-key" if configured else None
    base = "https://example.test" if configured else None
    return Settings(
        host="127.0.0.1",
        port=8000,
        public_url="http://localhost:8000/mcp",
        auth_secret=None,
        log_level="INFO",
        crm=ProductConfig("FastCRM", base, key),
        accounts=ProductConfig("FastAccounts", base, key),
        bi=ProductConfig("FastBI", base, key),
    )


def test_gateway_calls_expected_read_only_endpoints():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True, "path": request.url.path})

    transport = httpx.MockTransport(handler)
    gateway = ProductGateway(
        settings(), {"crm": transport, "accounts": transport, "bi": transport}
    )

    assert asyncio.run(gateway.crm.get("/api/customers", {"q": "Acme"})) == {
        "ok": True,
        "path": "/api/customers",
    }
    assert asyncio.run(gateway.accounts.get("/api/invoices/overdue")) == {
        "ok": True,
        "path": "/api/invoices/overdue",
    }
    assert asyncio.run(
        gateway.bi.get(
            "/api/reports/sales-summary",
            {"start_date": date(2026, 1, 1).isoformat()},
        )
    ) == {"ok": True, "path": "/api/reports/sales-summary"}
    assert all(request.headers["Authorization"] == "Bearer test-key" for request in requests)


def test_unconfigured_product_fails_without_network_access():
    gateway = ProductGateway(settings(configured=False))
    with pytest.raises(ProductNotConfiguredError, match="FastCRM is not configured"):
        asyncio.run(gateway.crm.get("/api/customers"))


def test_status_never_exposes_credentials():
    gateway = ProductGateway(settings())
    result = gateway.integration_status()
    assert result == [
        {"product": "FastCRM", "configured": True},
        {"product": "FastAccounts", "configured": True},
        {"product": "FastBI", "configured": True},
    ]
    assert "test-key" not in repr(result)


def test_mcp_lists_and_calls_read_only_tools_in_process():
    async def exercise():
        server = build_server(settings(), ProductGateway(settings()))
        async with Client(server) as client:
            tools = await client.list_tools()
            names = {tool.name for tool in tools.tools}
            assert names == {
                "integration_status",
                "search_customers",
                "list_invoices",
                "list_overdue_invoices",
                "sales_summary",
            }
            assert all(tool.annotations.read_only_hint for tool in tools.tools)
            result = await client.call_tool("integration_status", {})
            assert not result.is_error
            assert result.structured_content["result"][0]["product"] == "FastCRM"

    asyncio.run(exercise())


def test_http_mcp_endpoint_requires_bearer_secret_but_health_stays_public():
    server = build_server(settings(), ProductGateway(settings()))
    app = BearerAuthMiddleware(
        server.streamable_http_app(stateless_http=True, json_response=True),
        "mcp-test-secret",
    )
    with TestClient(app) as client:
        assert client.get("/healthz").json() == {
            "status": "ok",
            "service": "fastsme-mcp",
        }
        response = client.post("/mcp", json={})
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
