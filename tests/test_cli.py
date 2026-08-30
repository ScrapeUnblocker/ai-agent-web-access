"""CLI argument parsing and dispatch, with the tools layer mocked."""

from __future__ import annotations

import json

import pytest

from ai_web_access import cli


def test_parser_requires_subcommand():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args([])


def test_fetch_args_parse():
    args = cli.build_parser().parse_args(["fetch", "https://x.example", "--country", "us"])
    assert args.command == "fetch"
    assert args.url == "https://x.example"
    assert args.country == "us"


def test_tools_subcommand_prints_schema(capsys):
    rc = cli.main(["tools", "--format", "anthropic"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert {t["name"] for t in payload} == {"fetch_html", "fetch_parsed", "web_search"}


def test_search_dispatch_uses_tools(monkeypatch, capsys):
    captured = {}

    class FakeTools:
        def __init__(self, *a, **k):
            pass

        def web_search(self, query, *, pages=1, country=None):
            captured["query"] = query
            captured["pages"] = pages
            return {"query": query, "results": [{"position": 1, "title": "t", "url": "u"}]}

        def close(self):
            pass

    monkeypatch.setattr(cli, "WebAccessTools", FakeTools)
    rc = cli.main(["search", "hello", "--pages", "2"])
    assert rc == 0
    assert captured == {"query": "hello", "pages": 2}
    out = json.loads(capsys.readouterr().out)
    assert out["results"][0]["url"] == "u"


def test_error_result_exits_nonzero(monkeypatch, capsys):
    class FakeTools:
        def __init__(self, *a, **k):
            pass

        def fetch_html(self, *a, **k):
            raise AssertionError("should not be called directly")

        def close(self):
            pass

    # run_tool receives an unknown tool -> error dict -> exit 1
    monkeypatch.setattr(cli, "WebAccessTools", FakeTools)
    monkeypatch.setattr(cli, "run_tool", lambda *a, **k: {"error": {"type": "X", "message": "m"}})
    rc = cli.main(["fetch", "https://x.example"])
    assert rc == 1
