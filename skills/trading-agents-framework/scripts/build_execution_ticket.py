#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('final_decision'); p.add_argument('--validity-hours', type=int, default=24); p.add_argument('--out', default='./execution_ticket.json'); args = p.parse_args()
    ticket = {'type':'paper_execution_ticket','validity_hours':args.validity_hours,'status':'simulated_handoff'}
    Path(args.out).write_text(json.dumps(ticket, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
