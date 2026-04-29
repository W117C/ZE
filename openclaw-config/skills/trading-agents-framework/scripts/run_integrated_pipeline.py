#!/usr/bin/env python3
import argparse, json, subprocess
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent

def run(*args):
    subprocess.check_call(['python3', *map(str,args)])

def main():
    p = argparse.ArgumentParser(); p.add_argument('--top', type=int, default=1); p.add_argument('--out-dir', default='./integrated-runs'); p.add_argument('--risk-profile', default='neutral'); args = p.parse_args()
    root = Path(args.out_dir); root.mkdir(parents=True, exist_ok=True)
    screening = root/'screening_output.json'
    run(SCRIPT_DIR/'bridge_screening_to_agents.py', '--top', str(args.top), '--out', screening)
    screening_data = json.loads(screening.read_text())
    candidates = screening_data.get('candidates', [])[:args.top]
    all_runs = []
    for c in candidates:
        symbol = c['symbol']
        cdir = root/symbol; cdir.mkdir(parents=True, exist_ok=True)
        market = cdir/'market_context.json'; funda = cdir/'fundamentals_context.json'; news = cdir/'news_context.json'; social = cdir/'social_context.json'; packet = cdir/'integrated_candidate_packet.json'; tech = cdir/'technical_note.json'; fnote = cdir/'fundamentals_note.json'; nnote = cdir/'news_note.json'; snote = cdir/'sentiment_note.json'; bundle = cdir/'analyst_bundle.json'; debate = cdir/'debate'; proposal = cdir/'trade_proposal.json'; risk = cdir/'risk_review.json'; final = cdir/'final_decision.json'; ticket = cdir/'execution_ticket.json'
        run(SCRIPT_DIR/'build_market_context.py', symbol, '--market', 'CN', '--out', market)
        run(SCRIPT_DIR/'build_fundamentals_context.py', symbol, '--out', funda)
        run(SCRIPT_DIR/'build_news_context.py', symbol, '--out', news)
        run(SCRIPT_DIR/'build_sentiment_context.py', symbol, '--out', social)
        run(SCRIPT_DIR/'build_candidate_packet.py', screening, market, funda, news, social, '--out', packet)
        run(SCRIPT_DIR/'run_technical_analyst_stub.py', market, '--out', tech)
        run(SCRIPT_DIR/'run_fundamentals_analyst_stub.py', funda, '--out', fnote)
        run(SCRIPT_DIR/'run_news_analyst_stub.py', news, '--out', nnote)
        run(SCRIPT_DIR/'run_sentiment_analyst_stub.py', social, '--out', snote)
        run(SCRIPT_DIR/'merge_analyst_notes.py', tech, fnote, nnote, snote, '--out', bundle)
        run(SCRIPT_DIR/'run_bull_bear_debate_stub.py', bundle, '--out-dir', debate)
        run(SCRIPT_DIR/'run_trader_stub.py', debate/'debate_summary.json', '--out', proposal)
        run(SCRIPT_DIR/'run_risk_manager_stub.py', proposal, '--risk-profile', args.risk_profile, '--out', risk)
        run(SCRIPT_DIR/'run_portfolio_manager_stub.py', proposal, risk, '--out', final)
        run(SCRIPT_DIR/'build_execution_ticket.py', final, '--out', ticket)
        all_runs.append(str(cdir))
    print(json.dumps({'root': str(root), 'runs': all_runs}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
