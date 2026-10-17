"""Open MCP Inspector and configure the local FastSME server visibly."""

from __future__ import annotations

import argparse

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--hold-ms", type=int, default=600_000)
    args = parser.parse_args()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless)
        page = browser.new_page(viewport={"width": 1440, "height": 960})
        page.goto("http://127.0.0.1:6274", wait_until="domcontentloaded", timeout=10_000)
        page.wait_for_timeout(700)

        if page.get_by_text("fastsme-local", exact=True).count() == 0:
            page.get_by_role("button", name="Add Servers").click()
            page.wait_for_timeout(200)
            page.locator("button").evaluate_all(
                "buttons => buttons.find(button => button.textContent.includes('Add manually')).click()"
            )
            page.get_by_placeholder("my-server").fill("fastsme-local")
            page.locator("label", has_text="Transport").evaluate(
                "(label) => document.getElementById(label.htmlFor).click()"
            )
            page.get_by_role("option", name="streamable-http").click()
            page.get_by_placeholder("https://example.com/mcp").fill("http://127.0.0.1:8000/mcp")
            page.get_by_role("button", name="Add", exact=True).click()
            page.wait_for_timeout(1_000)

        connection = page.get_by_role("switch", name='Connect or disconnect "fastsme-local"')
        if not connection.is_checked():
            connection.check(force=True)
        page.wait_for_timeout(1_500)
        page.get_by_text("Tools", exact=True).first.click()
        page.wait_for_timeout(800)
        page.get_by_text("integration_status", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("button", name="Execute Tool").click()
        page.wait_for_timeout(900)

        print(page.locator("body").inner_text())
        if not args.headless:
            page.wait_for_timeout(args.hold_ms)
        browser.close()


if __name__ == "__main__":
    main()
