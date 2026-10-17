"""Read-only MCP tools that expose the first FastSME product integrations."""

from __future__ import annotations

from datetime import date
from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse

from .client import ProductGateway
from .config import Settings


READ_ONLY = ToolAnnotations(read_only_hint=True, idempotent_hint=True, open_world_hint=False)


def build_server(settings: Settings | None = None, gateway: ProductGateway | None = None) -> MCPServer:
    settings = settings or Settings.from_env()
    gateway = gateway or ProductGateway(settings)
    mcp = MCPServer(
        "FastSME",
        instructions=(
            "Use these read-only tools to retrieve business data from the authenticated "
            "user's FastSME products. Never claim that an integration is available when "
            "integration_status reports it as unconfigured."
        ),
    )

    @mcp.custom_route("/healthz", methods=["GET"])
    async def healthz(request: Request) -> JSONResponse:
        """Unauthenticated infrastructure health check with no private data."""
        return JSONResponse({"status": "ok", "service": "fastsme-mcp"})

    @mcp.tool(title="FastSME integration status", annotations=READ_ONLY)
    def integration_status() -> list[dict[str, Any]]:
        """Show which initial FastSME product connections are configured."""
        return gateway.integration_status()

    @mcp.tool(title="Search customers", annotations=READ_ONLY)
    async def search_customers(query: str = "", limit: int = 20) -> Any:
        """Search customer records in FastCRM by name, email, or company."""
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        return await gateway.crm.get("/api/customers", {"q": query, "limit": limit})

    @mcp.tool(title="List invoices", annotations=READ_ONLY)
    async def list_invoices(
        status: str = "all", customer_id: str | None = None, limit: int = 20
    ) -> Any:
        """List invoices from FastAccounts, optionally filtered by status or customer."""
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        params: dict[str, Any] = {"status": status, "limit": limit}
        if customer_id:
            params["customer_id"] = customer_id
        return await gateway.accounts.get("/api/invoices", params)

    @mcp.tool(title="List overdue invoices", annotations=READ_ONLY)
    async def list_overdue_invoices(as_of: date | None = None, limit: int = 20) -> Any:
        """Return unpaid FastAccounts invoices that are overdue as of a given date."""
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        return await gateway.accounts.get(
            "/api/invoices/overdue",
            {"as_of": (as_of or date.today()).isoformat(), "limit": limit},
        )

    @mcp.tool(title="Sales summary", annotations=READ_ONLY)
    async def sales_summary(start_date: date, end_date: date) -> Any:
        """Read the FastBI sales summary for an inclusive date range."""
        if end_date < start_date:
            raise ValueError("end_date must be on or after start_date")
        return await gateway.bi.get(
            "/api/reports/sales-summary",
            {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
        )

    return mcp


mcp = build_server()
