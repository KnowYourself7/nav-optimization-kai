# nav-optimization skill 设计

日期：2026-10-22。状态：已和 Kai 逐段确认。来源：Coofandy 导航栏优化项目（2026-10-15 至 10-17）的完整工作流。

## 目标

给一个已有的电商站，只改导航菜单的分组、顺序、命名和入口，让它接近电商导航的最佳实践；每一处改动都有数据和竞对依据，能直接交给客户拍板和实施。

## 已定的决定

| 事项 | 决定 |
|---|---|
| 形态 | 独立插件仓库 nav-optimization-kai，一个 skill，名 nav-optimization（避开 claude 保留字） |
| 范围 | 只改菜单；动页面、商品、网址的事全部进“需要客户决定”清单 |
| 平台 | 平台无关；商品数由用户提供 CSV，Shopify 站附一段生成命令 |
| 必须输入 | 甲方要求文件；商品数表 |
| 可选输入 | Search Console 导出、GA4 网页和屏幕报表、DataForSEO、竞对名单，各有固定降级 |
| 抓取 | Firecrawl 优先，内置浏览器备用，都失败让用户粘菜单文字 |
| 产物 | README、方案书、HTML 示意页、改动表 CSV，加中间产物进 appendix |
| 停点 | 三个：清点与竞对名单后；改动表草案后；交付前 |
| 语言 | 跟甲方要求文件，模板中英两套；菜单项名称保留站点原文 |
| 架构 | 单 skill + references + scripts + assets，判断在主会话，脚本只做确定性的事 |

## 验收标准

产物合格：每个菜单项指向已存在页面；不新建、删除、改网址；顶栏和任一下拉栏不超过 10 项；手机端一级是品类，任何分类页两次点击可达；改动表每行有原位置、新位置、商品数、改动类型、理由；方案书每节有现状到改成的树和五列表；客户决策事项只在最后一节。
流程合格：三个停点都停过并记录裁定；缺数据处标“缺什么、怎么降级”，不填估计值；产物里没有凭据。
验收脚本查能查的项，其余在停点三人工过。

## 输入与降级

| 输入 | 必须 | 缺了怎么办 |
|---|---|---|
| 甲方要求（站点、问题、不能动的、语言） | 是 | 停下来问 |
| 商品数表（网址、商品数） | 是 | 停下来要 |
| Search Console 按页面导出 | 否 | 不做“有流量没入口”查找，删入口只按商品数 |
| GA4 网页和屏幕报表 | 否 | 不删“没人看”的项，只标待定 |
| DataForSEO（MCP 优先，REST 备用，凭据读环境变量） | 否 | 改名项标“待查” |
| 竞对名单 3 到 5 家 | 否 | 按行业默认选，停点一确认 |

## 产物与目录

```
<工作目录>/
  inputs/     甲方要求、商品数表、GSC、GA4 导出
  work/       现状菜单表.csv、竞对菜单矩阵.csv、搜索量表.csv、菜单抓取记录
  deliver/    README、方案书.md、示意页.html、改动表.csv、appendix/（中间产物）
  history/    每次运行的数据快照和裁定
```

方案书结构：文档信息表、一页摘要、总览（原则、改动汇总、数据来源、竞对）、按顶栏一级一节（树 + 五列表 + 三句好处）、需要客户决定的事项（补货建页、重复页合并、内容、结构模板、备选验证）、实施与验证、依据出处、术语表。
示意页：自包含 HTML，菜单数据是文件内一个 JSON，skill 只改 JSON；桌面悬停展开，手机两层抽屉，页脚带标记。
改动表：14 列，与 Coofandy v5 改动表一致。

## 流程

1. 清点：读必须输入，查可选输入，抓现有菜单桌面和手机版，出输入清单和竞对候选。停点一。
2. 现状表：合并商品数、搜索点击、浏览、关键事件，自动打四种标记（不足 10 件、某级超 10 项、表头错链、同网址两处）。
3. 竞对矩阵：每家抓桌面和手机，七个维度，两家以上一致标“可参考”。
4. 方案草案：按四条原则套改动规则生成改动表；改名项查搜索量；定不了的汇成“待定”清单附推荐。停点二。
5. 成稿：生成四件交付物，跑验收脚本。停点三。
6. 归档：数据快照和裁定进 history。

## 质检

脚本：网址存在、项数上限、必填列非空、方案书每节结构、无凭据字符串。数据对账：改动表数字抽查 20 行回溯到中间表。人工：停点三读一页摘要和任意两节。

## 禁止

不改网址；不建议新建或删除页面（只进最后一节）；少于 10 件不进菜单；公司页和内容页不占顶栏除非甲方要求；属性不做分类；竞对做法必须有抓取记录；没数据的判断标待定；不打印不存凭据；正文不混客户决策事项；数字不估算。

## 架构（做法一）

```
nav-optimization-kai/
  .claude-plugin/plugin.json
  skills/nav-optimization/
    SKILL.md                      流程、停点、禁止清单，300 行内
    references/
      principles.md               四条原则与阈值（Baymard、Google 出处）
      competitor-matrix.md        七个维度与填法
      change-rules.md             升一级、改名、新增、删除、移位、进页脚的判定规则
      deliverable-templates.md    方案书与 README 结构（中英）
      mockup.md                   示意页 JSON 结构与注入方法
      degradation.md              每种缺失输入的降级
    scripts/
      inventory.py                输入清点与清单
      parse_menu.py               抓取结果解析成现状表
      search_volume.py            DataForSEO 查询（MCP 不可用时）
      inject_mockup.py            把菜单 JSON 写进示意页
      verify.py                   验收脚本
    assets/
      mockup-template.html
      proposal-template.zh.md / proposal-template.en.md
      readme-template.zh.md / readme-template.en.md
  docs/plans/                     设计与计划
  tests/
```

依据：Agent Skills 规范（目录约定、frontmatter、500 行、引用一层）；Claude 平台 Skill authoring best practices（脚本解决不推诿、工作流清单加校验回路、评测先行）；Claude Code Skills 与 Plugins 文档（frontmatter 字段、plugin.json）。改 skill 前按 essentials/skill-dev-sources.md 核对，铁律第 15 条。
