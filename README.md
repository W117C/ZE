# W117C · OpenClaw Workspace

严谨专业版 AI 助理的完整工作空间。

## 目录结构

```
├── openclaw-config/          # OpenClaw 完整配置
│   ├── openclaw.json         # 主配置文件
│   ├── cron/                 # 定时任务配置
│   ├── devices/              # 设备信息
│   └── skills/               # 所有已安装的 skills
├── skills/                   # 核心开发模块（带代码）
│   ├── auto-sim-trading/     # 自动模拟炒股系统
│   ├── trading-agents-framework/  # 多Agent交易框架
│   ├── quant-fund-analysis/  # 量化基金分析
│   └── finance-data/         # 金融数据获取
├── workspace/                # 工作空间配置
│   ├── SOUL.md               # 人格定义
│   ├── USER.md               # 用户信息
│   ├── TOOLS.md              # 工具笔记
│   └── AGENTS.md             # Agent行为规则
├── reports/                  # 分析报告
└── config/                   # 脱敏配置示例
```

## 核心模块

### 1. Auto Sim Trading（自动模拟炒股）
- 虚拟账户管理（资金/净值/回撤跟踪）
- 全市场扫描 + 多因子评分
- 自动交易决策（买入/卖出/止损/止盈）
- 日报生成 + 自我反思引擎
- 定时任务（每日15:30自动运行）

### 2. Trading Agents Framework
- 多 Agent 会话链（Bull/Bear/Trader/Risk/Manager）
- 东方财富股吧情绪分析（A股实时）
- 基本面/技术面/新闻分析
- 组合优化（等权/风险平价/夏普最大化）

### 3. Quant Fund Analysis
- 基金持仓分析
- 组合评级与建议

### 4. Finance Data
- A股实时数据获取
- 历史行情/新闻/公告

## 已安装的 Skills（完整列表）
- auto-sim-trading（自定义）
- trading-agents-framework（自定义）
- quant-fund-analysis（自定义）
- finance-data（自定义）
- 2nd-brain
- academic-deep-research
- agent-browser
- agent-evolver
- agent-reach
- a-share-real-time-data
- canary
- close-loop
- copywriting
- csvtoexcel
- daily-news
- docx
- elite-longterm-memory
- error-driven-evolution
- failure-memory
- find-skills
- humanize-chinese
- moltguard
- office-document-specialist-suite
- ontology
- pdf
- pua
- qoderwork-ppt
- self-evolve
- session-logs
- systematic-debugging
- thesethrose-agent-browser
- travel-planner
- using-superpowers
- waiy-browser
- weather
- xlsx
- zero-rules
