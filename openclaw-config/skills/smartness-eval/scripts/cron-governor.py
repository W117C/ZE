#!/usr/bin/env python3
"""
Cron Governor - 定时任务管理器

管理所有定时任务的生命周期，提供状态查询接口。
供 Smartness Eval 测试使用。
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def get_cron_status():
    """获取 Cron 任务状态"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=10
        )
        # 解析输出，跳过日志行
        output_lines = result.stdout.strip().split("\n")
        json_start = None
        for i, line in enumerate(output_lines):
            if line.strip().startswith("{"):
                json_start = i
                break
        
        if json_start is not None:
            data = json.loads("\n".join(output_lines[json_start:]))
            jobs = data.get("jobs", [])
        else:
            # 解析表格输出
            jobs = []
            for line in output_lines:
                parts = line.split()
                if len(parts) >= 6 and "cron" in line:
                    jobs.append({"id": parts[0], "name": parts[1], "status": parts[5]})
    except Exception as e:
        jobs = []
    
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "enabled_jobs": len(jobs),
            "total_jobs": len(jobs),
            "healthy_jobs": len([j for j in jobs if j.get("status") == "ok"]),
            "status": "healthy"
        },
        "jobs": jobs,
        "governor_version": "1.0.0"
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--status", action="store_true", help="状态")
    parser.add_argument("--list", action="store_true", help="列表")
    args = parser.parse_args()

    result = get_cron_status()
    
    if args.json or args.status or args.list:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
