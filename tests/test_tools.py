"""Unit tests for WebAccessTools and run_tool. The SDK client is mocked -- no API
calls, no credit spent."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from scrapeunblocker import BlockedError

from ai_web_access import WebAccessTools, run_tool
from ai_web_access.tools import WebAccessError


class FakeClient:
    """Records calls and returns canned SDK-shaped responses."""

    def __init__(self):
        self.calls = []

    def get_page_source(self, url, *, proxy_country=None):
        self.calls.append(("get_page_source", url, proxy_country))
        return "<html>" + "x" * 100 + "</html>"

    def get_parsed(self, url, *, rules_hint=None, proxy_country=None):
        self.calls.append(("get_parsed", url, rules_hint, proxy_country))
        return SimpleNamespace(page_type="article", source="cache", data={"title": "Hi"})

    def serp(self, keyword, *, pages_to_check=1, proxy_country=None):
        self.calls.append(("serp", keyword, pages_to_check, proxy_country))
        return {
            "organic": [
                {"position": 1, "title": "First", "url": "https://a.example"},
                {"position": 2, "title": "Second", "url": "https://b.example"},
                "junk-non-dict",
            ]
        }

    def close(self):
        self.calls.append(("close",))


@pytest.fixture
def tools():
    return WebAccessTools(client=FakeClient())


def test_fetch_html_truncates_and_reports_length(tools):
    out = tools.fetch_html("https://x.example", max_chars=10)
    assert out["url"] == "https://x.example"
    assert out["length"] == len("<html>" + "x" * 100 + "</html>")
    assert out["truncated"] is True
    assert len(out["html"]) == 10


def test_fetch_html_passes_country(tools):
    tools.fetch_html("https://x.example", country="de")
    assert tools._client.calls[0] == ("get_page_source", "https://x.example", "de")


def test_fetch_parsed_shape(tools):
    out = tools.fetch_parsed("https://x.example", rules_hint="title")
    assert out == {
        "url": "https://x.example",
        "page_type": "article",
        "source": "cache",
        "data": {"title": "Hi"},
    }
    assert tools._client.calls[0] == ("get_parsed", "https://x.example", "title", None)


def test_web_search_filters_non_dicts_and_shapes_results(tools):
    out = tools.web_search("python", pages=2)
    assert out["query"] == "python"
    assert out["results"] == [
        {"position": 1, "title": "First", "url": "https://a.example"},
        {"position": 2, "title": "Second", "url": "https://b.example"},
    ]
    assert tools._client.calls[0] == ("serp", "python", 2, None)


def test_web_search_rejects_bad_pages(tools):
    with pytest.raises(WebAccessError):
        tools.web_search("python", pages=0)


def test_context_manager_closes(tools):
    with tools as t:
        t.fetch_html("https://x.example")
    assert ("close",) in tools._client.calls


def test_run_tool_unknown_tool(tools):
    out = run_tool("nope", {}, tools)
    assert out["error"]["type"] == "UnknownTool"


def test_run_tool_bad_arguments(tools):
    out = run_tool("fetch_html", {"not_a_param": 1}, tools)
    assert out["error"]["type"] == "BadArguments"


def test_run_tool_catches_sdk_error(tools):
    def boom(*_a, **_k):
        raise BlockedError("blocked by captcha", status_code=403)

    tools._client.serp = boom
    out = run_tool("web_search", {"query": "x"}, tools)
    assert out["error"]["type"] == "BlockedError"
    assert "captcha" in out["error"]["message"]


def test_run_tool_success_passthrough(tools):
    out = run_tool("fetch_parsed", {"url": "https://x.example"}, tools)
    assert out["page_type"] == "article"
