"""Wire the web-access tools into an Anthropic tool-calling loop.

This is the whole point of the package: give a model reliable web access with a few
lines of glue. The model decides which tool to call; ``run_tool`` executes it against
ScrapeUnblocker and feeds the JSON result back.

Requires the Anthropic SDK and a key:
    pip install anthropic
    export ANTHROPIC_API_KEY=...            # your Anthropic key
    export SCRAPEUNBLOCKER_KEY=...          # your ScrapeUnblocker key
    python examples/agent_tool_loop.py "What does example.com say?"

If you don't have an Anthropic key handy, run `python examples/basic_fetch.py`
instead -- it calls the same tools directly without a model.
"""

from __future__ import annotations

import sys

from ai_web_access import ANTHROPIC_TOOLS, WebAccessTools, run_tool

MODEL = "claude-opus-4-8"


def main() -> None:
    try:
        import anthropic
    except ImportError:
        sys.exit("This example needs the Anthropic SDK: pip install anthropic")

    question = sys.argv[1] if len(sys.argv) > 1 else "Summarise https://example.com"

    client = anthropic.Anthropic()
    tools = WebAccessTools()
    messages = [{"role": "user", "content": question}]

    try:
        while True:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                tools=ANTHROPIC_TOOLS,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                text = "".join(b.text for b in response.content if b.type == "text")
                print(text)
                return

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                print(f"[tool] {block.name}({block.input})")
                result = run_tool(block.name, dict(block.input), tools)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": _stringify(result),
                    }
                )
            messages.append({"role": "user", "content": tool_results})
    finally:
        tools.close()


def _stringify(result: object) -> str:
    import json

    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
