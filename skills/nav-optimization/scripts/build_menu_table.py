#!/usr/bin/env python3
"""Build the current-menu table with product counts, search and analytics data, and flags.

Usage:
    python3 scripts/build_menu_table.py --workdir <work-directory>

Reads work/menu_current.json, inputs/product_counts.csv and, when present,
inputs/gsc_pages.csv and inputs/ga4_pages.csv.
Writes work/current_menu_table.csv and prints a JSON summary.
Exit code 2 when the menu or the product counts are missing.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from _common import emit, find_column, iterate_menu, load_menu, normalize_path, read_csv_rows, to_int, write_csv

# Baymard 2025: the deepest level needs at least 10 products.
MIN_PRODUCTS = 10
# Baymard 2025: users feel overwhelmed at about ten options in one level.
MAX_ITEMS_PER_LEVEL = 10
# Pages that list the whole catalog are not categories. Their handles vary; these are common.
LIST_ALL_HANDLES = {"/collections", "/collections/all", "/collections/all-products", "/collections/popular"}

COLUMNS = [
    "level", "top_level", "group", "label", "href", "product_count",
    "gsc_clicks", "gsc_impressions", "ga4_views", "ga4_key_events", "flags",
]


def load_product_counts(path: Path) -> dict[str, int]:
    rows = read_csv_rows(path)
    headers = list(rows[0].keys())
    url_col = find_column(headers, ["url", "path", "网址"])
    count_col = find_column(headers, ["product_count", "count", "商品数"])
    counts = {}
    for row in rows:
        counts[normalize_path(row[url_col])] = to_int(row[count_col]) or 0
    return counts


def load_gsc(path: Path) -> dict[str, dict]:
    rows = read_csv_rows(path)
    headers = list(rows[0].keys())
    page_col = find_column(headers, ["top pages", "page", "网页", "页面"])
    clicks_col = find_column(headers, ["clicks", "点击"])
    impr_col = find_column(headers, ["impressions", "展示"])
    data: dict[str, dict] = defaultdict(lambda: {"clicks": 0, "impressions": 0})
    for row in rows:
        key = normalize_path(row[page_col])
        data[key]["clicks"] += to_int(row.get(clicks_col)) or 0
        data[key]["impressions"] += to_int(row.get(impr_col)) or 0 if impr_col else 0
    return data


def load_ga4(path: Path) -> dict[str, dict]:
    rows = read_csv_rows(path)
    headers = list(rows[0].keys())
    page_col = find_column(headers, ["page path", "网页路径", "page"])
    views_col = find_column(headers, ["views", "浏览"])
    key_col = find_column(headers, ["key events", "关键事件", "conversions"])
    data: dict[str, dict] = defaultdict(lambda: {"views": 0, "key_events": 0})
    for row in rows:
        key = normalize_path(row[page_col])
        data[key]["views"] += to_int(row.get(views_col)) or 0
        data[key]["key_events"] += to_int(row.get(key_col)) or 0 if key_col else 0
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", required=True)
    args = parser.parse_args()
    workdir = Path(args.workdir).expanduser().resolve()

    menu_path = workdir / "work" / "menu_current.json"
    counts_path = workdir / "inputs" / "product_counts.csv"
    missing = [str(p.relative_to(workdir)) for p in (menu_path, counts_path) if not p.exists()]
    if missing:
        emit({"error": "missing inputs", "missing": missing}, 2)

    menu = load_menu(menu_path)
    counts = load_product_counts(counts_path)
    gsc_path = workdir / "inputs" / "gsc_pages.csv"
    ga4_path = workdir / "inputs" / "ga4_pages.csv"
    gsc = load_gsc(gsc_path) if gsc_path.exists() else None
    ga4 = load_ga4(ga4_path) if ga4_path.exists() else None

    rows = []
    href_counter = Counter()
    per_level_counter = Counter()
    for level, top, group, label, href, node in iterate_menu(menu):
        path = normalize_path(href)
        # A top-level link that repeats its own "All" entry is normal. Only third-level
        # entries at two places count as duplicates.
        if level == 3:
            href_counter[path] += 1
        per_level_counter[(top, group) if level == 3 else ("__top__", "") if level == 1 else (top, "__cols__")] += 1
        rows.append({
            "level": level, "top_level": top, "group": group, "label": label, "href": path,
            "product_count": counts.get(path, ""),
            "gsc_clicks": gsc[path]["clicks"] if gsc is not None and path in gsc else ("" if gsc is None else 0),
            "gsc_impressions": gsc[path]["impressions"] if gsc is not None and path in gsc else ("" if gsc is None else 0),
            "ga4_views": ga4[path]["views"] if ga4 is not None and path in ga4 else ("" if ga4 is None else 0),
            "ga4_key_events": ga4[path]["key_events"] if ga4 is not None and path in ga4 else ("" if ga4 is None else 0),
            "flags": "",
        })

    flag_counts = Counter()
    for row in rows:
        flags = []
        count = row["product_count"]
        if isinstance(count, int) and count < MIN_PRODUCTS:
            flags.append(f"fewer_than_{MIN_PRODUCTS}_products")
        if row["href"] in LIST_ALL_HANDLES and row["level"] > 1:
            flags.append("links_to_list_all_page")
        if href_counter[row["href"]] > 1:
            flags.append(f"same_url_{href_counter[row['href']]}_times")
        key = (row["top_level"], row["group"]) if row["level"] == 3 else ("__top__", "") if row["level"] == 1 else (row["top_level"], "__cols__")
        if per_level_counter[key] > MAX_ITEMS_PER_LEVEL:
            flags.append(f"level_has_{per_level_counter[key]}_items")
        row["flags"] = ";".join(flags)
        for flag in flags:
            flag_counts[flag.split("_")[0] + "_" + flag.split("_")[1]] += 1

    out = workdir / "work" / "current_menu_table.csv"
    write_csv(out, rows, COLUMNS)

    # Pages with data but no menu entry: a list for Step 4.
    menu_paths = {row["href"] for row in rows}
    not_in_menu = []
    for path in set(counts) | set(gsc or {}) | set(ga4 or {}):
        if path in menu_paths:
            continue
        not_in_menu.append({
            "href": path, "product_count": counts.get(path, ""),
            "gsc_clicks": gsc[path]["clicks"] if gsc and path in gsc else "",
            "ga4_views": ga4[path]["views"] if ga4 and path in ga4 else "",
            "ga4_key_events": ga4[path]["key_events"] if ga4 and path in ga4 else "",
        })
    not_in_menu.sort(key=lambda r: (-(r["gsc_clicks"] or 0) if isinstance(r["gsc_clicks"], int) else 0, -(r["ga4_views"] or 0) if isinstance(r["ga4_views"], int) else 0))
    write_csv(workdir / "work" / "pages_not_in_menu.csv", not_in_menu, ["href", "product_count", "gsc_clicks", "ga4_views", "ga4_key_events"])

    emit({
        "rows": len(rows), "output": str(out.relative_to(workdir)),
        "gsc_present": gsc is not None, "ga4_present": ga4 is not None,
        "flag_counts": dict(flag_counts), "pages_not_in_menu": len(not_in_menu),
        "top_level_count": len(menu.get("items", [])),
    })


if __name__ == "__main__":
    main()
