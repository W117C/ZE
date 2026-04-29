#!/usr/bin/env python3
import argparse, json, subprocess
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
AUTO = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/'scripts'/'run_real_sim.py'

def run_json(cmd):
    return json.loads(subprocess.check_output(cmd, text=True))

def main():
    p = argparse.ArgumentParser(); p.add_argument('--top', type=int, default=3); p.add_argument('--out', default='./screening_output.json'); args = p.parse_args()
    data = run_json(['python3', str(AUTO), '--json', '--top', str(args.top)])
    out = {'generated_at': None, 'source_skill': 'auto-sim-trading', 'candidates': data.get('candidates', [])[:args.top]}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
