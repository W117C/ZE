#!/bin/bash
set -e

echo "========================================"
echo "  W117C OpenClaw Workspace - 安装脚本"
echo "========================================"

# 检测系统
OS=$(uname -s)
echo "检测到系统: $OS"

# 检查 Python
if ! command -v python3 &>/dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python: $PYTHON_VERSION"

# 检查 Node.js
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
fi

# 1. 安装 Python 依赖
echo ""
echo "📦 安装 Python 依赖..."
pip3 install akshare pandas --quiet 2>/dev/null || pip3 install akshare pandas --user --quiet 2>/dev/null || {
    echo "⚠️ pip3 安装失败，请手动运行: pip3 install akshare pandas"
}

# 2. 安装 OpenClaw skills
if command -v openclaw &>/dev/null; then
    echo ""
    echo "🔧 安装 Skills 到 OpenClaw..."
    
    # 查找 skills 目录
    SKILLS_DIR="./skills"
    OPENCLAW_SKILLS_DIR="$HOME/.openclaw/skills"
    
    if [ -d "$SKILLS_DIR" ]; then
        mkdir -p "$OPENCLAW_SKILLS_DIR"
        for skill in "$SKILLS_DIR"/*/; do
            SKILL_NAME=$(basename "$skill")
            if [ -f "$skill/SKILL.md" ]; then
                cp -r "$skill" "$OPENCLAW_SKILLS_DIR/"
                echo "  ✅ $SKILL_NAME"
            fi
        done
    fi
    
    # 安装 config 目录的 skills
    if [ -d "./openclaw-config/skills" ]; then
        for skill in "./openclaw-config/skills"/*/; do
            SKILL_NAME=$(basename "$skill")
            if [ -f "$skill/SKILL.md" ]; then
                cp -r "$skill" "$OPENCLAW_SKILLS_DIR/"
                echo "  ✅ $SKILL_NAME (from config)"
            fi
        done
    fi
    
    # 复制 workspace 配置
    if [ -d "./workspace" ]; then
        cp ./workspace/*.md "$HOME/openclaw/workspace/" 2>/dev/null || {
            mkdir -p "$HOME/openclaw/workspace"
            cp ./workspace/*.md "$HOME/openclaw/workspace/"
        }
        echo "  ✅ Workspace 配置已复制"
    fi
    
    echo ""
    echo "🚀 安装完成！重启 OpenClaw 即可使用。"
    echo "   运行: openclaw gateway restart"
else
    echo ""
    echo "⚠️ OpenClaw 未安装"
    echo ""
    echo "请先安装 OpenClaw:"
    echo "  npm install -g openclaw"
    echo ""
    echo "或者手动安装 Skills："
    echo "  cp -r skills/* ~/.openclaw/skills/"
    echo "  cp -r openclaw-config/skills/* ~/.openclaw/skills/"
fi

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
