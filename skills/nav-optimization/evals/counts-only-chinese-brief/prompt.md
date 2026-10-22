---
tags: [nav-optimization]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

帮我优化 Northwind 这个男装站的导航栏。工作目录就是当前目录，inputs 里有甲方要求、每个分类页的商品数，work 里有抓好的现有菜单 menu_current.json。没有 Search Console 和 GA4 数据，也没有 DataForSEO，竞对你按行业默认选，不用真的去抓，三个停点你都按推荐项直接往下走，最后把交付包生成到 deliver。
Input files: brief.md, product_counts.csv, menu_current.json
