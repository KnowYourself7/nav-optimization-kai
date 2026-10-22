---
name: nav-optimization
description: Optimizes the navigation menu of an existing e-commerce site. Changes only grouping, order, labels and entries, never a URL. Delivers a client proposal, a clickable HTML mockup and a change table backed by product counts, Search Console, GA4, keyword volume and competitor menus. If the user wants to improve, audit, restructure, simplify or rename a site menu, use this skill. This covers the navigation, mega menu, header menu, main menu, category menu and mobile hamburger menu. If the user asks how to group a store's categories, use this skill too, even without the word navigation.
argument-hint: "[work-directory]"
user-invocable: true
compatibility: Needs Python 3.11. Uses Firecrawl MCP or the built-in browser to capture menus. Reads DataForSEO through MCP or REST with credentials in environment variables.
metadata:
  author: Kai
  version: "0.1.0"
---

# Navigation optimization

Improve the navigation menu of a live e-commerce site. Change only grouping, order, labels and entries. Reuse existing pages. Never create, delete or rename a URL. Every change in the deliverable carries a data reason and a competitor reference.

The work directory is `$ARGUMENTS`. If it is empty, ask the user for one. Inside it use four folders: `inputs/`, `work/`, `deliver/`, `history/`.

## Checklist

Copy this checklist into your first reply and update it as you go.

```
Nav optimization
- [ ] Step 1 Inventory: inputs checked, current menu captured, competitor list proposed. STOP 1
- [ ] Step 2 Current-menu table built with flags
- [ ] Step 3 Competitor matrix filled
- [ ] Step 4 Change table drafted, open decisions listed. STOP 2
- [ ] Step 5 Deliverables generated, verify.py passed. STOP 3
- [ ] Step 6 Snapshot saved to history/
```

## Step 1: Inventory

The skill needs two inputs. If one is missing, stop and ask for it.

| File | Content |
|---|---|
| `inputs/brief.md` | Site URL, the problem the client states, what must not change, delivery language |
| `inputs/product_counts.csv` | Columns `url,product_count`, one row per category page |

Four inputs are optional. Each has a fixed fallback in `references/degradation.md`.

| File | Content |
|---|---|
| `inputs/gsc_pages.csv` | Search Console page export, 12 months, filtered to category paths |
| `inputs/ga4_pages.csv` | GA4 "Pages and screens" export, 12 months |
| `inputs/competitors.txt` | Three to five competitor URLs, one per line |
| DataForSEO | MCP tools, or `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` in the environment |

Capture the current menu, desktop and mobile. Use Firecrawl MCP `firecrawl_scrape` with JavaScript rendering first. If it fails, use the built-in browser. If both fail, ask the user to paste the menu text. Write the result as `work/menu_current.json` in the schema given in `references/mockup.md`.

Run the inventory script. It lists what is present, what is missing and which fallback applies.

```bash
python3 scripts/inventory.py --workdir <work-directory>
```

If the user gave no competitor list, propose three to five sites by tier. The tiers are mass market, direct-to-consumer, mid-price, and one marketplace as a reference only. Give a reason for each pick in the reply.

STOP 1. Show the inventory and the competitor list. Wait until the user approves both.

## Step 2: Current-menu table

Build one row per menu item with product count, search clicks, views and key events joined by URL path.

```bash
python3 scripts/build_menu_table.py --workdir <work-directory>
```

The script writes `work/current_menu_table.csv` and sets four flags on its own. Flag one: fewer than 10 products. Flag two: more than 10 items at one level. Flag three: a header link that points to a list-all page. Flag four: the same URL at two places. Read the flagged rows. They are the first candidates for change.

## Step 3: Competitor matrix

For each competitor capture the desktop menu and the mobile menu the same way as in Step 1. Fill `work/competitor_matrix.csv` with the seven dimensions in `references/competitor-matrix.md`. If at least two brand sites agree on a practice, mark it "reference". A marketplace counts as context, not as a vote.

Record what you were not able to capture. Never fill a cell from memory.

## Step 4: Change table and open decisions

Apply the rules in `references/change-rules.md` to every row of the current-menu table. Then apply them to every page with traffic that has no entry. Write `deliver/changes.csv` with the 14 columns listed there. Write `deliver/menu_proposed.json` in the mockup schema.

For label changes, look up the search volume. If a DataForSEO MCP tool is present, use `dataforseo_labs_google_keyword_overview` or the Google Ads tool for search volume. If not, run:

```bash
python3 scripts/search_volume.py --keywords work/label_candidates.txt --out work/search_volume.csv
```

Some decisions depend on business priorities, not data. Examples: whether a style collection stays, whether a content entry keeps a top-level slot, whether a signature material gets its own top-level item. Collect these in `work/open_decisions.md`, one line each, with your recommendation and the numbers behind it.

STOP 2. Show the open decisions. Wait for the user. Write each ruling into the `reason` column of the row it affects.

## Step 5: Deliverables

Generate four files in `deliver/` from the templates in `assets/`, in the language the brief names. Read `references/deliverable-templates.md` for the fixed structure of the proposal and the README.

1. `README.md` for the client.
2. `proposal.md`: one section per top-level item. Each section has a before-and-after tree and a five-column table (item, what changes, why, data, competitor practice). Client decisions go only in the last section.
3. `mockup.html`: run `python3 scripts/inject_mockup.py --menu deliver/menu_proposed.json --lang zh|en --out deliver/mockup.html`.
4. `changes.csv` from Step 4.

Copy the Step 2 and Step 3 tables into `deliver/appendix/`.

Run the verifier. Fix every failure before the stop.

```bash
python3 scripts/verify.py --workdir <work-directory>
```

STOP 3. Show the verifier report and the proposal summary. Wait until the user approves.

## Step 6: Snapshot

Copy `work/` and `deliver/` into `history/<date>/` so that you can compare the next revision with this one.

## Rules that do not bend

Each rule has a reason in `references/principles.md`.

- Do not change, create or delete a URL. Needs of that kind go to the "client decisions" section only.
- A page with fewer than 10 products gets no menu entry.
- Company pages (about, reviews, certificates, news) do not take a top-level slot. If the brief asks for it, they can.
- Content entries (blog, guides) take a top-level slot only in one case: the brief asks for internal links to content.
- Attributes such as color, material, warehouse or shipping origin become filters, not categories.
- A competitor practice without a capture record is not a reference.
- Mark a judgment without data as "pending". Never write it as a conclusion.
- Numbers come from a file in `inputs/` or `work/`. Never estimate.
- Credentials never appear in any output. The scripts read them from the environment only.

## Reference files

Read the file that the current step names.

- `references/principles.md`: the four principles, the thresholds and their sources.
- `references/competitor-matrix.md`: the seven dimensions and how to fill them.
- `references/change-rules.md`: the decision rules per change type and the 14 columns.
- `references/deliverable-templates.md`: proposal and README structure.
- `references/mockup.md`: the menu JSON schema and how the script builds the mockup.
- `references/degradation.md`: the fallback for each missing optional input.
