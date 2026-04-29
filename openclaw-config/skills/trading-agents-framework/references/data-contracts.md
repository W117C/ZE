# Data Contracts

## screening_output.json
- generated_at
- source_skill
- candidates[]
  - symbol
  - name
  - total_score
  - trend_score
  - risk_score
  - liquidity_score
  - price_change_pct
  - volatility
  - price

## market_context.json
- symbol
- market
- horizon
- history

## fundamentals_context.json
- symbol
- provider
- valuation
- profitability
- growth
- leverage
- notes

## news_context.json
- symbol
- provider
- news[]
  - title
  - summary
  - date
  - tag

## social_context.json
- symbol
- provider
- sentiment_summary
- attention_level
- crowding_risk

## integrated_candidate_packet.json
- screening
- market_context
- fundamentals_context
- news_context
- social_context
