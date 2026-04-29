#!/usr/bin/env python3
"""
Trading Decision Engine: 基于评分结果 + 账户状态 自动执行买卖决策。

买入规则：
  1. 总分 ≥ buy_score_threshold（默认 78）
  2. 趋势分 > 风险分
  3. 流动性 ≥ 50
  4. 当前持仓数 < max_positions
  5. 单只仓位 ≤ max_position_pct

卖出规则：
  1. 止损：跌幅 ≥ stop_loss_pct → 立即卖出
  2. 止盈：涨幅 ≥ take_profit_pct → 分批止盈
  3. 评分恶化：当前评分 < sell_score_threshold → 卖出

仓位控制：
  - 初始资金 200,000
  - 单只最大仓位 25%（¥50,000）
  - 最大持仓 4 只
  - 买入按整百股

Usage:
  python3 trade_decision.py --candidates-file /tmp/candidates.json
  python3 trade_decision.py --dry-run  # 只输出不执行
"""
import argparse, json, time, subprocess, math
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/'data'
ACCOUNT = DATA_DIR/'account.json'
PORTFOLIO = DATA_DIR/'portfolio.json'
TRADE_LOG = DATA_DIR/'trade_log.json'

# 默认交易参数
DEFAULT_PARAMS = {
    'buy_score_threshold': 78,        # 买入最低总分
    'min_trend_over_risk': 0,         # 趋势分至少要大于风险分多少
    'min_liquidity': 50,              # 最低流动性
    'max_positions': 4,               # 最大持仓数
    'max_position_pct': 0.25,         # 单只最大仓位占比
    'stop_loss_pct': -8.0,            # 止损线（-8%）
    'take_profit_pct': 15.0,          # 止盈线（+15%）
    'sell_score_threshold': 70,       # 评分低于此值卖出
}

def load_json(path, default=None):
    if path.exists():
        return json.loads(path.read_text())
    return default if default is not None else {}

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def record_trade(action, symbol, price, reason, quantity):
    """通过 trade_logger 记录交易"""
    subprocess.run([
        'python3', str(SCRIPT_DIR/'trade_logger.py'),
        'record', '--action', action, '--symbol', symbol,
        '--price', str(price), '--quantity', str(quantity),
        '--reason', reason
    ], text=True, timeout=30)

def calc_buy_quantity(price, available_cash, max_pct):
    """计算可买入的整百股数"""
    if price <= 0: return 0
    max_amount = available_cash * max_pct
    qty = int(max_amount / price / 100) * 100
    return max(0, qty)

def make_decisions(candidates, account, portfolio, params=None, dry_run=False):
    """主决策逻辑"""
    if params is None:
        params = DEFAULT_PARAMS
    
    trades_executed = []
    cash = account.get('cash', 0)
    current_positions = portfolio.get('positions', [])
    position_count = len(current_positions)
    
    action_log = []

    # ========== 第一步：检查现有持仓是否需要卖出 ==========
    positions_to_sell = []
    for pos in current_positions:
        symbol = pos['symbol']
        avg_price = pos.get('avg_price', 0)
        current_price = pos.get('current_price', avg_price)
        quantity = pos.get('quantity', 0)
        
        if avg_price <= 0 or current_price <= 0:
            continue
        
        pnl_pct = (current_price / avg_price - 1) * 100
        
        # 检查评分是否恶化
        candidate = next((c for c in candidates if c['symbol'] == symbol), None)
        score = candidate['total_score'] if candidate else params['sell_score_threshold'] - 1
        
        # 止损
        if pnl_pct <= params['stop_loss_pct']:
            reason = f"止损（浮亏 {pnl_pct:.1f}%，均价¥{avg_price} → 现价¥{current_price}）"
            positions_to_sell.append((symbol, current_price, quantity, reason, 'stop_loss'))
            action_log.append(f"🔴 卖出 {symbol}: {reason}")
        
        # 止盈
        elif pnl_pct >= params['take_profit_pct']:
            reason = f"止盈（浮盈 {pnl_pct:.1f}%）"
            positions_to_sell.append((symbol, current_price, quantity, reason, 'take_profit'))
            action_log.append(f"🟢 止盈卖出 {symbol}: {reason}")
        
        # 评分恶化
        elif score < params['sell_score_threshold']:
            reason = f"评分恶化（当前分 {score} < 阈值 {params['sell_score_threshold']}）"
            positions_to_sell.append((symbol, current_price, quantity, reason, 'score_degrade'))
            action_log.append(f"⚠️ 评分卖出 {symbol}: {reason}")

    # 执行卖出
    for symbol, price, qty, reason, sell_type in positions_to_sell:
        if not dry_run:
            record_trade('sell', symbol, price, reason, qty)
        trades_executed.append({
            'action': 'sell', 'symbol': symbol, 'price': price,
            'quantity': qty, 'reason': reason, 'type': sell_type
        })

    # 更新可用现金（模拟）
    for _, price, qty, _, _ in positions_to_sell:
        cash += price * qty
        position_count -= 1

    # ========== 第二步：检查是否有新买入机会 ==========
    if position_count >= params['max_positions']:
        action_log.append(f"⏸️ 已达最大持仓数 {params['max_positions']}，暂不买入")
        return trades_executed, action_log

    # 按总分排序
    sorted_candidates = sorted(candidates, key=lambda x: x.get('total_score', 0), reverse=True)
    
    bought_count = 0
    for candidate in sorted_candidates:
        symbol = candidate['symbol']
        total = candidate.get('total_score', 0)
        trend = candidate.get('trend_score', 0)
        risk = candidate.get('risk_score', 0)
        liquidity = candidate.get('liquidity_score', 0)
        price = candidate.get('price', 0)
        
        # 已在持仓的跳过
        if any(p['symbol'] == symbol for p in current_positions):
            continue
        
        # 买入条件检查
        reasons_rejected = []
        if total < params['buy_score_threshold']:
            reasons_rejected.append(f"总分 {total} < {params['buy_score_threshold']}")
        if trend - risk < params['min_trend_over_risk']:
            reasons_rejected.append(f"趋势{trend} 不大于 风险{risk}")
        if liquidity < params['min_liquidity']:
            reasons_rejected.append(f"流动性 {liquidity} < {params['min_liquidity']}")
        if position_count + bought_count >= params['max_positions']:
            reasons_rejected.append(f"已达最大持仓数")
        
        if reasons_rejected:
            continue
        
        # 计算买入数量
        max_pct = params['max_position_pct']
        qty = calc_buy_quantity(price, cash, max_pct)
        
        if qty <= 0:
            action_log.append(f"⏸️ {symbol}: 资金不足，跳过")
            continue
        
        cost = price * qty
        reason = f"买入评分 {total} | 趋势{trend}/风险{risk}/流动性{liquidity}"
        
        if not dry_run:
            record_trade('buy', symbol, price, reason, qty)
        
        trades_executed.append({
            'action': 'buy', 'symbol': symbol, 'price': price,
            'quantity': qty, 'reason': reason, 'cost': cost
        })
        action_log.append(f"🟢 买入 {symbol} {qty}股 @ ¥{price} = ¥{cost:.0f} | 总分 {total}")
        
        cash -= cost
        bought_count += 1
        
        if position_count + bought_count >= params['max_positions']:
            break

    if not trades_executed:
        action_log.append("⏸️ 今日无交易信号")

    return trades_executed, action_log

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidates-file', default=None, help='候选股 JSON 文件路径')
    p.add_argument('--dry-run', action='store_true', help='只输出决策不执行')
    args = p.parse_args()

    # 加载账户
    account = load_json(ACCOUNT, {'cash': 200000, 'initial_capital': 200000})
    portfolio = load_json(PORTFOLIO, {'positions': []})

    # 加载候选股
    candidates = []
    if args.candidates_file and Path(args.candidates_file).exists():
        data = json.loads(Path(args.candidates_file).read_text())
        candidates = data.get('candidates', data if isinstance(data, list) else [])
    else:
        # 默认从 run_real_sim 获取
        try:
            result = subprocess.check_output(
                ['python3', str(SCRIPT_DIR/'run_real_sim.py'), '--json', '--top', '20'],
                text=True, timeout=120
            )
            data = json.loads(result)
            candidates = data.get('candidates', [])
        except Exception as e:
            print(f"获取候选股失败: {e}")
            return

    if not candidates:
        print("⚠️ 无候选股，跳过交易决策")
        return

    print(f"收到 {len(candidates)} 只候选股，开始决策...\n")

    trades, logs = make_decisions(candidates, account, portfolio, dry_run=args.dry_run)

    for log in logs:
        print(log)

    if trades:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}共执行 {len(trades)} 笔交易:")
        for t in trades:
            print(f"  {t['action'].upper()} {t['symbol']} {t.get('quantity','')}股 @ ¥{t['price']} | {t['reason']}")
    else:
        print(f"\n今日无交易")

    # 保存决策结果
    decision_file = DATA_DIR / f'decision_{time.strftime("%Y%m%d")}.json'
    save_json(decision_file, {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'trades': trades,
        'action_log': logs
    })

if __name__ == '__main__':
    main()
