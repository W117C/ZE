---
name: quant-fund-analysis
description: Use when the user asks for quantitative fund analysis, CTA or quant private fund or hedge fund research, strategy comparison, factor logic, fund due diligence framing, manager evaluation, risk-return review, portfolio construction, or scoring and rating. Implements Quant Fund OS with 4-layer architecture (Data to Analysis to Scoring to Decision), 10-point scoring system with 7 dimensions, A/B/C rating, anti-cyclic portfolio construction, DD framework, and red flag detection. Not for guaranteed return claims, 内幕信息, or unsupported price predictions.
---

# Quant Fund OS

## Overview

机构级量化基金操作系统：基金分析 + 筛选 + 打分 + 组合配置 + 决策输出。

## Architecture

```
数据层 - 分析层 - 评分层 - 决策层
```

## Quick Start

单只基金分析（完整）：
```bash
python3 scripts/analyze_single_fund.py --name "某CTA基金" --strategy CTA --annual-return 18 --max-dd 9 --vol 11 --sharpe 1.2 --calmar 2.0 --win-rate 55 --profit-loss-ratio 1.5 --aum 500 --fee 1.5
```

批量基金对比：
```bash
python3 scripts/compare_funds.py --json-file ./funds.json
```

组合配置：
```bash
python3 scripts/portfolio_builder.py --cta 0.25 --market-neutral 0.25 --long-only 0.25 --arbitrage 0.15 --cash 0.10
```

生成尽调问题：
```bash
python3 scripts/generate_dd_questions.py --strategy market-neutral
```

## Scoring System (10分制)

| 维度 | 权重 |
|------|------|
| 收益质量 | 20% |
| 回撤控制 | 20% |
| 稳定性 | 20% |
| 可解释性 | 15% |
| 容量 | 10% |
| 管理人 | 10% |
| 费用 | 5% |

## Rating

| 等级 | 标准 |
|------|------|
| A | ≥8.5 |
| B | 7–8.5 |
| C | <7 |

## Output Template

```
【结论】
【评分】
【收益来源】
【风险】
【稳定性】
【可投资性】
【待验证】
【下一步】
```

## Resources

### scripts/
- `analyze_single_fund.py`: 完整分析 + 评分 + 评级
- `compare_funds.py`: 多基金横向对比
- `generate_dd_questions.py`: 管理人尽调问题清单
- `portfolio_builder.py`: 抗周期组合构建器

### references/
- `metrics.md`: 指标解释与误用提醒
- `dd-checklist.md`: 尽调问题与红旗项
- `scoring-rubric.md`: 评分标准详解
- `portfolio-theory.md`: 组合配置逻辑
