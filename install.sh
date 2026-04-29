#!/bin/bash
set -e

echo "========================================"
echo "  W117C OpenClaw Workspace - 安装脚本"
echo "========================================"
echo ""

# ========== 1. 系统检测 ==========
OS=$(uname -s)
echo "🖥️  系统: $OS"

# 检查 Node.js
if ! command -v node &>/dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js 18+"
    echo "   推荐: https://nodejs.org/"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✅ Node.js: $NODE_VERSION"

# 检查 npm
if ! command -v npm &>/dev/null; then
    echo "❌ 未找到 npm"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo "✅ npm: $NPM_VERSION"

# 检查 Python
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Python: $PYTHON_VERSION"
fi

# ========== 2. 安装 OpenClaw ==========
echo ""
echo "📦 检查 OpenClaw..."
if command -v openclaw &>/dev/null; then
    OC_VERSION=$(openclaw --version 2>/dev/null || echo "unknown")
    echo "✅ OpenClaw 已安装: $OC_VERSION"
else
    echo "⬇️  正在安装 OpenClaw..."
    npm install -g openclaw --quiet 2>&1 | tail -3
    if command -v openclaw &>/dev/null; then
        OC_VERSION=$(openclaw --version 2>/dev/null)
        echo "✅ OpenClaw 安装完成: $OC_VERSION"
    else
        echo "❌ OpenClaw 安装失败，请手动运行: npm install -g openclaw"
        exit 1
    fi
fi

# ========== 3. 安装 Python 依赖 ==========
echo ""
echo "📦 安装 Python 依赖（akshare / pandas）..."
pip3 install akshare pandas --quiet 2>/dev/null || \
pip3 install akshare pandas --user --quiet 2>/dev/null || \
echo "⚠️ pip3 安装失败，请手动运行: pip3 install akshare pandas"

# ========== 4. 安装 Skills ==========
echo ""
echo "🔧 安装 Skills..."

OPENCLAW_SKILLS_DIR="$HOME/.openclaw/skills"
mkdir -p "$OPENCLAW_SKILLS_DIR"

SKILL_COUNT=0
for src in "./skills" "./openclaw-config/skills"; do
    if [ -d "$src" ]; then
        for skill in "$src"/*/; do
            SKILL_NAME=$(basename "$skill")
            if [ -f "$skill/SKILL.md" ]; then
                cp -rf "$skill" "$OPENCLAW_SKILLS_DIR/"
                echo "  ✅ $SKILL_NAME"
                SKILL_COUNT=$((SKILL_COUNT + 1))
            fi
        done
    fi
done
echo "   共安装 $SKILL_COUNT 个 Skills"

# ========== 5. 安装 OpenClaw 系统设置 ==========
echo ""
echo "🔧 安装 OpenClaw 系统设置..."

if [ -d "./openclaw-settings" ]; then
    # cron
    if [ -f "./openclaw-settings/cron/jobs.json" ]; then
        mkdir -p "$HOME/.openclaw/cron"
        cp -f ./openclaw-settings/cron/jobs.json "$HOME/.openclaw/cron/"
        echo "  ✅ cron/jobs.json"
    fi
    
    # systemd
    if [ -f "./openclaw-settings/systemd/openclaw-gateway.service" ]; then
        mkdir -p "$HOME/.config/systemd/user"
        cp -f ./openclaw-settings/systemd/openclaw-gateway.service "$HOME/.config/systemd/user/"
        echo "  ✅ systemd service"
    fi
    
    # exec-approvals
    if [ -f "./openclaw-settings/exec-approvals.json" ]; then
        cp -f ./openclaw-settings/exec-approvals.json "$HOME/.openclaw/"
        echo "  ✅ exec-approvals.json"
    fi
    
    # 环境变量（写入 .bashrc）
    if [ -f "./openclaw-settings/env/openclaw.env" ]; then
        if ! grep -q "OPENCLAW_HOME" "$HOME/.bashrc" 2>/dev/null; then
            echo "" >> "$HOME/.bashrc"
            echo "# OpenClaw Environment (auto-added by install.sh)" >> "$HOME/.bashrc"
            cat ./openclaw-settings/env/openclaw.env >> "$HOME/.bashrc"
            echo "  ✅ 环境变量 → .bashrc"
        else
            echo "  ⏭️  环境变量已存在"
        fi
    fi
fi

# ========== 6. 安装主配置文件 ==========
echo ""
echo "🔧 安装主配置..."

if [ -f "./openclaw-config/openclaw.json" ]; then
    cp -f ./openclaw-config/openclaw.json "$HOME/.openclaw/openclaw.json"
    echo "  ⚠️  openclaw.json（请替换 token 为你自己的）"
fi

# ========== 7. 安装 Workspace 配置 ==========
echo ""
echo "🔧 安装 Workspace 配置..."

WORKSPACE_DIR="$HOME/openclaw/workspace"
mkdir -p "$WORKSPACE_DIR"

if [ -d "./workspace" ]; then
    cp -rf ./workspace/*.md "$WORKSPACE_DIR/" 2>/dev/null && echo "  ✅ 配置文件 (*.md)"
    if [ -d "./workspace/memory" ]; then
        cp -rf ./workspace/memory "$WORKSPACE_DIR/" 2>/dev/null && echo "  ✅ memory/"
    fi
    if [ -d "./workspace/reports" ]; then
        cp -rf ./workspace/reports "$WORKSPACE_DIR/" 2>/dev/null && echo "  ✅ reports/"
    fi
fi

# ========== 8. 完成 ==========
echo ""
echo "========================================"
echo "  🎉 安装完成！"
echo "========================================"
echo ""
echo "下一步："
echo "  1. 编辑 ~/.openclaw/openclaw.json，替换 token"
echo "  2. 运行: openclaw gateway restart"
echo "  3. 测试: ./test.sh"
echo "  4. 启动模拟炒股: ./start.sh"
