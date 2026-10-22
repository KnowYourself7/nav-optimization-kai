#!/usr/bin/env python3
"""Look up US monthly search volume for label candidates through the DataForSEO REST API.

Usage:
    python3 scripts/search_volume.py --keywords work/label_candidates.txt --out work/search_volume.csv

The keywords file holds one keyword per line. Credentials come from the
environment variables DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD. The script never
prints them. Use --location-code and --language-code for another market.
Exit code 2 when credentials or the keywords file are missing, 1 when the API
returns an error, else 0.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from _common import emit, write_csv

ENDPOINT = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
# DataForSEO accepts up to 1000 keywords per request. 700 leaves room for long labels.
BATCH_SIZE = 700
# A live request normally answers within a few seconds. 60 covers a slow queue.
TIMEOUT_SECONDS = 60


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keywords", required=True, help="text file, one keyword per line")
    parser.add_argument("--out", required=True, help="CSV to write")
    parser.add_argument("--location-code", type=int, default=2840, help="DataForSEO location code, 2840 is the United States")
    parser.add_argument("--language-code", default="en")
    args = parser.parse_args()

    login = os.environ.get("DATAFORSEO_LOGIN")
    password = os.environ.get("DATAFORSEO_PASSWORD")
    if not login or not password:
        emit({"error": "DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD are not set. Use the MCP tool or export them, then run again."}, 2)

    keywords_path = Path(args.keywords)
    if not keywords_path.exists():
        emit({"error": f"keywords file not found: {keywords_path}"}, 2)
    keywords = []
    for line in keywords_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text and text not in keywords:
            keywords.append(text)
    if not keywords:
        emit({"error": "the keywords file is empty"}, 2)

    auth = base64.b64encode(f"{login}:{password}".encode()).decode()
    rows = []
    cost = 0.0
    for start in range(0, len(keywords), BATCH_SIZE):
        batch = keywords[start:start + BATCH_SIZE]
        body = json.dumps([{"keywords": batch, "location_code": args.location_code, "language_code": args.language_code}]).encode()
        request = urllib.request.Request(ENDPOINT, data=body, headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as error:
            emit({"error": f"HTTP {error.code} from DataForSEO", "hint": "a 401 means wrong credentials, a 402 means no balance"}, 1)
        except (urllib.error.URLError, TimeoutError) as error:
            emit({"error": f"network error: {error}"}, 1)
        task = payload.get("tasks", [{}])[0]
        if task.get("status_code") != 20000:
            emit({"error": task.get("status_message", "unknown task error"), "status_code": task.get("status_code")}, 1)
        cost += float(payload.get("cost") or 0)
        for result in task.get("result") or []:
            rows.append({
                "keyword": result.get("keyword"),
                "search_volume": result.get("search_volume") if result.get("search_volume") is not None else "no data",
                "competition": result.get("competition") or "",
                "cpc": result.get("cpc") or "",
            })

    rows.sort(key=lambda r: -(r["search_volume"] if isinstance(r["search_volume"], int) else -1))
    out = Path(args.out)
    write_csv(out, rows, ["keyword", "search_volume", "competition", "cpc"])
    emit({"keywords": len(keywords), "rows": len(rows), "cost_usd": round(cost, 4), "output": str(out)})


if __name__ == "__main__":
    main()
