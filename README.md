# W117C · OpenClaw Workspace

严谨专业版 AI 助理的完整工作空间。

## 快速开始

```bash
git clone https://github.com/W117C/ZE.git w117c
cd w117c
./install.sh
```

## 目录结构

```
├── install.sh              # 一键安装脚本
├── start.sh                # 启动模拟炒股
├── test.sh                 # 测试所有模块
├── README.md               # 本文档
│
├── openclaw-config/        # OpenClaw 配置
│   ├── openclaw.json       # 主配置
│   ├── cron/               # 定时任务
│   └── skills/             # 全部 Skills (38个)
│
├── scripts/                # 核心脚本 (14个)
│   ├── autodream.py        # 记忆自动整合
│   ├── cognitive-kernel-v6.py  # 认知引擎适配
│   ├── error_tracker.py    # 错误追踪
│   ├── intent_classifier.py    # 意图分类
│   ├── kairos_monitor.py   # 主动监控引擎
│   ├── memory_sqlite.py    # SQLite 记忆管理
│   ├── preference_guard.py # 偏好保护
│   ├── reasoning_engine.py # 推理引擎 (5种推理模板)
│   ├── task_planner.py     # DAG 任务分解
│   ├── knowledge_populator.py  # 知识填充
│   ├── self_improvement_engine.py  # 自我改进引擎
│   ├── pattern_learning_engine.py  # 模式学习引擎
│   ├── api-fallback-v5.py  # API 回退健康检查
│   └── cron-governor.py    # Cron 任务治理
│
├── workspace/              # 工作空间
│   ├── SOUL.md             # 人格定义
│   ├── USER.md             # 用户信息
│   ├── AGENTS.md           # Agent 行为规则
│   ├── HEARTBEAT.md        # 心跳配置
│   ├── IDENTITY.md         # 身份定义
│   ├── TOOLS.md            # 工具笔记
│   ├── MEMORY.md           # 长期记忆
│   ├── memory/             # 记忆日志
│   └── reports/            # 报告输出
│
└── config/                 # 脱敏配置
```

## 核心能力

### 📊 Auto Sim Trading
- 虚拟账户管理（资金/净值/回撤跟踪）
- 全市场扫描 + 多因子评分
- 自动交易决策（买入/卖出/止损/止盈）
- 日报生成 + 自我反思引擎

### 🧬 Trading Agents Framework
- 多 Agent 会话链 (Bull/Bear/Trader/Risk/Manager)
- 东方财富股吧情绪分析
- 基本面/技术面/新闻分析
- 组合优化 (等权/风险平价/夏普最大化)

### 📈 Quant Fund Analysis
- 基金持仓分析
- 组合评级与建议
- 每日市场分析报告
- 新闻热点趋势分析

### 🔧 GEP (Genome Evolution Protocol)
- Gene: 可复用策略模板
- Capsule: 验证过的解决方案
- EvolutionEvent: 审计链
- 信号去重 + 变异门控

### 🎯 Smartness Eval
- 11 维度评分，总分 93.31/100 (A+)
- 27/27 测试通过

## Smartness Eval 成绩

| 维度 | 分数 |
|------|------|
| 意图理解 | 100/100 ✅ |
| 安全意识 | 100/100 ✅ |
| 任务路由 | 100/100 ✅ |
| 响应质量 | 100/100 ✅ |
| 鲁棒性 | 100/100 ✅ |
| 延迟 | 50/100 |
| 错误控制 | 59/100 |
| 基础设施 | 100/100 ✅ |
| 知识 | 100/100 ✅ |
| 自我改进 | 100/100 ✅ |
| 模式学习 | 92/100 ✅ |

## 系统要求
- Python 3.10+
- Node.js
- 网络访问（获取金融数据）

## 注意事项
- `openclaw.json` 中的 token 需要替换为你自己的
- 首次运行 `akshare` 会下载依赖，可能需要几分钟
