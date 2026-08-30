"""Tool schemas for the three web-access capabilities.

``TOOL_SPECS`` is the canonical, provider-neutral description. ``OPENAI_TOOLS`` and
``ANTHROPIC_TOOLS`` are the same three tools shaped for each provider's tool-calling
API, so you can hand them straight to ``client.chat.completions.create`` /
``client.messages.create``.
"""

from __future__ import annotations

from typing import Any

# Canonical specs: name, description, and a JSON Schema for the arguments.
TOOL_SPECS: list[dict[str, Any]] = [
    {
        "name": "fetch_html",
        "description": (
            "Fetch the fully rendered HTML of any URL, bypassing bot protection. "
            "Use this to read a specific web page an agent already has the URL for."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Absolute URL to fetch."},
                "country": {
                    "type": "string",
                    "description": "Optional ISO-3166 country code to route through, e.g. 'us'.",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "fetch_parsed",
        "description": (
            "Fetch a page and return AI-parsed structured JSON instead of raw HTML. "
            "Best when you want clean fields (e.g. a product's title and price) rather "
            "than the whole document."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Absolute URL to parse."},
                "rules_hint": {
                    "type": "string",
                    "description": "What to extract, in words, e.g. 'article title and author'.",
                },
                "country": {
                    "type": "string",
                    "description": "Optional ISO-3166 country code to route the request through.",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "web_search",
        "description": (
            "Run a Google search and return organic results as JSON. Use this when the "
            "agent needs to discover URLs or find current information, not read one page."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."},
                "pages": {
                    "type": "integer",
                    "description": "How many result pages to fetch (default 1).",
                    "minimum": 1,
                },
                "country": {
                    "type": "string",
                    "description": "Optional ISO-3166 country code to search from.",
                },
            },
            "required": ["query"],
        },
    },
]


def _openai_tool(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": spec["name"],
            "description": spec["description"],
            "parameters": spec["parameters"],
        },
    }


def _anthropic_tool(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": spec["name"],
        "description": spec["description"],
        "input_schema": spec["parameters"],
    }


OPENAI_TOOLS: list[dict[str, Any]] = [_openai_tool(s) for s in TOOL_SPECS]
ANTHROPIC_TOOLS: list[dict[str, Any]] = [_anthropic_tool(s) for s in TOOL_SPECS]
