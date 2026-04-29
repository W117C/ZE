# OpenClaw 完整配置

本目录包含 OpenClaw 的所有配置文件和设置。

## 目录说明

| 目录 | 内容 |
|------|------|
| `cron/` | 定时任务配置和执行记录 |
| `devices/` | 设备配对信息 |
| `identity/` | 设备认证文件 |
| `logs/` | 配置审计日志 |
| `subagents/` | 子代理运行记录 |
| `systemd/` | Gateway 服务配置 |
| `env/` | 环境变量 |
| `jvs-claw/` | 系统激活脚本 |

## 核心文件

- `openclaw.json` — 主配置文件（仓库根目录）
- `exec-approvals.json` — 执行审批记录
- `.clawhub/lock.json` — ClawHub 锁文件

## 使用说明

部署时，将 `cron/jobs.json` 和 `openclaw.json` 复制到：
```bash
~/.openclaw/openclaw.json
~/.openclaw/cron/jobs.json
```

⚠️ **注意**：`openclaw.json` 中的 token 需要替换为你自己的。
