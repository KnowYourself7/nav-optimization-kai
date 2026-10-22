"""Shared helpers for the nav-optimization scripts.

Every script prints a JSON report to stdout and uses the exit codes:
0 ok, 1 a check failed, 2 a required input is missing or unreadable.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# A locale prefix such as /de/ or /zh-tw/ before the real path.
LOCALE_PREFIX = re.compile(r"^/[a-z]{2}(?:-[a-z]{2})?(?=/)")


def emit(report: dict, exit_code: int = 0) -> None:
    """Print the report as JSON and exit."""
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(exit_code)


def normalize_path(value: str) -> str:
    """Turn a URL or a path into a site-relative path without query or locale prefix."""
    value = (value or "").strip()
    if not value:
        return ""
    if "://" in value:
        value = urlparse(value).path
    value = value.split("?")[0].split("#")[0]
    if not value.startswith("/"):
        value = "/" + value
    value = LOCALE_PREFIX.sub("", value)
    if len(value) > 1 and value.endswith("/"):
        value = value[:-1]
    return value


def read_csv_rows(path: Path) -> list[dict]:
    """Read a CSV with or without a BOM and skip comment lines that start with #.

    GA4 exports start with comment lines. Search Console exports do not.
    """
    text = path.read_text(encoding="utf-8-sig")
    lines = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
    return list(csv.DictReader(lines))


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    """Write rows as UTF-8 with BOM so that Excel opens the file correctly."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def to_int(value) -> int | None:
    """Parse numbers like '1,234' or '1234.0'. Return None for blanks."""
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if text == "" or text.lower() in {"na", "n/a", "none", "no data"}:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def find_column(headers: list[str], candidates: list[str]) -> str | None:
    """Return the first header whose lowercase text contains one of the candidates."""
    lowered = {header: header.lower() for header in headers}
    for candidate in candidates:
        for header, low in lowered.items():
            if candidate in low:
                return header
    return None


def load_menu(path: Path) -> dict:
    """Load a menu JSON file in the schema from references/mockup.md."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "items" not in data:
        raise ValueError(f"{path} must be an object with an 'items' list")
    return data


def iterate_menu(menu: dict):
    """Yield (level, top_label, group_title, label, href, node) for every menu entry."""
    for top in menu.get("items", []):
        yield 1, top.get("label", ""), "", top.get("label", ""), top.get("href", ""), top
        for col in top.get("cols", []) or []:
            if col.get("href"):
                yield 2, top.get("label", ""), col.get("title", ""), col.get("title", ""), col.get("href", ""), col
            for item in col.get("items", []) or []:
                yield 3, top.get("label", ""), col.get("title", ""), item.get("label", ""), item.get("href", ""), item
            article = col.get("article")
            if article:
                yield 3, top.get("label", ""), col.get("title", ""), article.get("label", ""), article.get("href", ""), article
        article = top.get("article")
        if article:
            yield 2, top.get("label", ""), "", article.get("label", ""), article.get("href", ""), article
