# Change rules

Apply the rules in this order to every row of `work/current_menu_table.csv`. Then apply them to every page with traffic that has no entry. Write the result to `deliver/changes.csv`.

## Contents

- The 14 columns
- Change types
- Rules by change type
- Pages with traffic but no entry
- Duplicate pages
- Open decisions

## The 14 columns

| Column | Content |
|---|---|
| `top_level` | the proposed top-level item, or `removed`, or `footer` |
| `group` | the proposed column or group inside the dropdown, or empty |
| `item` | the proposed label |
| `old_location` | where the item sits today, as `TOP > group > item`, or `not in menu` |
| `old_label` | the current label. Empty for a new entry. |
| `new_label` | the proposed label |
| `href` | the existing page path |
| `product_count` | from `inputs/product_counts.csv` |
| `gsc_clicks` | 12-month clicks, or `no data` |
| `ga4_views` | 12-month views, or `no data` |
| `ga4_key_events` | 12-month key events, or `no data` |
| `search_volume` | monthly volume of the label candidates, or `not checked` |
| `change_type` | one of the types below |
| `reason` | one sentence with the numbers that decided it. If the user made a ruling, add it here. |

## Change types

The types are `keep`, `rename`, `move`, `promote`, `add`, `remove`, `merge`, `retarget` and `footer`. Promote means a move to the top level. Add means a new entry for an existing page. Remove means the entry goes, never the page. Retarget means the same label points at a better page.

## Rules by change type

### Promote to top level

If a group is a product type and its product count or its traffic ranks in the site's top five, promote it. Keep the top level at ten items or fewer. If the brief asks for internal links to content, a content group can be promoted too. Otherwise it stays below.

### Rename

Rename in three cases. The search volume of another label is clearly higher. The label is misspelled. The label hides what is inside, for example "Gifts" over an accessories list. If the volumes are close, keep the site's own word. Record both volumes in `search_volume`.

### Move

Move an item to the group where shoppers look for it. Knitwear sits with sweaters. Dress shirts and suit vests sit with tailoring. Promotions sit under Sale. Collaborations sit under new arrivals.

### Add

Add an entry for an existing page in one case. The page has 10 or more products, and its search clicks or views are above the median for menu pages. Write the numbers in the reason.

### Remove

Remove the entry, never the page, in these cases:

- the page has fewer than 10 products
- GA4 is present and 12 months of views and key events are near zero
- the entry is a header link that points to a list-all page
- the same URL already has an entry elsewhere

If only product counts are present, remove on the product rule only. Mark the traffic-based candidates `pending`.

### Merge

If a group encodes an attribute (warehouse, shipping origin), merge it into one entry. Merge several promo entries into Sale.

### Retarget

Two pages can serve the same label. If the page in the menu has far fewer search clicks than the page outside the menu, point the entry at the stronger page. Both pages go to the duplicate list.

### Footer

Company pages (about, story, reviews, certificates, news, loyalty) move to the footer. Competitors keep them in the utility bar or the footer, not in the main menu.

## Pages with traffic but no entry

Join Search Console and GA4 against the menu. List every category page with clicks or views above the median of menu pages and no entry. If the page passes the product rule, it becomes an `add` candidate. If not, it becomes a client decision.

A page with a product count equal to the whole catalog is a campaign landing page, not a category. It never enters the menu. List it under client decisions with the note "noindex, retire after the campaign".

## Duplicate pages

Two pages with near-identical product sets are duplicates. Keep the one with more search clicks and impressions. A redirect transfers that equity, and views from ads or internal links move with the link. Put the pair in the client-decisions table with both pages' product count, clicks, impressions, views and key events side by side.

## Open decisions

These need the user, not data. List each with a recommendation and the numbers:

- a style or trend collection with low traffic that the brand still wants to promote
- whether a content entry keeps a top-level slot
- whether a signature material (for example linen) gets a top-level item or a column inside "Shop by"
- how to split a content dropdown (by product type or by reader task)
- whether to keep ten top-level items or fall back to a plan with one umbrella "Clothing" item
