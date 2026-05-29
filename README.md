# SwiftCart 新用户转化与留存诊断

一个围绕即时零售新用户首单转化、交易后段流失、供给缺货归因与 AB 实验验证的端到端数据分析项目。

本项目基于 Instacart 公开学习数据结构进行业务 Mock 与指标建模，构造 SwiftCart 即时零售场景下的用户行为链路，并通过 DuckDB、Python、SQL 和前端看板完成从数据生产到业务汇报的完整闭环。

## 项目概览

项目核心问题：

> 2026 年 4 月 21 日至 4 月 26 日期间，SwiftCart 新用户首单支付率与 D1 留存率出现同步下探。我们需要判断这是流量质量问题、漏斗链路问题，还是供给缺货问题，并验证可落地的优化策略。

分析链路：

```text
数据清洗与造数 -> 指标计算 -> 总览异动识别 -> 渠道诊断 -> 漏斗下钻 -> 库存/城市交叉验证 -> AB实验评估 -> 行动建议
```

## 核心发现

- 大盘新用户规模整体稳定，异常主要体现在首单支付率和 D1 留存率下探。
- 信息流渠道A是后段支付率下降和留存质量下滑的主要责任渠道。
- 漏斗断点集中在交易后段，尤其是“结算 -> 支付”环节。
- Top20 爆款 SKU 缺货率在异常期明显抬升，北京、杭州风险最集中。
- “智能替代品推荐 + 补偿券”实验组相对原策略表现出显著正向改善，全量口径首单支付率绝对提升 +15.43%。

## 关键指标

| 指标 | 数值 | 说明 |
| --- | ---: | --- |
| 新用户数 | 479,680 | 2026-04-01 至 2026-04-30 发生曝光行为的去重用户 |
| 首单支付率 | 4.85% | 首单支付用户 / 新用户 |
| 结算 -> 支付转化率 | 67.21% | 支付链路去重用户 / 结算链路去重用户 |
| D1 留存率 | 16.60% | 次日活跃用户 / 当日新增用户 |
| Top20 缺货率变化 | 31.99% -> 37.31% | 正常期 vs 异常期 |
| 北京 Top20 缺货率 | 49.44% | 异常期城市维度 |
| 杭州 Top20 缺货率 | 48.22% | 异常期城市维度 |
| AB 首单绝对提升 | +15.43% | Treatment ALL - Control ALL |

## 看板页面

| 页面 | 文件 | 说明 |
| --- | --- | --- |
| 01 Overview | `dashboards/html/index.html` | 大盘总览，识别异常是否存在 |
| 02 Channel | `dashboards/html/channel.html` | 渠道诊断，定位责任渠道 |
| 03 Funnel | `dashboards/html/funnel.html` | 漏斗与交易后段诊断 |
| 04 Supply | `dashboards/html/supply.html` | 库存供给证据链 |
| 05 Experiment & Action | `dashboards/html/experiment_action.html` | AB 实验验证与行动建议 |

## 看板预览

| 页面 | PNG 预览 | 
| --- | --- | 
| 增长总览 | `images/dashboard/01_overview.png` |
| 渠道诊断 | `images/dashboard/02_channel.png` |
| 漏斗下钻 | `images/dashboard/03_funnel.png` |
| 供给证据链 | `images/dashboard/04_inventory.png` |
| 实验与行动 | `images/dashboard/05_experiment_action.png` |

## 目录结构

```text
.
├── README.md
├── docs/
│   ├── 指标口径字典.md
│   └── 项目复现指南.md
├── sql/
│   ├── 05_duckdb_final_marts.sql
│   └── quickmart_all_marts.sql
├── data_samples/
│   └── aggregated_dashboard_csv/
├── dashboards/
│   └── html/
├── images/
│   └── dashboard/
├── scripts/
│   └── render_static_dashboard_exports.py
```

## 技术栈

- Python / Pandas / NumPy：业务行为日志 Mock、AB 实验数据生成、数据质量校验
- DuckDB / SQL：内存级聚合计算与 Data Mart 生产
- ECharts / Tailwind CSS：单文件 HTML 商业看板
- Two-Proportion Z-Test：AB 实验双样本比例检验
- Dashboard Storytelling：总览、诊断、归因、验证、行动的分析叙事

## 可复用 Skill

本项目内置了一套可复用 Codex skill：

```text
skills/swiftcart-bi-project/
```

它沉淀了本项目的 BI 交付流程，包括业务问题澄清、指标口径统一、看板页面取舍、GitHub 目录整理、截图/PDF 导出和交付校验。后续做类似“零售增长诊断 / 漏斗归因 / AB 实验验证”的作品集项目时，可以复用这套 skill 的流程，如需skill请联系我lc20010418@163.com。

## 数据说明

本仓库仅公开聚合后的 Data Mart 样例数据，不包含原始订单明细、用户行为明细或任何可还原单个用户行为路径的数据、SQL、HTML 看板、截图和 PDF。
如需复现完整链路，可参考 `docs/项目复现指南.md`。
