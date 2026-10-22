---
tags: [nav-optimization]
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Please optimize the navigation menu of our Shopify store Northwind Menswear. The work directory is the current directory. inputs/ holds the brief, product counts, a 12-month Search Console page export, a GA4 pages-and-screens export and a competitors list. work/menu_current.json is the captured current menu. Do not scrape competitor sites in this run; fill the competitor matrix with "not captured" and a reason. There are no DataForSEO credentials. At each of the three stops, take the recommended option and continue. Generate the full delivery package in deliver/ in English.
Input files: brief.md, product_counts.csv, gsc_pages.csv, ga4_pages.csv, competitors.txt, menu_current.json
