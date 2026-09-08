# ai-agent-web-access

[![CI](https://github.com/ScrapeUnblocker/ai-agent-web-access/actions/workflows/ci.yml/badge.svg)](https://github.com/ScrapeUnblocker/ai-agent-web-access/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Give any AI agent reliable, unblocked web access.** Three drop-in tools —
`fetch_html`, `fetch_parsed`, and `web_search` — that let a language model read
real web pages and search the web without getting blocked, powered by
[ScrapeUnblocker](https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos).

Agents that scrape the web with a bare HTTP client hit CAPTCHAs, bot walls, and
empty pages. This package routes those reads through ScrapeUnblocker's rendering
and unblocking, then hands the model clean HTML, structured JSON, or search
results — as native tool-calling tools you can plug into OpenAI, Anthropic,
LangChain, or your own agent loop.

> Powered by [ScrapeUnblocker](https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos).

## Features

- **The same three capabilities as the official MCP server**, as native Python tools:
  - `fetch_html` — the fully rendered HTML of any URL
  - `fetch_parsed` — AI-parsed structured JSON instead of raw markup
  - `web_search` — Google organic results as JSON
- **Provider-ready schemas** — `OPENAI_TOOLS` and `ANTHROPIC_TOOLS` shaped for each
  API's tool-calling format, plus a provider-neutral `TOOL_SPECS`.
- **A safe dispatcher** — `run_tool()` never raises into your agent loop; failures
  come back as `{"error": {...}}` so the model can read them and recover.
- **A CLI** for quick checks and for dumping the schemas.
- **Built on the official SDK** with automatic retries on transient errors.

## Two ways to use it

### 1. Drop-in MCP server (no code)

If your agent client speaks [MCP](https://modelcontextprotocol.io) (Claude Desktop,
Cursor, and others), you don't need this package at all — just point it at the
official [`scrapeunblocker-mcp`](https://docs.scrapeunblocker.com/sdks/mcp?utm_source=github&utm_medium=integration&utm_campaign=example-repos)
server. Copy [`mcp/claude_desktop_config.json`](mcp/claude_desktop_config.json)
into your client config:

```json
{
  "mcpServers": {
    "scrapeunblocker": {
      "command": "npx",
      "args": ["-y", "scrapeunblocker-mcp"],
      "env": { "SCRAPEUNBLOCKER_KEY": "your_key_here" }
    }
  }
}
```

That exposes `fetch_html`, `fetch_parsed`, and `web_search` to the model directly.

### 2. Python tools (this package)

For agents built on the OpenAI/Anthropic SDKs, LangChain, or a custom loop, use the
identical three tools from Python — see below.

## Install

```bash
pip install .
# or, for development:
pip install -e ".[dev]"
```

Set your API key (get one at
[scrapeunblocker.com](https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos)):

```bash
cp .env.example .env      # then edit, or just export it:
export SCRAPEUNBLOCKER_KEY=your_key_here
```

## Library usage

```python
from ai_web_access import WebAccessTools, ANTHROPIC_TOOLS, run_tool

tools = WebAccessTools()  # reads SCRAPEUNBLOCKER_KEY

# Call a tool directly:
page = tools.fetch_html("https://example.com")
print(page["length"], "chars")

# Or wire the schemas into a model and route its tool calls through run_tool:
#   response = anthropic_client.messages.create(model=..., tools=ANTHROPIC_TOOLS, ...)
#   for block in response.content:
#       if block.type == "tool_use":
#           result = run_tool(block.name, dict(block.input), tools)
```

A full, runnable Anthropic tool-calling loop is in
[`examples/agent_tool_loop.py`](examples/agent_tool_loop.py).

## CLI usage

```bash
ai-web-access fetch  https://example.com
ai-web-access parsed https://example.com --hint "page title"
ai-web-access search "web scraping api"
ai-web-access tools  --format anthropic      # print schemas for your agent
```

### Example output

```console
$ ai-web-access fetch https://example.com --max-chars 120
{
  "url": "https://example.com",
  "html": "<!DOCTYPE html>\n<html lang=\"en\">\n <head>\n  <title>\n   Example Domain\n  </title>\n  <link href=\"data:,\" rel=\"icon\"/>",
  "length": 653,
  "truncated": true
}
```

`fetch_parsed` returns the same envelope with a `page_type`, `source`, and an
extracted `data` object instead of raw HTML.

## Project layout

```
src/ai_web_access/
  __init__.py     package exports + __version__
  tools.py        WebAccessTools + the run_tool dispatcher
  schemas.py      TOOL_SPECS, OPENAI_TOOLS, ANTHROPIC_TOOLS
  cli.py          the ai-web-access command
examples/         basic_fetch, agent_tool_loop, search_to_csv
tests/            offline unit tests (the SDK is mocked)
mcp/              ready-to-use MCP client config
```

## Development

```bash
make install      # editable install with dev deps
make lint         # ruff check
make format       # ruff format
make test         # pytest (fully offline — no API credit spent)
```

Tests mock the SDK, so `make test` runs without a key and without spending credit.

## Links

- Website — https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos
- Documentation — https://docs.scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos
- MCP server — https://docs.scrapeunblocker.com/sdks/mcp?utm_source=github&utm_medium=integration&utm_campaign=example-repos
- Python SDK — https://docs.scrapeunblocker.com/sdks/python?utm_source=github&utm_medium=integration&utm_campaign=example-repos

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 ScrapeUnblocker.
