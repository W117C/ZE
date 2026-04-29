# W117C · OpenClaw Workspace

严谨专业版 AI 助理的完整工作空间，开箱即用。

## 快速开始

### 一键安装
```bash
git clone https://github.com/W117C/ZE.git w117c
cd w117c
./install.sh
```

### 手动安装
```bash
# 1. 克隆仓库
git clone https://github.com/W117C/ZE.git w117c
cd w117c

# 2. 安装 Python 依赖
pip3 install akshare pandas

# 3. 安装 Skills（如果已有 OpenClaw）
cp -r skills/* ~/.openclaw/skills/
cp -r openclaw-config/skills/* ~/.openclaw/skills/

# 4. 复制工作空间配置
cp -r workspace/* ~/openclaw/workspace/

# 5. 重启 OpenClaw
openclaw gateway restart
```

### 测试安装
```bash
./test.sh
```

### 启动模拟炒股
```bash
./start.sh
```

## 目录结构

```
├── install.sh              # 一键安装脚本
├── start.sh                # 启动模拟炒股
├── test.sh                 # 测试所有模块
├── README.md               # 本文档
│
├── openclaw-config/        # OpenClaw 完整配置
│   ├── openclaw.json       # 主配置文件（需替换token）
│   ├── cron/               # 定时任务配置
│   └── skills/             # 全部已安装的 Skills（40+）
│
├── skills/                 # 核心开发模块（带完整代码）
│   ├── auto-sim-trading/   # 自动模拟炒股系统
│   ├── trading-agents-framework/  # 多Agent交易框架
│   ├── quant-fund-analysis/  # 量化基金分析
│   └── finance-data/       # A股金融数据获取
│
├── workspace/              # 工作空间配置
│   ├── SOUL.md             # 人格定义
│   ├── USER.md             # 用户信息
│   ├── TOOLS.md            # 工具笔记
│   └── AGENTS.md           # Agent行为规则
│
├── reports/                # 分析报告
└── config/                 # 脱敏配置示例
```

## 核心模块

### 1. Auto Sim Trading（自动模拟炒股）
- 虚拟账户管理（资金/净值/回撤跟踪）
- 全市场扫描 + 多因子评分
- 自动交易决策（买入/卖出/止损/止盈）
- 日报生成 + 自我反思引擎
- 定时任务（每日15:30自动运行）

**快速使用**：
```bash
python3 skills/auto-sim-trading/scripts/run_real_sim.py --top 10
```

### 2. Trading Agents Framework
- 多 Agent 会话链（Bull/Bear/Trader/Risk/Manager）
- 东方财富股吧情绪分析（A股实时）
- 基本面/技术面/新闻分析
- 组合优化（等权/风险平价/夏普最大化）

**快速使用**：
```bash
python3 skills/trading-agents-framework/scripts/build_sentiment_context.py --symbol 600519
```

### 3. Quant Fund Analysis
- 基金持仓分析
- 组合评级与建议

**快速使用**：
```bash
python3 skills/quant-fund-analysis/scripts/analyze_single_fund.py 000216
```

### 4. Finance Data
- A股实时数据获取
- 历史行情/新闻/公告

**快速使用**：
```bash
python3 skills/finance-data/tools/stock_query.py 600519
```

## 已安装的 Skills（40+）
- **自定义**：auto-sim-trading、trading-agents-framework、quant-fund-analysis、finance-data
- **官方/社区**：2nd-brain、academic-deep-research、agent-browser、agent-evolver、agent-reach、a-share-real-time-data、canary、close-loop、copywriting、csvtoexcel、daily-news、docx、elite-longterm-memory、error-driven-evolution、failure-memory、find-skills、humanize-chinese、moltguard、office-document-specialist-suite、ontology、pdf、pua、qoderwork-ppt、self-evolve、session-logs、systematic-debugging、thesethrose-agent-browser、travel-planner、using-superpowers、waiy-browser、weather、xlsx、zero-rules

## 系统要求
- Python 3.10+
- Node.js（如果使用 OpenClaw）
- 网络访问（获取金融数据）

## 注意事项
- `openclaw.json` 中的 token 需要替换为你自己的
- 首次运行 `akshare` 会下载依赖，可能需要几分钟
- 模拟炒股系统仅用于研究，不构成投资建议

## 许可证
MIT
