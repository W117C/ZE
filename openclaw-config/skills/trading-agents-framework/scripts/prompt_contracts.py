#!/usr/bin/env python3
import json
contracts = {
  'technical_analyst': ['trend','momentum','volatility','levels','confidence'],
  'fundamentals_analyst': ['thesis','valuation','balance_sheet','red_flags','confidence'],
  'news_analyst': ['event_impact','timing_risk','narrative','confidence'],
  'sentiment_analyst': ['sentiment_state','crowding_risk','reversal_risk','confidence'],
  'trader': ['direction','size_logic','horizon','triggers'],
  'risk_manager': ['approve_or_reject','position_cap','drawdown_concern','liquidity_risk'],
  'portfolio_manager': ['decision','modifications','rationale']
}
print(json.dumps(contracts, ensure_ascii=False, indent=2))
