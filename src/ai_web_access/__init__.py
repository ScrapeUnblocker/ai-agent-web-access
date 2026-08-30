"""Reliable, unblocked web access tools for AI agents, powered by ScrapeUnblocker.

This package exposes the same three capabilities as the ``scrapeunblocker-mcp``
server -- fetch rendered HTML, fetch AI-parsed structured JSON, and run a Google
search -- as native Python *tools* you can drop into any LLM tool-calling loop
(OpenAI, Anthropic, LangChain, your own dispatcher).

Typical use::

    from ai_web_access import WebAccessTools, ANTHROPIC_TOOLS, run_tool

    tools = WebAccessTools()          # reads SCRAPEUNBLOCKER_KEY from the env
    result = tools.fetch_html("https://example.com")

Hand ``ANTHROPIC_TOOLS`` / ``OPENAI_TOOLS`` to your model and route the model's
tool calls back through :func:`run_tool`.
"""

from __future__ import annotations

from .schemas import ANTHROPIC_TOOLS, OPENAI_TOOLS, TOOL_SPECS
from .tools import WebAccessError, WebAccessTools, run_tool

__version__ = "0.1.0"

__all__ = [
    "WebAccessTools",
    "WebAccessError",
    "run_tool",
    "TOOL_SPECS",
    "OPENAI_TOOLS",
    "ANTHROPIC_TOOLS",
    "__version__",
]
