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

# 5. 复制 OpenClaw 完整配置
cp openclaw-settings/cron/jobs.json ~/.openclaw/cron/
cp openclaw-settings/systemd/openclaw-gateway.service ~/.config/systemd/user/

# 6. 重启 OpenClaw
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
├── openclaw-config/        # OpenClaw Skills 配置（40+ 个）
│   ├── openclaw.json       # 主配置文件（需替换token）
│   ├── cron/               # 定时任务配置
│   └── skills/             # 全部已安装的 Skills
│
├── openclaw-settings/      # OpenClaw 完整系统设置
│   ├── README.md           # 配置说明
│   ├── cron/               # 定时任务 + 执行记录
│   ├── devices/            # 设备配对信息
│   ├── identity/           # 设备认证
│   ├── logs/               # 配置审计日志
│   ├── subagents/          # 子代理运行记录
│   ├── systemd/            # Gateway 服务配置
│   ├── env/                # 环境变量
│   ├── jvs-claw/           # 系统激活脚本
│   ├── exec-approvals.json # 执行审批
│   └── lock.json           # ClawHub 锁
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
│   ├── AGENTS.md           # Agent行为规则
│   ├── HEARTBEAT.md        # 心跳配置
│   ├── IDENTITY.md         # 身份定义
│   └── memory/             # 记忆日志
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

## OpenClaw 完整设置

`openclaw-settings/` 目录包含**所有 OpenClaw 配置**：

| 文件/目录 | 内容 |
|-----------|------|
| `cron/` | 3 个定时任务 + 执行记录 |
| `devices/` | 设备配对信息 |
| `identity/` | 设备认证（device.json / device-auth.json） |
| `logs/` | 配置审计日志 |
| `subagents/` | 子代理运行记录 |
| `systemd/` | Gateway 服务配置 |
| `env/` | 环境变量（OPENCLAW_HOME/PORT 等） |
| `jvs-claw/` | 激活脚本（activate.sh / env.sh） |
| `exec-approvals.json` | 执行审批记录 |
| `openclaw.json` | 主配置（仓库根目录 openclaw-config/） |

## 系统要求
- Python 3.10+
- Node.js（用于 OpenClaw）
- 网络访问（获取金融数据）

## 注意事项
- `openclaw.json` 中的 token 需要替换为你自己的
- 首次运行 `akshare` 会下载依赖，可能需要几分钟
- 模拟炒股系统仅用于研究，不构成投资建议

## 许可证
MIT
