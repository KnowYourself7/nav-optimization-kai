# Fallbacks for missing inputs

Each optional input has one fallback. Apply it. Say so in the inventory and in the proposal's data-sources table. Never fill the gap with an estimate.

| Missing input | Fallback | What the proposal says |
|---|---|---|
| `inputs/gsc_pages.csv` | Skip the "traffic but no entry" search. Remove entries on the product rule only. Mark retarget candidates `pending`. | "Search Console data was not available. Only pages with fewer than 10 products lost their entry." |
| `inputs/ga4_pages.csv` | Do not remove entries for low views. Mark them `pending` with the recommendation. | "GA4 data was not available. Low-traffic candidates are listed as pending." |
| DataForSEO (no MCP tool and no credentials) | Keep the current label. Write `not checked` in `search_volume`. List the candidates under client decisions. | "Search volume was not checked. Label candidates are listed for a later check." |
| `inputs/competitors.txt` | Propose three to five sites by tier at STOP 1. | The competitors table names the picks and the reasons. |
| A competitor site blocks capture | List it as "not captured" with the reason. If fewer than three sites remain, pick a replacement in the same tier. | The competitors table names the sites that were not captured. |
| Mobile menu capture fails | Mark the mobile dimension "not verified" for that site. For the client's own site, ask the user for a screenshot. | The matrix shows "not verified". |
| Blog or content pages in the menu but not in the exports | Keep the content section without traffic numbers. Ask for an export filtered to the content path. | "Content pages had no data in the exports." |

## Export formats the scripts accept

Search Console page export: a CSV with a page column (`Top pages`, `Page`, or the Chinese header), a clicks column and an impressions column. The script matches headers without regard to case and strips thousands separators.

GA4 "Pages and screens" export: a CSV that can start with comment lines beginning with `#`. The script skips them and reads the page path column, views and key events. Locale-prefixed paths such as `/de/collections/x` are folded into the base path.

Product counts: `url,product_count`. For a Shopify store the user can produce it with the collection `products.json` endpoint. If the brief names Shopify, offer this command. Tell the user that some stores rate-limit the endpoint.

```bash
for h in shirts pants; do n=$(curl -s "https://example.com/collections/$h/products.json?limit=250" | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["products"]))'); echo "/collections/$h,$n"; done
```
