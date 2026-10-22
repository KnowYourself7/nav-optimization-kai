# Competitor matrix

One table. One row per dimension, one column per competitor, and a last column for the practice that at least two brand sites share.

## How to pick competitors

Pick three to five sites. Spread them across tiers so that a pattern is not an artifact of catalog size:

- one or two mass-market brands
- one or two direct-to-consumer brands
- one mid-price brand
- at most one marketplace, marked "reference only", because its catalog is far larger than a brand store

Record each pick and each rejection with a reason. If a site blocks capture, list it as "not captured" with the reason.

## How to capture

Capture the desktop menu and the mobile menu for each site. Use Firecrawl MCP `firecrawl_scrape` with JavaScript rendering. If the site blocks it, use the built-in browser. If both fail, ask the user for a screenshot or the menu text. Save the raw capture under `work/competitors/<site>/` and note the capture date.

JavaScript often renders the menu. A capture without rendering returns an empty header.

## The seven dimensions

| Dimension | What to write |
|---|---|
| Top-level items and order | the labels in order, and how many are product entries |
| Items per level | the count of the largest column or group |
| Grouping axis | product type, occasion, material, collection, promo, or a mix |
| Attributes as filters or categories | whether color, material and fit appear as menu items or as filter links |
| Mobile first level | whether product categories appear on the first level of the hamburger menu, or "not verified" |
| Sale handling | a permanent top-level Sale, a Sale inside a group, or none, and how the site subdivides it |
| New-arrivals handling | a top-level entry, subdivided by category or by season, mixed with promos or not |

## Reading the matrix

If at least two brand sites agree, write "reference" in the last column. The marketplace does not vote. Note a practice found on one site. Do not adopt it.

Keep the matrix as `work/competitor_matrix.csv`. The first column is the dimension. The next columns are the sites. The last column is the shared practice.
