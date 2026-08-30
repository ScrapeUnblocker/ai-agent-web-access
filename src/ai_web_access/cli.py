"""Command-line entry point: exercise the web-access tools from a terminal.

Examples::

    ai-web-access fetch https://example.com
    ai-web-access parsed https://example.com --hint "page title"
    ai-web-access search "web scraping api"
    ai-web-access tools --format anthropic
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .schemas import ANTHROPIC_TOOLS, OPENAI_TOOLS, TOOL_SPECS
from .tools import WebAccessTools, run_tool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-web-access",
        description="Reliable, unblocked web access tools for AI agents (ScrapeUnblocker).",
    )
    parser.add_argument(
        "--indent", type=int, default=2, help="JSON indent for output (default: 2)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="Fetch rendered HTML of a URL.")
    p_fetch.add_argument("url")
    p_fetch.add_argument("--country", default=None, help="ISO country code, e.g. us.")
    p_fetch.add_argument("--max-chars", type=int, default=20_000, help="Truncate HTML to N chars.")

    p_parsed = sub.add_parser("parsed", help="Fetch AI-parsed structured JSON.")
    p_parsed.add_argument("url")
    p_parsed.add_argument("--hint", default=None, help="What to extract (rules hint).")
    p_parsed.add_argument("--country", default=None, help="ISO country code.")

    p_search = sub.add_parser("search", help="Run a Google search.")
    p_search.add_argument("query")
    p_search.add_argument("--pages", type=int, default=1, help="Result pages (default 1).")
    p_search.add_argument("--country", default=None, help="ISO country code.")

    p_tools = sub.add_parser("tools", help="Print the tool schemas for your agent.")
    p_tools.add_argument(
        "--format",
        choices=["canonical", "openai", "anthropic"],
        default="canonical",
        help="Schema flavour to print (default: canonical).",
    )

    return parser


def _dispatch(args: argparse.Namespace) -> object:
    if args.command == "tools":
        return {
            "canonical": TOOL_SPECS,
            "openai": OPENAI_TOOLS,
            "anthropic": ANTHROPIC_TOOLS,
        }[args.format]

    tools = WebAccessTools()
    try:
        if args.command == "fetch":
            return run_tool(
                "fetch_html",
                {"url": args.url, "country": args.country, "max_chars": args.max_chars},
                tools,
            )
        if args.command == "parsed":
            return run_tool(
                "fetch_parsed",
                {"url": args.url, "rules_hint": args.hint, "country": args.country},
                tools,
            )
        if args.command == "search":
            return run_tool(
                "web_search",
                {"query": args.query, "pages": args.pages, "country": args.country},
                tools,
            )
    finally:
        tools.close()
    raise AssertionError(f"unhandled command: {args.command}")  # pragma: no cover


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = _dispatch(args)
    print(json.dumps(result, indent=args.indent, ensure_ascii=False))
    # Surface tool-level failures as a non-zero exit for scripting.
    if isinstance(result, dict) and "error" in result:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
