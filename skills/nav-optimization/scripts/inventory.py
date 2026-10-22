#!/usr/bin/env python3
"""Check the inputs of a nav-optimization run and write the inventory.

Usage:
    python3 scripts/inventory.py --workdir <work-directory>

Reads <workdir>/inputs/ and <workdir>/work/menu_current.json.
Writes <workdir>/work/inventory.json and <workdir>/work/inventory.md.
Exit code 2 when a required input is missing, else 0.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from _common import emit, find_column, load_menu, read_csv_rows

REQUIRED = {
    "brief": ("inputs/brief.md", "site URL, the problem, what must not change, delivery language"),
    "product_counts": ("inputs/product_counts.csv", "columns url,product_count"),
}

OPTIONAL = {
    "gsc": ("inputs/gsc_pages.csv", "Search Console page export"),
    "ga4": ("inputs/ga4_pages.csv", "GA4 Pages and screens export"),
    "competitors": ("inputs/competitors.txt", "three to five competitor URLs"),
}

FALLBACK = {
    "gsc": "No 'traffic but no entry' search. Entries are removed on the product rule only. Retarget candidates are marked pending.",
    "ga4": "Entries are not removed for low views. Low-traffic candidates are marked pending.",
    "competitors": "Propose three to five sites by tier at STOP 1.",
    "dataforseo": "Labels keep their current text. search_volume is 'not checked'. Candidates go to client decisions.",
    "menu_current": "Capture the menu with Firecrawl or the browser, or ask the user to paste it.",
}


def check_product_counts(path: Path) -> tuple[bool, str]:
    rows = read_csv_rows(path)
    if not rows:
        return False, "the file has no rows"
    headers = list(rows[0].keys())
    url_col = find_column(headers, ["url", "path", "网址"])
    count_col = find_column(headers, ["product_count", "count", "商品数"])
    if not url_col or not count_col:
        return False, f"need columns url and product_count, found {headers}"
    bad = [row for row in rows if not str(row.get(count_col, "")).strip().replace(",", "").isdigit()]
    if bad:
        return False, f"{len(bad)} rows have a non-numeric product_count"
    return True, f"{len(rows)} category pages"


def check_gsc(path: Path) -> tuple[bool, str]:
    rows = read_csv_rows(path)
    headers = list(rows[0].keys()) if rows else []
    page_col = find_column(headers, ["top pages", "page", "网页", "页面"])
    clicks_col = find_column(headers, ["clicks", "点击"])
    if not rows or not page_col or not clicks_col:
        return False, f"need a page column and a clicks column, found {headers}"
    return True, f"{len(rows)} rows"


def check_ga4(path: Path) -> tuple[bool, str]:
    rows = read_csv_rows(path)
    headers = list(rows[0].keys()) if rows else []
    page_col = find_column(headers, ["page path", "网页路径", "page"])
    views_col = find_column(headers, ["views", "浏览"])
    if not rows or not page_col or not views_col:
        return False, f"need a page path column and a views column, found {headers}"
    return True, f"{len(rows)} rows"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", required=True, help="the run's work directory")
    args = parser.parse_args()
    workdir = Path(args.workdir).expanduser().resolve()
    for folder in ("inputs", "work", "deliver", "history"):
        (workdir / folder).mkdir(parents=True, exist_ok=True)

    report = {"workdir": str(workdir), "required": {}, "optional": {}, "missing_required": [], "fallbacks": {}}

    for key, (relative, hint) in REQUIRED.items():
        path = workdir / relative
        if not path.exists():
            report["required"][key] = {"present": False, "path": relative, "hint": hint}
            report["missing_required"].append(relative)
            continue
        if key == "product_counts":
            ok, note = check_product_counts(path)
        else:
            ok = path.stat().st_size > 0
            note = "non-empty" if ok else "the file is empty"
        report["required"][key] = {"present": ok, "path": relative, "note": note, "hint": hint}
        if not ok:
            report["missing_required"].append(relative)

    for key, (relative, hint) in OPTIONAL.items():
        path = workdir / relative
        if not path.exists():
            report["optional"][key] = {"present": False, "path": relative, "hint": hint}
            report["fallbacks"][key] = FALLBACK[key]
            continue
        if key == "gsc":
            ok, note = check_gsc(path)
        elif key == "ga4":
            ok, note = check_ga4(path)
        else:
            lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            ok, note = len(lines) >= 1, f"{len(lines)} sites"
        report["optional"][key] = {"present": ok, "path": relative, "note": note, "hint": hint}
        if not ok:
            report["fallbacks"][key] = FALLBACK[key]

    has_creds = bool(os.environ.get("DATAFORSEO_LOGIN")) and bool(os.environ.get("DATAFORSEO_PASSWORD"))
    report["optional"]["dataforseo_env"] = {"present": has_creds, "note": "credentials found in environment" if has_creds else "no credentials in environment; an MCP tool can still provide volumes"}
    if not has_creds:
        report["fallbacks"]["dataforseo"] = FALLBACK["dataforseo"]

    menu_path = workdir / "work" / "menu_current.json"
    if menu_path.exists():
        try:
            menu = load_menu(menu_path)
            report["menu_current"] = {"present": True, "top_level_items": len(menu.get("items", []))}
        except (ValueError, OSError) as error:
            report["menu_current"] = {"present": False, "note": str(error)}
            report["fallbacks"]["menu_current"] = FALLBACK["menu_current"]
    else:
        report["menu_current"] = {"present": False}
        report["fallbacks"]["menu_current"] = FALLBACK["menu_current"]

    lines = ["# Inventory", ""]
    lines.append("## Required")
    for key, info in report["required"].items():
        lines.append(f"- {info['path']}: {'present' if info['present'] else 'MISSING'} ({info.get('note', info['hint'])})")
    lines.append("")
    lines.append("## Optional")
    for key, info in report["optional"].items():
        lines.append(f"- {info.get('path', key)}: {'present' if info['present'] else 'missing'} ({info.get('note', '')})")
    lines.append(f"- work/menu_current.json: {'present' if report['menu_current'].get('present') else 'missing'}")
    lines.append("")
    if report["fallbacks"]:
        lines.append("## Fallbacks that apply")
        for key, text in report["fallbacks"].items():
            lines.append(f"- {key}: {text}")
    (workdir / "work" / "inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (workdir / "work" / "inventory.json").write_text(__import__("json").dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    emit(report, 2 if report["missing_required"] else 0)


if __name__ == "__main__":
    main()
