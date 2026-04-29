#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('analyst_bundle'); p.add_argument('--out', default='./agent_session_chain.json'); args = p.parse_args()
    chain = {
      'topology': 'bull_bear_independent_sessions_then_manager',
      'agents': {
        'bull': {'mode': 'session', 'role': 'independent bullish case generator'},
        'bear': {'mode': 'session', 'role': 'independent bearish case generator'},
        'manager': {'mode': 'session', 'role': 'synthesizer after bull/bear outputs'}
      },
      'execution_plan': [
        {'step': 1, 'agent': 'bull', 'input': 'analyst_bundle', 'output': 'bull_session_output.json'},
        {'step': 2, 'agent': 'bear', 'input': 'analyst_bundle', 'output': 'bear_session_output.json'},
        {'step': 3, 'agent': 'manager', 'input': ['bull_session_output.json','bear_session_output.json'], 'output': 'manager_session_output.json'}
      ],
      'status': 'ready_for_openclaw_sessions_integration'
    }
    Path(args.out).write_text(json.dumps(chain, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
