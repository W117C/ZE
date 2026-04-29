#!/usr/bin/env python3
import argparse, subprocess, json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

def run(*args):
    subprocess.check_call(['python3', *map(str,args)])

def main():
    p = argparse.ArgumentParser(); p.add_argument('symbol'); p.add_argument('--market', default='CN'); p.add_argument('--risk-profile', default='neutral'); p.add_argument('--out-dir', default='./runs'); args = p.parse_args()
    run_dir = Path(args.out_dir)/f"{args.symbol}-{args.market}"
    run_dir.mkdir(parents=True, exist_ok=True)
    market = run_dir/'market_context.json'; tech = run_dir/'technical_note.json'; bundle = run_dir/'analyst_bundle.json'; debate = run_dir/'debate'; proposal = run_dir/'trade_proposal.json'; risk = run_dir/'risk_review.json'; final = run_dir/'final_decision.json'; ticket = run_dir/'execution_ticket.json'
    run(SCRIPT_DIR/'build_market_context.py', args.symbol, '--market', args.market, '--out', market)
    run(SCRIPT_DIR/'run_technical_analyst_stub.py', market, '--out', tech)
    run(SCRIPT_DIR/'merge_analyst_notes.py', tech, '--out', bundle)
    run(SCRIPT_DIR/'run_bull_bear_debate_stub.py', bundle, '--out-dir', debate)
    run(SCRIPT_DIR/'run_trader_stub.py', debate/'debate_summary.json', '--out', proposal)
    run(SCRIPT_DIR/'run_risk_manager_stub.py', proposal, '--risk-profile', args.risk_profile, '--out', risk)
    run(SCRIPT_DIR/'run_portfolio_manager_stub.py', proposal, risk, '--out', final)
    run(SCRIPT_DIR/'build_execution_ticket.py', final, '--out', ticket)
    print(run_dir)

if __name__ == '__main__':
    main()
