"""Run a Google search through the web_search tool and write results to CSV.

Run:
    export SCRAPEUNBLOCKER_KEY=your_key_here
    python examples/search_to_csv.py "web scraping api" results.csv
"""

from __future__ import annotations

import csv
import sys

from ai_web_access import WebAccessTools


def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else "web scraping api"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "results.csv"

    with WebAccessTools() as tools:
        payload = tools.web_search(query, pages=1)

    results = payload["results"]
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["position", "title", "url"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Wrote {len(results)} results for {query!r} to {out_path}")


if __name__ == "__main__":
    main()
