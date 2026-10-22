# Deliverable templates

Four files go to the client. Build them from `assets/` in the language the brief names. Menu labels stay in the site's own language in every file.

## Contents

- README
- Proposal
- Mockup
- Change table
- Appendix

## README

Template: `assets/readme-template.zh.md` or `assets/readme-template.en.md`.

Sections, in order:

1. The three files and how to open each.
2. Reading order.
3. The decisions the client must make, with the section number for each.
4. How to give feedback.
5. Next steps.
6. Data note.

## Proposal

Template: `assets/proposal-template.zh.md` or `assets/proposal-template.en.md`.

Fixed structure:

1. Document info table: site, version and date, status, scope, data window, companion files, how to read.
2. One-page summary: the problems with numbers, the proposal in three lines, expected benefits, the four things the client must do, how to verify.
3. Overview. It holds five parts. The full proposed tree in a code block. The four principles table. A change summary table with counts per type. The data sources table. The competitors table.
4. One section per top-level item, in menu order. Each section has three parts. First, a code block with the current tree on the left and the proposed tree on the right. The trees carry product counts, the marks `(new)`, `(renamed)` and `(retargeted)`, and arrows for items that move out. Second, one table with five columns: item, what changes, why, data, competitor practice. Third, three sentences on the benefit for shoppers, for search and for operations.
5. A footer section with the same shape.
6. Client decisions in five groups. Group A: restock or build pages, ordered by search volume. Group B: duplicate pages, with the merge rules and a two-row-per-pair table with all numbers. Group C: content. Group D: structure and templates. Group E: alternatives and verification.
7. Implementation and verification: steps, the acceptance list, metrics to compare 30 days after launch.
8. Appendix one, sources. Appendix two, glossary.

Rules for the tables: one row per change. The data column holds the numbers. The competitor column names the sites. A cell with no data says "no data" and the reason.

## Mockup

`assets/mockup-template.html` plus `deliver/menu_proposed.json` through `scripts/inject_mockup.py`. Read `references/mockup.md` for the schema. The page shows a desktop header with hover dropdowns, a phone frame with a two-level drawer, a content-area spacer and a labeled footer. The label keeps the client from taking the footer for the menu.

## Change table

`deliver/changes.csv`, the 14 columns in `references/change-rules.md`. Save it as UTF-8 with BOM so that Excel reads it.

## Appendix

Copy `work/current_menu_table.csv`, `work/competitor_matrix.csv` and `work/search_volume.csv` into `deliver/appendix/`.
