"""Schemas stay consistent across the canonical / OpenAI / Anthropic shapes."""

from __future__ import annotations

from ai_web_access import ANTHROPIC_TOOLS, OPENAI_TOOLS, TOOL_SPECS

EXPECTED_NAMES = {"fetch_html", "fetch_parsed", "web_search"}


def test_canonical_has_three_tools():
    names = {spec["name"] for spec in TOOL_SPECS}
    assert names == EXPECTED_NAMES


def test_every_spec_has_description_and_required():
    for spec in TOOL_SPECS:
        assert spec["description"].strip()
        assert spec["parameters"]["type"] == "object"
        assert "required" in spec["parameters"]


def test_openai_shape():
    assert {t["function"]["name"] for t in OPENAI_TOOLS} == EXPECTED_NAMES
    for tool in OPENAI_TOOLS:
        assert tool["type"] == "function"
        assert "parameters" in tool["function"]


def test_anthropic_shape():
    assert {t["name"] for t in ANTHROPIC_TOOLS} == EXPECTED_NAMES
    for tool in ANTHROPIC_TOOLS:
        assert "input_schema" in tool
        assert tool["input_schema"]["type"] == "object"


def test_url_is_required_where_expected():
    by_name = {s["name"]: s for s in TOOL_SPECS}
    assert by_name["fetch_html"]["parameters"]["required"] == ["url"]
    assert by_name["fetch_parsed"]["parameters"]["required"] == ["url"]
    assert by_name["web_search"]["parameters"]["required"] == ["query"]
