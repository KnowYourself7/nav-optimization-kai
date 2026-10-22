# {{SITE}} navigation proposal (version {{VERSION}})

| Document | |
|---|---|
| Site | {{SITE_URL}} |
| Version | {{VERSION}}, {{DATE}} |
| Status | waiting for client approval |
| Scope | menu grouping, order, labels and entries only. No page is created, deleted or moved. |
| Data window | {{DATA_WINDOW}} |
| Companion files | mockup.html (clickable mockup), changes.csv (one row per change) |
| How to read | Read the one-page summary first. Each top-level menu has its own section with a tree and a five-column table. Client decisions are in the last section. Terms are in appendix two. |

---

## One-page summary

Problems today:

- {{PROBLEM_1_WITH_NUMBERS}}
- {{PROBLEM_2_WITH_NUMBERS}}
- {{PROBLEM_3_WITH_NUMBERS}}

The proposal:

- {{PROPOSAL_LINE_1}}
- {{PROPOSAL_LINE_2}}
- {{PROPOSAL_LINE_3}}

Expected benefits:

- Shoppers: {{BENEFIT_SHOPPERS}}
- Search: {{BENEFIT_SEARCH}}
- Operations: {{BENEFIT_OPERATIONS}}

Four things the client must do (details in the client decisions section):

1. {{CLIENT_TODO_1}}
2. {{CLIENT_TODO_2}}
3. {{CLIENT_TODO_3}}
4. {{CLIENT_TODO_4}}

How to verify: {{VERIFICATION_ONE_LINE}}

---

## Overview

```
{{PROPOSED_TREE}}
```

### Four principles

| Principle | Meaning | Source |
|---|---|---|
| One axis per level | product type is the main axis. Material, style and occasion sit together under one entry. Attributes become filters. | Baymard 2025 |
| Mobile first | categories on the first level of the mobile menu, two taps to any category | mobile share of clicks: {{MOBILE_SHARE}}. Baymard 2025 pitfall 1 |
| Data decides | product count decides entry, traffic decides the slot, search volume decides the label | Baymard 2025, Google Search Central |
| Menu only | every entry reuses an existing page | project scope |

### Change summary

| Change type | Count | Items |
|---|---|---|
| promote | {{N}} | {{LIST}} |
| rename | {{N}} | {{LIST}} |
| add | {{N}} | {{LIST}} |
| remove | {{N}} | {{LIST}} |
| move | {{N}} | {{LIST}} |
| footer | {{N}} | {{LIST}} |

### Data sources

| Data | Window | Used for |
|---|---|---|
| product counts | {{DATE}} | whether a page can enter the menu |
| Search Console | {{WINDOW}} or "not available" | search traffic, pages without an entry |
| GA4 pages and screens | {{WINDOW}} or "not available" | views and key events |
| search volume | {{DATE}} or "not looked up" | labels |
| competitor menus | {{DATE}} | practice reference |

### Competitors

| Site | Tier | Menu pattern |
|---|---|---|
| {{SITE}} | {{TIER}} | {{PATTERN}} |

Sites not captured: {{NOT_CAPTURED_WITH_REASON}}

---

## 1. {{TOP_LEVEL_LABEL}}

```
Current                                   Proposed
{{BEFORE_TREE}}                           {{AFTER_TREE}}
```

| Item | What changes | Why | Data | Competitor practice |
|---|---|---|---|---|
| {{ITEM}} | {{CHANGE}} | {{WHY}} | {{DATA}} | {{COMPETITORS}} |

Benefits: {{SHOPPER_BENEFIT}} {{SEARCH_BENEFIT}} {{OPERATIONS_BENEFIT}}

---

## Footer

```
{{FOOTER_TREE}}
```

| Item | What changes | Why | Data | Competitor practice |
|---|---|---|---|---|
| {{ITEM}} | {{CHANGE}} | {{WHY}} | {{DATA}} | {{COMPETITORS}} |

---

## Client decisions

Everything here is outside "menu only". Each row names the section it comes from.

### A. Restock or build pages (ordered by search volume)

| Item | Today | Recommendation | Section |
|---|---|---|---|

### B. Duplicate pages

Merge rules, in order:

1. Two normal category pages with near-identical products: keep the URL with more search clicks and impressions, move the products into it, redirect the other one. A redirect transfers search equity. Views from ads and internal links follow the link.
2. Both pages weak in search: keep the one the menu uses with more products.
3. A page whose product count equals the whole catalog is a campaign landing page: do not redirect. Add noindex and retire it after the campaign.

| Pair | Page | Products | Clicks / impressions | Views / key events | Decision | Section |
|---|---|---|---|---|---|---|

### C. Content

| Item | Note | Section |
|---|---|---|

### D. Structure and templates

| Item | Note | Section |
|---|---|---|

### E. Alternatives and verification

| Item | Note |
|---|---|
| Plan B | {{PLAN_B}} |
| User testing | {{USER_TESTING_NOTE}} |

---

## Implementation and verification

### Steps

| Step | Action | Owner | Note |
|---|---|---|---|
| 1 | Client approves plan A or plan B and the restock items | client | restock does not block the menu launch |
| 2 | Create a new menu in the store admin. Do not edit the live one. | implementer | copy each href from changes.csv |
| 3 | Point the header and the mobile drawer to the new menu. Build the footer menu. | implementer | most themes share one menu object for desktop and mobile |
| 4 | Preview: every item opens the right page, every dropdown opens, every mobile level expands | implementer | compare with mockup.html |
| 5 | Publish. Keep the old menu so that the store can switch back. | implementer | |
| 6 | Within a week apply the redirects and noindex from section B | implementer | separate task |

### Acceptance list

- Every menu item points to an existing page. No 404.
- At most 10 top-level items. No dropdown column above 10 items.
- The mobile first level is the categories. Any category page is two taps away.
- The footer has the About, Guides and Help columns.

### Metrics 30 days after launch

| Metric | Today | Expectation | Source |
|---|---|---|---|
| share of views on menu pages | {{N}} | up | GA4 pages and screens |
| views and key events of the new entries | {{N}} | up | GA4 |
| search clicks of category pages | {{N}} | not down | Search Console pages |

---

## Appendix one: sources

- Google Search Central, e-commerce site structure: https://developers.google.com/search/docs/specialty/ecommerce/help-google-understand-your-ecommerce-site-structure
- Google Search Central, faceted navigation: https://developers.google.com/search/blog/2024/12/crawling-december-faceted-nav
- Baymard Institute, navigation research 2025: https://baymard.com/blog/ecommerce-navigation-best-practice
- Competitor captures: appendix folder
- Raw data: inputs folder

## Appendix two: glossary

| Term | Meaning |
|---|---|
| category page | a page that lists the products of one group, for example /collections/shirts |
| top level, dropdown, column | a top-level item sits in the header bar. The dropdown opens under it. A column is one list inside the dropdown. |
| clicks and impressions | Search Console numbers. Impressions count how often the page appeared in Google results. Clicks count visits from those results. |
| key events | GA4 actions marked as conversions, such as add to cart or purchase |
| search volume | average monthly searches on Google for a word, from DataForSEO |
| redirect | the old URL sends the visitor to the new URL and passes its search equity |
| noindex | tells search engines not to list the page. The page still works. |
| site-wide link | a link in the header or footer that appears on every page. Search engines treat the target as more important. |
