# Menu JSON and mockup

One JSON schema serves three uses: the captured current menu (`work/menu_current.json`), the proposed menu (`deliver/menu_proposed.json`) and the data inside the mockup.

## Schema

```json
{
  "brand": "STORE NAME",
  "utility": ["Track Order", "Membership"],
  "items": [
    {
      "label": "TOPS",
      "href": "/collections/tops",
      "count": 799,
      "direct": false,
      "cols": [
        {
          "title": "Tops",
          "href": "/collections/tops",
          "items": [
            {"label": "Shirts", "href": "/collections/shirts", "count": 375},
            {"label": "Polo Shirts", "href": "/collections/polos", "count": 82, "tag": "chg"}
          ],
          "article": {"label": "Types of Shirts for Men", "href": "/blogs/guides/types-of-shirts"}
        }
      ],
      "article": {"label": "Fall Wardrobe: What to Buy First", "href": "/blogs/guides/fall-wardrobe"}
    },
    {"label": "BEST SELLERS", "href": "/collections/best-sellers", "count": 216, "direct": true}
  ],
  "footer": [
    {"title": "About", "items": [{"label": "About us", "href": "/pages/about"}]}
  ]
}
```

Field rules:

- `items` is the top-level list in display order. Ten entries at most.
- `direct: true` means a link without a dropdown. Such an entry has no `cols`.
- `cols` is the list of columns inside the dropdown. Each column has a `title`, an optional `href`, and `items`. One column holds at most ten items.
- `tag` is `new` for an entry that did not exist, `chg` for a renamed or retargeted entry. Omit it for an unchanged entry.
- `count` is the product count. Omit it for a page that is not a category.
- `article` is an optional link to one content page. It shows at the end of a column or a dropdown.
- `footer` is a list of columns with the same shape as `cols`.

The page derives the mobile drawer from the same data. The first level is `items`. The second level lists each column's items under a small heading.

## Build the mockup

```bash
python3 scripts/inject_mockup.py --menu deliver/menu_proposed.json --lang zh --out deliver/mockup.html
```

The script does four things. It validates the JSON against the rules above. It picks the UI strings for the language. It writes the data into the template placeholder. It saves a self-contained HTML file. Open the file by double-clicking. It needs no network.

Do not edit the HTML by hand. Change the JSON and run the script again.

## Capturing the current menu into the schema

From a Firecrawl or browser capture, list every top-level label, its dropdown columns and items, with hrefs as site-relative paths. Put the desktop structure in `items`. In `work/menu_capture_notes.md`, note whether the mobile first level matches the desktop one and how many taps a category takes today.
