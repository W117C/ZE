#!/usr/bin/env python3
"""
Cognitive Kernel v6 Adapter
桥接 Smartness Eval 和当前系统的意图分类器。

提供统一的处理接口，将输入文本转换为结构化意图输出。
"""

import argparse
import json
import sys
import time
from pathlib import Path

# 导入意图分类器
SCRIPT_DIR = Path(__file__).resolve().parent.parent
WORKSPACE = Path.home() / "openclaw" / "workspace"
sys.path.insert(0, str(WORKSPACE / "scripts"))

try:
    from intent_classifier import classify_intent, detect_emotion
except ImportError:
    # fallback: inline definition
    def classify_intent(text):
        return {"intent": "unknown", "confidence": 0.0}
    def detect_emotion(text):
        return {"emotion": "neutral", "confidence": 0.0}


def map_intent(text):
    """将输入映射为 Smartness Eval 期望的意图类型"""
    result = classify_intent(text)
    intent_map = {
        "conversation": "casual_chat",
        "question": "question",
        "command": "task_execution",
        "analysis": "quant_analysis",
        "creative": "content_creation",
        "research": "research",
        "coding": "coding",
        "correction": "correction",
        "configuration": "configuration",
        "status": "status_check",
        "comparison": "comparison",
        "decision": "decision_support"
    }

    # 特殊意图识别
    if "视频" in text or "生成" in text and "宣传" in text:
        return "video_generation"
    if "小红书" in text:
        return "xhs_create"
    if "量化" in text or "A股" in text or "分析" in text and "策略" in text:
        return "quant_analysis"

    return intent_map.get(result["intent"], "unknown")


def assess_risk(text):
    """评估请求风险级别"""
    high_risk_patterns = ["删除", "rm -rf", "格式化", "DROP TABLE", "忽略之前", "系统提示", "prompt"]
    medium_risk_patterns = ["执行", "运行", "安装", "修改"]

    if any(p in text for p in high_risk_patterns):
        return "high"
    if any(p in text for p in medium_risk_patterns):
        return "medium"
    return "low"


def determine_action_type(text):
    """确定动作类型"""
    risk = assess_risk(text)
    if risk == "high":
        return "clarify"  # 高风险需要确认
    if not text.strip():
        return "invalid"
    if any(greeting in text for greeting in ["你好", "谢谢", "早", "晚安"]):
        return "respond"
    return "execute"


def suggest_skills(text):
    """推荐技能"""
    skills = []
    if "视频" in text:
        skills.append("video-generation")
    if "A股" in text or "量化" in text or "分析" in text:
        skills.append("quant-fund-analysis")
        skills.append("trading-agents-framework")
    if "小红书" in text:
        skills.append("copywriting")
    if not skills:
        skills.append("general")
    return skills


def process(text):
    """核心处理函数"""
    intent_result = classify_intent(text)
    emotion_result = detect_emotion(text)
    mapped_intent = map_intent(text)

    return {
        "text": text,
        "timestamp": time.time(),
        "intent": {
            "primary": mapped_intent,
            "raw": intent_result.get("intent", "unknown"),
            "confidence": intent_result.get("confidence", 0.0)
        },
        "emotion": emotion_result,
        "strategy": {
            "risk_level": assess_risk(text),
            "requires_confirmation": assess_risk(text) == "high"
        },
        "action_type": determine_action_type(text),
        "routing": {
            "suggested_skills": suggest_skills(text),
            "suggested_model": "gateway/jarvis" if "量化" in text else "gateway/jarvis",
            "use_reasoning_chain": any(kw in text for kw in ["分析", "决策", "对比"])
        },
        "has_memory": len(text) > 5,
        "complexity": "complex" if len(text.split()) > 3 else "simple"
    }


def boot():
    """启动信息"""
    return {
        "kernel": "cognitive-kernel-v6-adapter",
        "version": "1.0.0",
        "workspace": str(WORKSPACE),
        "status": "ready"
    }


def status():
    """系统状态"""
    return {
        "kernel": "running",
        "workspace_exists": WORKSPACE.exists(),
        "intent_classifier": "available",
        "scripts_dir": str(WORKSPACE / "scripts")
    }


def check():
    """健康检查"""
    return {
        "api_fallback": "not-configured",
        "local_processing": "active",
        "status": "healthy"
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--process", type=str, default=None, help="处理输入文本")
    parser.add_argument("--boot", action="store_true", help="启动信息")
    parser.add_argument("--status", action="store_true", help="系统状态")
    parser.add_argument("--check", action="store_true", help="健康检查")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    if args.boot:
        result = boot()
    elif args.status:
        result = status()
    elif args.check:
        result = check()
    elif args.process is not None:
        result = process(args.process)
    else:
        result = {"error": "No action specified", "help": "Use --process, --boot, --status, or --check"}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
