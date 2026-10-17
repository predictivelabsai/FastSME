# FastSME

The landing site for **FastSME** — an open-source platform bringing enterprise-grade software to SMEs and SMBs globally at affordable prices.

FastSME is operated by Exroad Fintech Ltd and the source is published at [github.com/predictivelabsai](https://github.com/predictivelabsai).

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The app listens on `http://localhost:5001` by default and honours the `PORT` environment variable.

## Tests

```bash
pip install pytest playwright
python -m playwright install chromium
python -m pytest tests/test_pages.py -v
```

Browser artifacts are written to `output/playwright/`.

## MCP server (early MVP)

The repository also contains an initial read-only MCP service for connecting
AI clients to FastCRM, FastAccounts and FastBI. Copy the MCP variables from
`.env.example` into the git-ignored `.env`, then run:

```bash
python mcp_main.py
```

The Streamable HTTP endpoint is `http://localhost:8000/mcp` and its health
check is `http://localhost:8000/healthz`. When `MCP_AUTH_SECRET` is set, MCP
requests must include `Authorization: Bearer <secret>`. Product tools remain
unavailable until the matching API base URL and key are configured.

Current tools are read-only: integration status, CRM customer search,
Accounts invoice lookup/overdue invoices, and a BI sales summary. The API
paths are initial adapter contracts and must be checked against each product's
actual API before enabling a live connection.

## Languages

The public site is available in English, Estonian, German, French, Swedish,
Latvian, Norwegian, Danish, Polish, Dutch, Finnish and Lithuanian. The first
visit follows the browser's supported language preference; a selection from
the top navigation is stored in the signed session and preserves the current
route.

Checked-in catalogues live in `content/locales/`. Validate that every public
source string is translated with:

```bash
python scripts/update_i18n.py
```

Maintainers can generate missing catalogue entries with `--translate`. This is
an explicit maintenance command that sends only public English site copy to the
translation service; deployed requests never call an external translator.

## Docker

```bash
docker build -t fastsme .
docker run --rm -p 5001:5001 fastsme
curl http://localhost:5001/healthz
```

See [DEPLOY.md](DEPLOY.md) for the Coolify and CI/CD setup.

## Structure

- `app.py` — routes, redirects and page composition
- `components.py` — shared layout and design system
- `content/products.py` — grouped Fast* product portfolio
- `content/clients.py` — selected client experience
- `content/partners.py` — linked integration-partner profiles and logos
- `content/team.py` — core team and advisory board
- `static/` — CSS and favicon

## Legal

Exroad Fintech Ltd, trading as FastSME<br>
Company number 11914994<br>
155 Minories Street, Flat 275, London, United Kingdom, EC3N 1AD<br>
Contact: info@fastsme.com
