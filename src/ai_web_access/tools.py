"""The web-access tools an AI agent can call, backed by the ScrapeUnblocker SDK.

Each public method returns a plain, JSON-serialisable ``dict`` so the result can be
handed straight back to a language model as a tool result. Errors are never raised
out of :func:`run_tool`; they are converted into an ``{"error": ...}`` payload so a
misbehaving page cannot crash the agent loop.
"""

from __future__ import annotations

from typing import Any

from scrapeunblocker import Client, ScrapeUnblockerError

# Upper bound on how much HTML we hand back to a model by default. Full pages can be
# hundreds of KB; that is rarely useful as a tool result and burns context tokens.
DEFAULT_HTML_LIMIT = 20_000


class WebAccessError(Exception):
    """Raised when a tool is called with arguments it cannot satisfy."""


class WebAccessTools:
    """A small, agent-friendly facade over the ScrapeUnblocker client.

    Parameters
    ----------
    api_key:
        Your ScrapeUnblocker key. If omitted, the SDK reads ``SCRAPEUNBLOCKER_KEY``
        from the environment.
    client:
        A pre-built :class:`scrapeunblocker.Client` (mainly for testing). When given,
        ``api_key``/``timeout``/``max_retries`` are ignored.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        client: Client | None = None,
        timeout: float = 180.0,
        max_retries: int = 2,
    ) -> None:
        self._client = client or Client(api_key=api_key, timeout=timeout, max_retries=max_retries)

    # -- individual tools ---------------------------------------------------

    def fetch_html(
        self,
        url: str,
        *,
        country: str | None = None,
        max_chars: int = DEFAULT_HTML_LIMIT,
    ) -> dict[str, Any]:
        """Fetch the fully rendered HTML of ``url``.

        Returns a dict with ``url``, ``html`` (possibly truncated), ``length`` (the
        full length before truncation) and ``truncated``.
        """
        html = self._client.get_page_source(url, proxy_country=country)
        html = html or ""
        full_length = len(html)
        truncated = full_length > max_chars
        return {
            "url": url,
            "html": html[:max_chars],
            "length": full_length,
            "truncated": truncated,
        }

    def fetch_parsed(
        self,
        url: str,
        *,
        rules_hint: str | None = None,
        country: str | None = None,
    ) -> dict[str, Any]:
        """Fetch ``url`` and return AI-parsed structured JSON.

        ``rules_hint`` is a natural-language nudge about what to extract (for
        example ``"product title and price"``). Returns ``url``, ``page_type``,
        ``source`` and the extracted ``data`` dict.
        """
        page = self._client.get_parsed(url, rules_hint=rules_hint, proxy_country=country)
        return {
            "url": url,
            "page_type": page.page_type,
            "source": page.source,
            "data": page.data,
        }

    def web_search(
        self,
        query: str,
        *,
        pages: int = 1,
        country: str | None = None,
    ) -> dict[str, Any]:
        """Run a Google search and return organic results as JSON.

        Returns ``query`` and a ``results`` list of ``{position, title, url}``.
        """
        if pages < 1:
            raise WebAccessError("pages must be >= 1")
        raw = self._client.serp(query, pages_to_check=pages, proxy_country=country)
        organic = raw.get("organic", []) if isinstance(raw, dict) else []
        results = [
            {
                "position": item.get("position"),
                "title": item.get("title"),
                "url": item.get("url"),
            }
            for item in organic
            if isinstance(item, dict)
        ]
        return {"query": query, "results": results}

    def close(self) -> None:
        """Release the underlying HTTP client."""
        close = getattr(self._client, "close", None)
        if callable(close):
            close()

    def __enter__(self) -> WebAccessTools:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


# -- dispatch ---------------------------------------------------------------

# Maps the tool name a model emits to the WebAccessTools method that serves it.
_DISPATCH = {
    "fetch_html": "fetch_html",
    "fetch_parsed": "fetch_parsed",
    "web_search": "web_search",
}


def run_tool(name: str, arguments: dict[str, Any], tools: WebAccessTools) -> dict[str, Any]:
    """Execute the tool ``name`` with ``arguments`` and return a JSON-safe result.

    This is the function you wire a model's tool calls into. Any ScrapeUnblocker or
    argument error is caught and returned as ``{"error": {"type", "message"}}`` so
    the agent can read the failure and decide what to do next, rather than crashing.
    """
    method_name = _DISPATCH.get(name)
    if method_name is None:
        return {"error": {"type": "UnknownTool", "message": f"No such tool: {name!r}"}}
    method = getattr(tools, method_name)
    try:
        return method(**arguments)
    except TypeError as exc:  # bad/missing arguments from the model
        return {"error": {"type": "BadArguments", "message": str(exc)}}
    except WebAccessError as exc:
        return {"error": {"type": "BadArguments", "message": str(exc)}}
    except ScrapeUnblockerError as exc:
        return {"error": {"type": type(exc).__name__, "message": str(exc)}}
