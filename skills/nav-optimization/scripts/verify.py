#!/usr/bin/env python3
"""Verify the deliverables of a nav-optimization run before STOP 3.

Usage:
    python3 scripts/verify.py --workdir <work-directory> [--lang zh|en]

Checks:
  1. deliver/changes.csv exists, has the 14 columns, and every active row has
     href, change_type and reason.
  2. every href in changes.csv and deliver/menu_proposed.json is a known page:
     it appears in inputs/product_counts.csv, work/menu_current.json, the
     exports, or inputs/known_pages.txt.
  3. the proposed menu has at most 10 top-level items and at most 10 items per
     column, and no entry with fewer than 10 products.
  4. deliver/proposal.md has the required headings for the language.
  5. no file in deliver/ contains a credential-like string.
Exit code 1 when any check fails, 2 when a deliverable is missing.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from _common import emit, find_column, iterate_menu, load_menu, normalize_path, read_csv_rows, to_int

COLUMNS = [
    "top_level", "group", "item", "old_location", "old_label", "new_label", "href",
    "product_count", "gsc_clicks", "ga4_views", "ga4_key_events", "search_volume", "change_type", "reason",
]
CHANGE_TYPES = {"keep", "rename", "move", "promote", "add", "remove", "merge", "retarget", "footer"}
MIN_PRODUCTS = 10
MAX_TOP_LEVEL = 10
MAX_PER_COLUMN = 10

REQUIRED_HEADINGS = {
    "zh": ["一页摘要", "总览", "需要客户决定", "实施与验证"],
    "en": ["One-page summary", "Overview", "Client decisions", "Implementation and verification"],
}
# Patterns that look like secrets. The DataForSEO login is an email, so email-like
# strings next to the word dataforseo are also flagged.
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|password|passwd|secret|token)\s*[:=]\s*\S{6,}"),
    re.compile(r"(?i)dataforseo[^\n]{0,40}@"),
    re.compile(r"Basic [A-Za-z0-9+/=]{20,}"),
]


def known_pages(workdir: Path) -> set[str]:
    pages: set[str] = set()
    counts = workdir / "inputs" / "product_counts.csv"
    if counts.exists():
        rows = read_csv_rows(counts)
        col = find_column(list(rows[0].keys()), ["url", "path", "网址"]) if rows else None
        pages.update(normalize_path(r[col]) for r in rows if col)
    for name, cols in (("gsc_pages.csv", ["top pages", "page", "网页", "页面"]), ("ga4_pages.csv", ["page path", "网页路径", "page"])):
        path = workdir / "inputs" / name
        if path.exists():
            rows = read_csv_rows(path)
            col = find_column(list(rows[0].keys()), cols) if rows else None
            pages.update(normalize_path(r[col]) for r in rows if col)
    current = workdir / "work" / "menu_current.json"
    if current.exists():
        pages.update(normalize_path(href) for _, _, _, _, href, _ in iterate_menu(load_menu(current)) if href)
        for col in load_menu(current).get("footer", []) or []:
            pages.update(normalize_path(i.get("href", "")) for i in col.get("items", []))
    extra = workdir / "inputs" / "known_pages.txt"
    if extra.exists():
        pages.update(normalize_path(line) for line in extra.read_text(encoding="utf-8").splitlines() if line.strip())
    pages.discard("")
    return pages


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    args = parser.parse_args()
    workdir = Path(args.workdir).expanduser().resolve()
    deliver = workdir / "deliver"

    missing = [name for name in ("changes.csv", "menu_proposed.json", "proposal.md", "README.md", "mockup.html") if not (deliver / name).exists()]
    if missing:
        emit({"error": "deliverables missing", "missing": missing}, 2)

    failures: list[str] = []
    warnings: list[str] = []
    pages = known_pages(workdir)

    # 1. change table shape
    rows = read_csv_rows(deliver / "changes.csv")
    headers = list(rows[0].keys()) if rows else []
    for column in COLUMNS:
        if column not in headers:
            failures.append(f"changes.csv lacks column {column}")
    counts_by_href: dict[str, int | None] = {}
    for index, row in enumerate(rows, start=2):
        change_type = (row.get("change_type") or "").strip()
        if change_type not in CHANGE_TYPES:
            failures.append(f"changes.csv row {index}: change_type '{change_type}' is not one of {sorted(CHANGE_TYPES)}")
        if not (row.get("reason") or "").strip():
            failures.append(f"changes.csv row {index}: reason is empty")
        href = normalize_path(row.get("href") or "")
        if change_type != "remove":
            if not href:
                failures.append(f"changes.csv row {index}: href is empty")
            elif pages and href not in pages:
                failures.append(f"changes.csv row {index}: href {href} is not a known page")
        count = to_int(row.get("product_count"))
        counts_by_href[href] = count
        if change_type in {"add", "promote", "keep", "rename", "move", "retarget"} and count is not None and count < MIN_PRODUCTS:
            failures.append(f"changes.csv row {index}: {href} has {count} products, below {MIN_PRODUCTS}")

    # 2 and 3. proposed menu
    menu = load_menu(deliver / "menu_proposed.json")
    if len(menu.get("items", [])) > MAX_TOP_LEVEL:
        failures.append(f"menu_proposed.json has {len(menu['items'])} top-level items, the limit is {MAX_TOP_LEVEL}")
    for top in menu.get("items", []):
        for col in top.get("cols") or []:
            if len(col.get("items") or []) > MAX_PER_COLUMN:
                failures.append(f"column '{col.get('title')}' under '{top.get('label')}' has {len(col['items'])} items, the limit is {MAX_PER_COLUMN}")
    for _, _, _, label, href, node in iterate_menu(menu):
        path = normalize_path(href)
        if pages and path and path not in pages:
            failures.append(f"menu_proposed.json: {label} points to unknown page {path}")
        count = node.get("count")
        if isinstance(count, int) and count < MIN_PRODUCTS:
            failures.append(f"menu_proposed.json: {label} has {count} products, below {MIN_PRODUCTS}")

    # 4. proposal headings
    proposal = (deliver / "proposal.md").read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS[args.lang]:
        if heading not in proposal:
            failures.append(f"proposal.md lacks the heading '{heading}'")
    if "## " not in proposal:
        failures.append("proposal.md has no sections")

    # 5. secrets
    for path in deliver.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".csv", ".html", ".json", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    failures.append(f"{path.relative_to(workdir)} contains a credential-like string ({pattern.pattern[:30]})")
                    break

    if not pages:
        warnings.append("no known-page list was found, href checks were skipped")

    emit({"passed": not failures, "failures": failures, "warnings": warnings, "rows_checked": len(rows), "known_pages": len(pages)}, 1 if failures else 0)


if __name__ == "__main__":
    main()
