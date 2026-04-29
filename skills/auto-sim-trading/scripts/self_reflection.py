#!/usr/bin/env python3
"""
Self-Reflection & Evolution Engine: Analyzes daily reports, identifies patterns, generates upgrades.

Usage:
  python3 self_reflection.py --report /tmp/daily-report.json
  python3 self_reflection.py --auto-upgrade
  python3 self_reflection.py --show-evolution-log
"""
import argparse, json, time, statistics
from pathlib import Path

DATA_DIR = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/'data'
EVOLUTION_LOG = DATA_DIR/'evolution_log.json'
UPGRADE_TASKS = DATA_DIR/'upgrade_tasks.json'
REPORTS_DIR = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/'data'
REPORTS_DIR_ALT = Path.home()/'openclaw'/'workspace'/'reports'

DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path, default=None):
    if path.exists():
        return json.loads(path.read_text())
    return default if default else []

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def analyze_report(report):
    """分析单份日报，识别问题"""
    issues = []
    improvements = []

    trades = report.get('today_trades', [])
    problems = report.get('today_problems', [])
    improvements_report = report.get('improvements', [])
    summary = report.get('summary', {})

    # 分析交易
    if not trades:
        issues.append({
            'category': 'operation',
            'severity': 'medium',
            'description': '今日无操作记录',
            'suggestion': '检查评分系统是否正常运行，或市场是否无符合条件标的'
        })

    # 分析问题
    data_problems = [p for p in problems if p.get('category') == 'data']
    if data_problems:
        issues.append({
            'category': 'data',
            'severity': 'high',
            'description': f'今日 {len(data_problems)} 个数据问题',
            'suggestion': '需要增强数据源容错或增加备用数据源'
        })

    model_problems = [p for p in problems if p.get('category') == 'model']
    if model_problems:
        issues.append({
            'category': 'model',
            'severity': 'high',
            'description': f'今日 {len(model_problems)} 个模型问题',
            'suggestion': '需要审视因子权重或评分逻辑'
        })

    # 分析改进建议
    if any('情绪' in imp for imp in improvements_report):
        issues.append({
            'category': 'sentiment',
            'severity': 'medium',
            'description': '情绪数据源不稳定',
            'suggestion': '增加备用情绪源或缓存策略'
        })

    if any('因子' in imp for imp in improvements_report):
        issues.append({
            'category': 'factor',
            'severity': 'low',
            'description': '因子权重可能需要调整',
            'suggestion': '定期回测验证因子有效性'
        })

    return {
        'date': report.get('date'),
        'issues': issues,
        'trade_count': summary.get('trade_count', 0),
        'problem_count': summary.get('problem_count', 0),
        'position_count': summary.get('position_count', 0)
    }

def analyze_pattern(days=7):
    """分析近 N 天日报，识别系统性问题"""
    today = time.strftime('%Y-%m-%d')
    issues_by_category = {}
    daily_summaries = []

    # 读取历史日报（两个目录都检查）
    for base_dir in [REPORTS_DIR, REPORTS_DIR_ALT]:
        if base_dir.exists():
            for f in sorted(base_dir.glob('daily-report-*.json')):
                try:
                    report = json.loads(f.read_text())
                    analysis = analyze_report(report)
                    daily_summaries.append(analysis)

                    for issue in analysis['issues']:
                        cat = issue['category']
                        if cat not in issues_by_category:
                            issues_by_category[cat] = []
                        issues_by_category[cat].append(issue)
                except Exception:
                    continue

    # 识别重复出现的问题
    recurring_issues = []
    for cat, issues in issues_by_category.items():
        if len(issues) >= 2:  # 出现 2 次以上视为系统性问题
            recurring_issues.append({
                'category': cat,
                'occurrence_count': len(issues),
                'description': issues[0]['description'],
                'suggestion': issues[0]['suggestion'],
                'severity': 'high' if len(issues) >= 3 else 'medium'
            })

    return {
        'analysis_date': today,
        'days_analyzed': len(daily_summaries),
        'daily_summaries': daily_summaries,
        'recurring_issues': recurring_issues,
        'issues_by_category': {k: len(v) for k, v in issues_by_category.items()}
    }

def generate_upgrade_tasks(pattern_analysis):
    """基于模式分析生成升级任务"""
    tasks = []
    recurring = pattern_analysis.get('recurring_issues', [])

    for issue in recurring:
        if issue['category'] == 'data':
            tasks.append({
                'type': 'data_source_enhancement',
                'priority': 'high',
                'description': '增强数据源容错',
                'action': '增加备用数据源和超时重试机制',
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })

        elif issue['category'] == 'sentiment':
            tasks.append({
                'type': 'sentiment_source_upgrade',
                'priority': 'medium',
                'description': '升级情绪数据源',
                'action': '增加备用情绪源或改进缓存策略',
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })

        elif issue['category'] == 'model':
            tasks.append({
                'type': 'model_review',
                'priority': 'high',
                'description': '模型逻辑审查',
                'action': '审视因子权重和评分逻辑',
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })

        elif issue['category'] == 'factor':
            tasks.append({
                'type': 'factor_rebalance',
                'priority': 'low',
                'description': '因子权重再平衡',
                'action': '基于回测结果调整因子权重',
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })

        elif issue['category'] == 'operation':
            tasks.append({
                'type': 'operation_review',
                'priority': 'medium',
                'description': '操作流程审查',
                'action': '检查评分系统与交易触发逻辑',
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })

    return tasks

def log_evolution(entry):
    """记录进化日志"""
    log = load_json(EVOLUTION_LOG, [])
    log.append(entry)
    save_json(EVOLUTION_LOG, log)

def save_upgrade_tasks(tasks):
    """保存升级任务"""
    existing = load_json(UPGRADE_TASKS, [])
    # 避免重复添加相同任务
    existing_types = {t.get('type') for t in existing if t.get('status') != 'completed'}
    new_tasks = [t for t in tasks if t.get('type') not in existing_types]
    existing.extend(new_tasks)
    save_json(UPGRADE_TASKS, existing)
    return new_tasks

def run_reflection(report_path=None):
    """运行完整反思流程"""
    # 1. 分析模式
    pattern = analyze_pattern()

    # 2. 生成升级任务
    tasks = generate_upgrade_tasks(pattern)
    new_tasks = save_upgrade_tasks(tasks)

    # 3. 记录进化
    log_evolution({
        'date': time.strftime('%Y-%m-%d'),
        'type': 'reflection',
        'pattern_analysis': {
            'days_analyzed': pattern['days_analyzed'],
            'recurring_issues_count': len(pattern['recurring_issues']),
            'issues_by_category': pattern['issues_by_category']
        },
        'new_tasks': len(new_tasks),
        'tasks': [t['description'] for t in new_tasks]
    })

    # 4. 输出结果
    if new_tasks:
        print(f"\n🔍 反思完成，发现 {len(new_tasks)} 个新升级任务:")
        for t in new_tasks:
            print(f"  [{t['priority']}] {t['description']}: {t['action']}")
    else:
        print("\n✅ 反思完成，未发现新的系统性问题")

    return {'pattern': pattern, 'new_tasks': new_tasks}

def show_evolution_log():
    """显示进化日志"""
    log = load_json(EVOLUTION_LOG, [])
    if not log:
        print("暂无进化记录")
        return

    print("=== 进化日志 ===")
    for entry in log:
        print(f"\n📅 {entry['date']} | {entry['type']}")
        if entry.get('new_tasks'):
            print(f"  新增 {entry['new_tasks']} 个升级任务")
            for t in entry.get('tasks', []):
                print(f"    - {t}")
    print("\n=== End ===")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--report')
    p.add_argument('--auto-upgrade', action='store_true')
    p.add_argument('--show-evolution-log', action='store_true')
    args = p.parse_args()

    if args.show_evolution_log:
        show_evolution_log()
    elif args.auto_upgrade:
        result = run_reflection()
        if result['new_tasks']:
            print("\n📋 升级任务已保存，等待执行")
    elif args.report:
        report = json.loads(Path(args.report).read_text())
        analysis = analyze_report(report)
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    else:
        result = run_reflection()

if __name__ == '__main__':
    main()
