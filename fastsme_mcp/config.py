"""Environment-backed configuration for the FastSME MCP service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

from dotenv import load_dotenv


load_dotenv()


def _url(name: str) -> str | None:
    value = os.getenv(name, "").strip().rstrip("/")
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{name} must be an absolute HTTP(S) URL")
    return value


@dataclass(frozen=True)
class ProductConfig:
    name: str
    base_url: str | None
    api_key: str | None

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key)


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    public_url: str
    auth_secret: str | None
    log_level: str
    crm: ProductConfig
    accounts: ProductConfig
    bi: ProductConfig

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            host=os.getenv("MCP_HOST", "127.0.0.1"),
            port=int(os.getenv("MCP_PORT", "8000")),
            public_url=os.getenv("MCP_PUBLIC_URL", "http://localhost:8000/mcp"),
            auth_secret=os.getenv("MCP_AUTH_SECRET") or None,
            log_level=os.getenv("MCP_LOG_LEVEL", "INFO").upper(),
            crm=ProductConfig("FastCRM", _url("FASTCRM_API_BASE_URL"), os.getenv("FASTCRM_API_KEY") or None),
            accounts=ProductConfig("FastAccounts", _url("FASTACCOUNTS_API_BASE_URL"), os.getenv("FASTACCOUNTS_API_KEY") or None),
            bi=ProductConfig("FastBI", _url("FASTBI_API_BASE_URL"), os.getenv("FASTBI_API_KEY") or None),
        )
