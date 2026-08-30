"""Fetch a page two ways: raw rendered HTML, then AI-parsed structured JSON.

Run:
    export SCRAPEUNBLOCKER_KEY=your_key_here
    python examples/basic_fetch.py https://example.com
"""

from __future__ import annotations

import json
import sys

from ai_web_access import WebAccessTools


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"

    with WebAccessTools() as tools:
        html = tools.fetch_html(url, max_chars=500)
        print(f"# fetch_html({url}) -> {html['length']} chars (truncated={html['truncated']})")
        print(html["html"])
        print()

        parsed = tools.fetch_parsed(url, rules_hint="page title and any headings")
        print(f"# fetch_parsed({url})")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
