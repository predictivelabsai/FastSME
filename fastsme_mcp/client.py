"""Small, defensive HTTP clients for FastSME product APIs."""

from __future__ import annotations

from typing import Any

import httpx

from .config import ProductConfig, Settings


class ProductNotConfiguredError(RuntimeError):
    """Raised when an MCP tool is called before its product is configured."""


class ProductAPIError(RuntimeError):
    """A safe error that does not expose upstream credentials or response bodies."""


class ProductClient:
    def __init__(self, config: ProductConfig, transport: httpx.AsyncBaseTransport | None = None):
        self.config = config
        self.transport = transport

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if not self.config.configured:
            raise ProductNotConfiguredError(
                f"{self.config.name} is not configured. Add its API base URL and API key to .env."
            )
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Accept": "application/json",
            "User-Agent": "FastSME-MCP/0.1",
        }
        try:
            async with httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                timeout=20,
                transport=self.transport,
                follow_redirects=False,
            ) as client:
                response = await client.get(path, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise ProductAPIError(
                f"{self.config.name} returned HTTP {exc.response.status_code}."
            ) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise ProductAPIError(f"Could not read data from {self.config.name}.") from exc


class ProductGateway:
    def __init__(
        self,
        settings: Settings,
        transports: dict[str, httpx.AsyncBaseTransport] | None = None,
    ):
        transports = transports or {}
        self.crm = ProductClient(settings.crm, transports.get("crm"))
        self.accounts = ProductClient(settings.accounts, transports.get("accounts"))
        self.bi = ProductClient(settings.bi, transports.get("bi"))

    def integration_status(self) -> list[dict[str, Any]]:
        return [
            {"product": client.config.name, "configured": client.config.configured}
            for client in (self.crm, self.accounts, self.bi)
        ]
