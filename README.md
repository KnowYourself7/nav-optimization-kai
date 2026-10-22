# nav-optimization-kai

A Claude Code plugin with one skill, `nav-optimization`. It improves the navigation menu of an existing e-commerce site. It changes only grouping, order, labels and entries. It never creates, deletes or renames a URL.

The skill came out of a real project, the navigation redesign for a menswear store in October 2026. The design is in `docs/plans/2026-10-22-nav-optimization-skill-design.md`.

## What it delivers

| File | Content |
|---|---|
| `deliver/README.md` | a reading guide for the client |
| `deliver/proposal.md` | one section per top-level menu, each with a before-and-after tree and a five-column table |
| `deliver/mockup.html` | a clickable desktop and mobile mockup, no network needed |
| `deliver/changes.csv` | one row per change with product count, traffic, search volume and reason |

## Install

Load the plugin from this folder during development:

```bash
claude --plugin-dir /path/to/nav-optimization-kai
```

Then run `/nav-optimization-kai:nav-optimization <work-directory>` in a session.

## Inputs

Required: `inputs/brief.md` and `inputs/product_counts.csv`. Optional: a Search Console page export, a GA4 pages-and-screens export, a competitors list and DataForSEO credentials in the environment. The skill captures the current menu with Firecrawl MCP or the built-in browser.

## Layout

```
.claude-plugin/plugin.json
skills/nav-optimization/
  SKILL.md
  references/     principles, competitor matrix, change rules, templates, mockup schema, fallbacks
  scripts/        inventory, build_menu_table, search_volume, inject_mockup, verify
  assets/         mockup template, proposal and README templates in Chinese and English
  evals/          two test cases with sample data
docs/plans/       design documents
tests/            pytest for the scripts
```

## Tests

```bash
python3 -m pytest tests/
```

The tests run the scripts on the sample data in `skills/nav-optimization/evals/`. They need no network and no credentials.

## Rules for changing this skill

Before any change to `SKILL.md`, the references or the scripts, read the matching official source. The maintainer's `skill-dev-sources.md` lists the sources. Record the result in the commit message.
