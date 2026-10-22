"""End-to-end tests for the nav-optimization scripts on the sample data in evals/.

Run: python3 -m pytest tests/
No network, no credentials.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "nav-optimization"
SCRIPTS = SKILL / "scripts"
CASE_FULL = SKILL / "evals" / "full-data-english-brief" / "files"
CASE_MIN = SKILL / "evals" / "counts-only-chinese-brief" / "files"


def run(script: str, *args: str, expect: int = 0) -> dict:
    result = subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True)
    assert result.returncode == expect, f"{script} exit {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    return json.loads(result.stdout)


def make_workdir(tmp_path: Path, case_dir: Path) -> Path:
    workdir = tmp_path / "run"
    (workdir / "inputs").mkdir(parents=True)
    (workdir / "work").mkdir()
    for file in case_dir.iterdir():
        target = workdir / ("work" if file.name == "menu_current.json" else "inputs") / file.name
        shutil.copy(file, target)
    return workdir


def test_inventory_reports_fallbacks_when_optional_inputs_are_missing(tmp_path):
    workdir = make_workdir(tmp_path, CASE_MIN)
    report = run("inventory.py", "--workdir", str(workdir))
    assert report["missing_required"] == []
    assert set(report["fallbacks"]) >= {"gsc", "ga4", "competitors"}
    assert (workdir / "work" / "inventory.md").exists()


def test_inventory_fails_without_product_counts(tmp_path):
    workdir = make_workdir(tmp_path, CASE_MIN)
    (workdir / "inputs" / "product_counts.csv").unlink()
    report = run("inventory.py", "--workdir", str(workdir), expect=2)
    assert "inputs/product_counts.csv" in report["missing_required"]


def test_build_menu_table_joins_data_and_flags(tmp_path):
    workdir = make_workdir(tmp_path, CASE_FULL)
    report = run("build_menu_table.py", "--workdir", str(workdir))
    assert report["gsc_present"] and report["ga4_present"]
    rows = list(csv.DictReader((workdir / "work" / "current_menu_table.csv").open(encoding="utf-8-sig")))
    by_href = {row["href"]: row for row in rows}
    assert by_href["/collections/knit-shirts"]["product_count"] == "7"
    assert "fewer_than_10_products" in by_href["/collections/knit-shirts"]["flags"]
    assert "links_to_list_all_page" in by_href["/collections"]["flags"]
    assert "same_url" in by_href["/collections/minimal-style"]["flags"]
    # the German locale row folds into the base path, so shirts clicks include it
    assert int(by_href["/collections/shirts"]["gsc_clicks"]) == 7400 + 141
    not_in_menu = {row["href"] for row in csv.DictReader((workdir / "work" / "pages_not_in_menu.csv").open(encoding="utf-8-sig"))}
    assert {"/collections/sets", "/collections/suits", "/collections/swim-trunks", "/collections/clearance"} <= not_in_menu


def proposed_menu() -> dict:
    return {
        "brand": "NORTHWIND",
        "utility": ["Track Order", "Rewards"],
        "items": [
            {"label": "NEW ARRIVALS", "href": "/collections/new-arrivals", "count": 410, "cols": [
                {"title": "New", "items": [{"label": "All New", "href": "/collections/new-arrivals", "count": 410}, {"label": "Summer Edit", "href": "/collections/summer-edit", "count": 95}]}]},
            {"label": "BEST SELLERS", "href": "/collections/best-sellers", "count": 120, "direct": True},
            {"label": "TOPS", "href": "/collections/tops", "count": 520, "cols": [
                {"title": "Tops", "items": [{"label": "Shirts", "href": "/collections/shirts", "count": 260}, {"label": "Polo Shirts", "href": "/collections/polos", "count": 60, "tag": "chg"}]}]},
            {"label": "SALE", "href": "/collections/clearance", "count": 14, "cols": [
                {"title": "Sale", "items": [{"label": "Clearance", "href": "/collections/clearance", "count": 14, "tag": "new"}, {"label": "Holiday", "href": "/collections/holiday-sale", "count": 40}]}]},
        ],
        "footer": [{"title": "About", "items": [{"label": "Our Story", "href": "/pages/about"}]}],
    }


def write_deliverables(workdir: Path, lang: str = "en") -> None:
    deliver = workdir / "deliver"
    deliver.mkdir(exist_ok=True)
    (deliver / "menu_proposed.json").write_text(json.dumps(proposed_menu()), encoding="utf-8")
    columns = ["top_level", "group", "item", "old_location", "old_label", "new_label", "href", "product_count", "gsc_clicks", "ga4_views", "ga4_key_events", "search_volume", "change_type", "reason"]
    rows = [
        dict(zip(columns, ["TOPS", "Tops", "Polo Shirts", "CLOTHING > Tops > Polos", "Polos", "Polo Shirts", "/collections/polos", 60, 790, 40000, 50, "not checked", "rename", "polo shirts is the common search term"])),
        dict(zip(columns, ["SALE", "Sale", "Clearance", "not in menu", "", "Clearance", "/collections/clearance", 14, 170, 600, 1, "not checked", "add", "170 clicks and no entry"])),
        dict(zip(columns, ["removed", "", "Knit Shirts", "CLOTHING > Tops > Knit Shirts", "Knit Shirts", "", "/collections/knit-shirts", 7, 2, 2200, 0, "not checked", "remove", "7 products, below 10"])),
    ]
    with (deliver / "changes.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    headings = {"en": ["One-page summary", "Overview", "Client decisions", "Implementation and verification"], "zh": ["一页摘要", "总览", "需要客户决定", "实施与验证"]}[lang]
    (deliver / "proposal.md").write_text("# Proposal\n\n" + "\n\n".join(f"## {h}\n\ntext" for h in headings) + "\n", encoding="utf-8")
    (deliver / "README.md").write_text("# Guide\n", encoding="utf-8")


def test_inject_mockup_builds_self_contained_page(tmp_path):
    menu_path = tmp_path / "menu.json"
    menu_path.write_text(json.dumps(proposed_menu()), encoding="utf-8")
    out = tmp_path / "mockup.html"
    report = run("inject_mockup.py", "--menu", str(menu_path), "--lang", "en", "--out", str(out))
    page = out.read_text(encoding="utf-8")
    assert report["top_level_items"] == 4
    assert "/*NAV_DATA*/null" not in page and "/*UI_STRINGS*/null" not in page
    assert "NORTHWIND" in page and "Polo Shirts" in page and "Footer" in page
    assert "http" not in page.split("<body>")[0].replace("http-equiv", "")


def test_inject_mockup_rejects_more_than_ten_top_level_items(tmp_path):
    menu = proposed_menu()
    menu["items"] = [{"label": f"T{i}", "href": f"/collections/t{i}", "direct": True} for i in range(11)]
    menu_path = tmp_path / "menu.json"
    menu_path.write_text(json.dumps(menu), encoding="utf-8")
    report = run("inject_mockup.py", "--menu", str(menu_path), "--out", str(tmp_path / "x.html"), expect=1)
    assert "11 top-level items" in " ".join(report["problems"])


def test_verify_passes_on_consistent_deliverables(tmp_path):
    workdir = make_workdir(tmp_path, CASE_FULL)
    write_deliverables(workdir)
    run("inject_mockup.py", "--menu", str(workdir / "deliver" / "menu_proposed.json"), "--lang", "en", "--out", str(workdir / "deliver" / "mockup.html"))
    report = run("verify.py", "--workdir", str(workdir), "--lang", "en")
    assert report["passed"], report["failures"]


def test_verify_catches_unknown_page_thin_entry_and_secret(tmp_path):
    workdir = make_workdir(tmp_path, CASE_FULL)
    write_deliverables(workdir)
    menu = proposed_menu()
    menu["items"][2]["cols"][0]["items"].append({"label": "Ghost", "href": "/collections/does-not-exist", "count": 50})
    menu["items"][2]["cols"][0]["items"].append({"label": "Leather", "href": "/collections/leather", "count": 3})
    (workdir / "deliver" / "menu_proposed.json").write_text(json.dumps(menu), encoding="utf-8")
    (workdir / "deliver" / "notes.txt").write_text("password = hunter2secret\n", encoding="utf-8")
    run("inject_mockup.py", "--menu", str(workdir / "deliver" / "menu_proposed.json"), "--out", str(workdir / "deliver" / "mockup.html"))
    report = run("verify.py", "--workdir", str(workdir), "--lang", "en", expect=1)
    text = " ".join(report["failures"])
    assert "does-not-exist" in text
    assert "3 products" in text
    assert "credential-like" in text


def test_search_volume_refuses_without_credentials(tmp_path, monkeypatch):
    monkeypatch.delenv("DATAFORSEO_LOGIN", raising=False)
    monkeypatch.delenv("DATAFORSEO_PASSWORD", raising=False)
    keywords = tmp_path / "k.txt"
    keywords.write_text("mens polo shirts\n", encoding="utf-8")
    report = run("search_volume.py", "--keywords", str(keywords), "--out", str(tmp_path / "v.csv"), expect=2)
    assert "DATAFORSEO_LOGIN" in report["error"]
