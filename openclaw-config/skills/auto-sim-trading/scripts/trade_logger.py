#!/usr/bin/env python3
"""
Trade Logger: Records all trading operations and manages portfolio state.

Usage:
  python3 trade_logger.py record --action buy --symbol 600519 --price 1527.2 --reason "基本面偏正面，技术面企稳"
  python3 trade_logger.py record --action sell --symbol 300750 --price 267.2 --reason "技术面转弱，触发止损"
  python3 trade_logger.py record --action hold --symbol 600036 --reason "等待进一步确认"
  python3 trade_logger.py show
  python3 trade_logger.py problems
"""
import argparse, json, time
from pathlib import Path

DATA_DIR = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/'data'
TRADE_LOG = DATA_DIR/'trade_log.json'
PORTFOLIO = DATA_DIR/'portfolio.json'
PROBLEMS_LOG = DATA_DIR/'problems_log.json'
ACCOUNT = DATA_DIR/'account.json'

DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path, default=None):
    if path.exists():
        return json.loads(path.read_text())
    return default if default else []

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def record_trade(action, symbol, price=None, reason="", quantity=None):
    """记录一笔交易"""
    trade = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'date': time.strftime('%Y-%m-%d'),
        'action': action,
        'symbol': symbol,
        'price': price,
        'quantity': quantity,
        'reason': reason
    }
    log = load_json(TRADE_LOG)
    log.append(trade)
    save_json(TRADE_LOG, log)

    # 更新持仓和账户
    update_portfolio(action, symbol, price, quantity)
    print(f"[OK] 已记录: {action} {symbol} {'@'+str(price) if price else ''} | {reason}")

def update_portfolio(action, symbol, price, quantity):
    """更新持仓状态和账户现金"""
    portfolio = load_json(PORTFOLIO, {'positions': [], 'history': []})
    account = load_json(ACCOUNT)

    if action == 'buy':
        # 扣除现金
        if account and price and quantity:
            cost = price * quantity
            account['cash'] = account.get('cash', 0) - cost
            account['trade_count'] = account.get('trade_count', 0) + 1
            save_json(ACCOUNT, account)
        
        # 更新持仓
        for pos in portfolio['positions']:
            if pos['symbol'] == symbol:
                pos['quantity'] = pos.get('quantity', 0) + (quantity or 0)
                pos['avg_price'] = price
                pos['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
                break
        else:
            portfolio['positions'].append({
                'symbol': symbol,
                'quantity': quantity or 0,
                'avg_price': price,
                'current_price': price,
                'entry_date': time.strftime('%Y-%m-%d'),
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            })

    elif action == 'sell':
        # 增加现金
        sell_qty = 0
        for pos in portfolio['positions']:
            if pos['symbol'] == symbol:
                sell_qty = pos.get('quantity', 0)
                portfolio['positions'] = [p for p in portfolio['positions'] if p['symbol'] != symbol]
                break
        if account and price and sell_qty:
            revenue = price * sell_qty
            account['cash'] = account.get('cash', 0) + revenue
            account['trade_count'] = account.get('trade_count', 0) + 1
            save_json(ACCOUNT, account)
        
        portfolio['history'].append({
            'symbol': symbol,
            'exit_price': price,
            'exit_date': time.strftime('%Y-%m-%d'),
            'reason': 'sold'
        })

    save_json(PORTFOLIO, portfolio)

def record_problem(category, description, suggestion=""):
    """记录一个问题"""
    problem = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'date': time.strftime('%Y-%m-%d'),
        'category': category,
        'description': description,
        'suggestion': suggestion
    }
    log = load_json(PROBLEMS_LOG)
    log.append(problem)
    save_json(PROBLEMS_LOG, log)
    print(f"[PROBLEM] 已记录: {category} - {description}")

def show_portfolio():
    """显示当前持仓"""
    portfolio = load_json(PORTFOLIO, {'positions': []})
    positions = portfolio.get('positions', [])
    if not positions:
        print("当前无持仓")
        return
    print("=== 当前持仓 ===")
    for p in positions:
        print(f"  {p['symbol']}: 数量 {p.get('quantity', 0)}, 均价 {p.get('avg_price', 0)}, 入场 {p.get('entry_date', '')}")
    print("=== End ===")

def show_problems(days=1):
    """显示近期问题"""
    problems = load_json(PROBLEMS_LOG, [])
    today = time.strftime('%Y-%m-%d')
    recent = [p for p in problems if p.get('date') == today]
    if not recent:
        print("今日无问题记录")
        return
    print("=== 今日问题 ===")
    for p in recent:
        print(f"  [{p['category']}] {p['description']}")
        if p.get('suggestion'):
            print(f"    建议: {p['suggestion']}")
    print("=== End ===")

def get_todays_trades():
    """获取今日交易"""
    log = load_json(TRADE_LOG)
    today = time.strftime('%Y-%m-%d')
    return [t for t in log if t.get('date') == today]

def get_todays_problems():
    """获取今日问题"""
    log = load_json(PROBLEMS_LOG)
    today = time.strftime('%Y-%m-%d')
    return [p for p in log if p.get('date') == today]

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='command')

    rec = sub.add_parser('record')
    rec.add_argument('--action', required=True, choices=['buy', 'sell', 'hold'])
    rec.add_argument('--symbol', required=True)
    rec.add_argument('--price', type=float)
    rec.add_argument('--quantity', type=int)
    rec.add_argument('--reason', default='')

    sub.add_parser('show')

    prob = sub.add_parser('problems')
    prob.add_argument('--record', action='store_true')
    prob.add_argument('--category', default='other')
    prob.add_argument('--description', default='')
    prob.add_argument('--suggestion', default='')

    args = p.parse_args()

    if args.command == 'record':
        record_trade(args.action, args.symbol, args.price, args.reason, args.quantity)
    elif args.command == 'show':
        show_portfolio()
    elif args.command == 'problems':
        if args.record:
            record_problem(args.category, args.description, args.suggestion)
        else:
            show_problems()
    else:
        p.print_help()

if __name__ == '__main__':
    main()
