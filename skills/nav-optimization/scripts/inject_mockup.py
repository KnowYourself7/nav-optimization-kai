#!/usr/bin/env python3
"""Write a proposed menu into the mockup template and save a self-contained HTML page.

Usage:
    python3 scripts/inject_mockup.py --menu deliver/menu_proposed.json --lang zh --out deliver/mockup.html

The menu file follows the schema in references/mockup.md. The script validates
it, selects the UI strings for the language (zh or en), replaces the
placeholders in assets/mockup-template.html and writes the page.
Exit code 2 when a file is missing, 1 when the menu breaks a schema rule.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import emit, load_menu

# Baymard 2025: about ten items per level is the limit.
MAX_TOP_LEVEL = 10
MAX_PER_COLUMN = 10

UI = {
    "zh": {
        "title": "导航示意",
        "desktop": "桌面端",
        "desktop_hint": "上方黑条是顶部工具栏，白条是导航栏，鼠标移到一级项上展开大菜单；最下面标“页脚”的是页面底部，不是导航",
        "hover_hint": "把鼠标移到任意一级项上。",
        "direct_hint": "{label} 是直链，没有下拉，点击直接进入。",
        "content_area": "…… 页面内容区（略）……",
        "footer_label": "页脚 Footer",
        "footer_note": "页面最底部，不是导航栏",
        "mobile": "手机端",
        "mobile_hint": "点右上角菜单，一级就是品类，再点一下到具体入口",
        "menu": "菜单",
        "open_menu": "打开菜单",
        "close_menu": "关闭菜单",
        "home_area": "首页内容区（示意）",
        "shop_all": "Shop All",
        "legend_new": "新增入口（页面已存在，原来没入口）",
        "legend_chg": "改名或改指向",
        "legend_article": "“指南”行是挂在下拉末尾的内容页",
        "legend_count": "数字 = 该分类的商品数",
        "tag_new": "新",
        "tag_chg": "改",
        "article": "指南",
    },
    "en": {
        "title": "Navigation mockup",
        "desktop": "Desktop",
        "desktop_hint": "The black bar is the utility bar, the white bar is the navigation. Hover a top-level item to open the dropdown. The block labeled Footer is the page bottom, not navigation.",
        "hover_hint": "Hover any top-level item.",
        "direct_hint": "{label} is a direct link with no dropdown.",
        "content_area": "... page content area (omitted) ...",
        "footer_label": "Footer",
        "footer_note": "bottom of the page, not navigation",
        "mobile": "Mobile",
        "mobile_hint": "Tap the menu icon. The first level is the categories. Tap once more to reach an entry.",
        "menu": "Menu",
        "open_menu": "Open menu",
        "close_menu": "Close menu",
        "home_area": "Home page content (placeholder)",
        "shop_all": "Shop All",
        "legend_new": "new entry (the page existed, the entry did not)",
        "legend_chg": "renamed or retargeted",
        "legend_article": "a Guide row is a content page at the end of a dropdown",
        "legend_count": "number = product count of the category",
        "tag_new": "new",
        "tag_chg": "chg",
        "article": "Guide",
    },
}


def validate(menu: dict) -> list[str]:
    """Return a list of schema problems. An empty list means the menu is valid."""
    problems = []
    items = menu.get("items", [])
    if not isinstance(items, list) or not items:
        return ["items must be a non-empty list"]
    if len(items) > MAX_TOP_LEVEL:
        problems.append(f"{len(items)} top-level items, the limit is {MAX_TOP_LEVEL}")
    for index, top in enumerate(items):
        where = f"items[{index}] {top.get('label', '?')}"
        if not top.get("label"):
            problems.append(f"{where}: missing label")
        if top.get("direct") and top.get("cols"):
            problems.append(f"{where}: direct is true but cols is present")
        if not top.get("direct") and not top.get("cols"):
            problems.append(f"{where}: no cols and not direct")
        for col_index, col in enumerate(top.get("cols") or []):
            col_where = f"{where} cols[{col_index}] {col.get('title', '?')}"
            col_items = col.get("items") or []
            if len(col_items) > MAX_PER_COLUMN:
                problems.append(f"{col_where}: {len(col_items)} items, the limit is {MAX_PER_COLUMN}")
            for item in col_items:
                if not item.get("label") or not item.get("href"):
                    problems.append(f"{col_where}: an item lacks label or href")
                if item.get("tag") not in (None, "new", "chg"):
                    problems.append(f"{col_where}: tag must be new or chg")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--menu", required=True)
    parser.add_argument("--lang", choices=sorted(UI), default="zh")
    parser.add_argument("--out", required=True)
    parser.add_argument("--template", default=str(Path(__file__).resolve().parent.parent / "assets" / "mockup-template.html"))
    args = parser.parse_args()

    menu_path = Path(args.menu)
    template_path = Path(args.template)
    for path in (menu_path, template_path):
        if not path.exists():
            emit({"error": f"file not found: {path}"}, 2)
    try:
        menu = load_menu(menu_path)
    except (ValueError, json.JSONDecodeError) as error:
        emit({"error": f"menu JSON is not valid: {error}"}, 1)

    problems = validate(menu)
    if problems:
        emit({"error": "menu breaks the schema", "problems": problems}, 1)

    template = template_path.read_text(encoding="utf-8")
    page = (
        template
        .replace("/*NAV_DATA*/null", json.dumps(menu, ensure_ascii=False))
        .replace("/*UI_STRINGS*/null", json.dumps(UI[args.lang], ensure_ascii=False))
        .replace("{{TITLE}}", f"{menu.get('brand', '')} {UI[args.lang]['title']}".strip())
        .replace("{{LANG}}", "zh-CN" if args.lang == "zh" else "en")
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    emit({"output": str(out), "top_level_items": len(menu["items"]), "lang": args.lang})


if __name__ == "__main__":
    main()
