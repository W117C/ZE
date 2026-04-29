#!/usr/bin/env python3
"""
Run Full Sim Trading Pipeline: market scan → trade decision → daily report.

This is the main entry point for the daily paper-trading workflow.
"""
import argparse, json, subprocess, time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/'data'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--top', type=int, default=20)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--send', action='store_true')
    p.add_argument('--reflect', action='store_true')
    args = p.parse_args()

    # Step 1: Market scan
    print("=== Step 1: Market Scan ===")
    try:
        result = subprocess.check_output(
            ['python3', str(SCRIPT_DIR/'run_real_sim.py'), '--json', '--top', str(args.top)],
            text=True, timeout=300
        )
        market = json.loads(result)
        candidates = market.get('candidates', [])
        print(f"Scanned: {len(candidates)} candidates")
    except Exception as e:
        print(f"Market scan failed: {e}")
        candidates = []

    if not candidates:
        print("No candidates, skipping trade decisions")
        return

    # Step 2: Save candidates for trade_decision
    candidates_file = Path('/tmp/sim_candidates.json')
    candidates_file.write_text(json.dumps({'candidates': candidates}, ensure_ascii=False, indent=2))

    # Step 3: Trade decisions
    print("\n=== Step 2: Trade Decisions ===")
    cmd = ['python3', str(SCRIPT_DIR/'trade_decision.py'), '--candidates-file', str(candidates_file)]
    if args.dry_run:
        cmd.append('--dry-run')
    try:
        result = subprocess.check_output(cmd, text=True, timeout=60)
        print(result)
    except Exception as e:
        print(f"Trade decision failed: {e}")

    # Step 4: Generate daily report
    print("\n=== Step 3: Generate Daily Report ===")
    report_cmd = [
        'python3', str(SCRIPT_DIR/'generate_daily_report.py'),
        '--out', args.out
    ]
    if args.send:
        report_cmd.append('--send')
    if args.reflect:
        report_cmd.append('--reflect')
    
    try:
        result = subprocess.check_output(report_cmd, text=True, timeout=60)
        print(result)
    except Exception as e:
        print(f"Report generation failed: {e}")

if __name__ == '__main__':
    main()
