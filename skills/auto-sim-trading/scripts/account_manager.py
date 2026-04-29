#!/usr/bin/env python3
"""
Account Manager: 模拟账户管理，跟踪总资产/净值/收益率/最大回撤。

Usage:
  python3 account_manager.py init --capital 100000        # 初始化10万模拟资金
  python3 account_manager.py show                         # 查看当前账户状态
  python3 account_manager.py update                       # 更新当前持仓市值
  python3 account_manager.py history                      # 查看历史净值
"""
import argparse, json, time, sys
from pathlib import Path

DATA_DIR = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/'data'
ACCOUNT = DATA_DIR/'account.json'
NAV_HISTORY = DATA_DIR/'nav_history.json'
PORTFOLIO = DATA_DIR/'portfolio.json'
TRADE_LOG = DATA_DIR/'trade_log.json'

DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path, default=None):
    if path.exists():
        return json.loads(path.read_text())
    return default if default else {}

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def get_current_prices():
    """获取持仓股票当前价格"""
    from pathlib import Path as P
    sys.path.insert(0, str(P.home()/'.openclaw'/'skills'/'finance-data'/'tools'))
    import subprocess
    portfolio = load_json(PORTFOLIO, {'positions': []})
    for pos in portfolio.get('positions', []):
        try:
            result = subprocess.check_output(
                ['python3', str(P.home()/'.openclaw'/'skills'/'finance-data'/'tools'/'stock_query.py'), pos['symbol']],
                text=True, timeout=15
            )
            data = json.loads(result)
            pos['current_price'] = data.get('data', {}).get('price', pos.get('avg_price', 0))
        except Exception:
            pass
    save_json(PORTFOLIO, portfolio)
    return portfolio

def calc_portfolio_value():
    """计算当前持仓市值"""
    portfolio = load_json(PORTFOLIO, {'positions': []})
    total = 0
    for pos in portfolio.get('positions', []):
        price = pos.get('current_price', pos.get('avg_price', 0))
        qty = pos.get('quantity', 0)
        total += price * qty
    return total, portfolio.get('positions', [])

def init_account(capital):
    """初始化模拟账户"""
    account = {
        'initial_capital': capital,
        'current_capital': capital,
        'total_value': capital,
        'cash': capital,
        'market_value': 0,
        'total_return_pct': 0,
        'max_drawdown_pct': 0,
        'peak_value': capital,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'trade_count': 0
    }
    save_json(ACCOUNT, account)
    
    # 记录初始净值
    nav = [{'date': time.strftime('%Y-%m-%d'), 'nav': capital, 'return_pct': 0}]
    save_json(NAV_HISTORY, nav)
    
    print(f"✅ 模拟账户已初始化")
    print(f"  初始资金: ¥{capital:,.2f}")
    print(f"  当前总资产: ¥{capital:,.2f}")
    print(f"  可用现金: ¥{capital:,.2f}")

def update_account():
    """更新账户状态（刷新持仓市值）"""
    account = load_json(ACCOUNT)
    if not account:
        print("❌ 账户未初始化，请先运行: python3 account_manager.py init --capital 100000")
        return

    # 获取最新价格
    portfolio = get_current_prices()
    
    # 计算持仓市值
    market_value = 0
    for pos in portfolio.get('positions', []):
        price = pos.get('current_price', pos.get('avg_price', 0))
        qty = pos.get('quantity', 0)
        market_value += price * qty

    total_value = account.get('cash', 0) + market_value
    account['market_value'] = market_value
    account['total_value'] = total_value
    account['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')

    # 计算收益率
    initial = account.get('initial_capital', total_value)
    account['total_return_pct'] = round((total_value - initial) / initial * 100, 2)

    # 更新峰值和最大回撤
    if total_value > account.get('peak_value', initial):
        account['peak_value'] = total_value
    
    peak = account.get('peak_value', total_value)
    drawdown = (peak - total_value) / peak * 100 if peak > 0 else 0
    account['max_drawdown_pct'] = round(max(account.get('max_drawdown_pct', 0), drawdown), 2)

    save_json(ACCOUNT, account)

    # 记录每日净值
    nav_history = load_json(NAV_HISTORY, [])
    today = time.strftime('%Y-%m-%d')
    # 更新或添加今日净值
    existing = False
    for entry in nav_history:
        if entry.get('date') == today:
            entry['nav'] = round(total_value, 2)
            entry['return_pct'] = account['total_return_pct']
            existing = True
            break
    if not existing:
        nav_history.append({
            'date': today,
            'nav': round(total_value, 2),
            'return_pct': account['total_return_pct']
        })
    save_json(NAV_HISTORY, nav_history)

    print(f"✅ 账户已更新 ({today})")
    print(f"  总资产: ¥{total_value:,.2f}")
    print(f"  持仓市值: ¥{market_value:,.2f}")
    print(f"  可用现金: ¥{account.get('cash', 0):,.2f}")
    print(f"  总收益率: {account['total_return_pct']}%")
    print(f"  最大回撤: {account['max_drawdown_pct']}%")

def show_account():
    """显示账户状态"""
    account = load_json(ACCOUNT)
    if not account:
        print("❌ 账户未初始化")
        print(f"  请先运行: python3 account_manager.py init --capital 100000")
        return

    portfolio = load_json(PORTFOLIO, {'positions': []})
    market_value = 0
    for pos in portfolio.get('positions', []):
        price = pos.get('current_price', pos.get('avg_price', 0))
        qty = pos.get('quantity', 0)
        market_value += price * qty

    total_value = account.get('cash', 0) + market_value
    initial = account.get('initial_capital', 0)

    print("═══ 模拟账户状态 ═══")
    print(f"  初始资金: ¥{initial:,.2f}")
    print(f"  总资产: ¥{total_value:,.2f}")
    print(f"  持仓市值: ¥{market_value:,.2f}")
    print(f"  可用现金: ¥{account.get('cash', 0):,.2f}")
    print(f"  仓位比例: {market_value/total_value*100:.1f}%" if total_value > 0 else "  仓位比例: 0%")
    print(f"  总收益率: {account.get('total_return_pct', 0)}%")
    print(f"  最大回撤: {account.get('max_drawdown_pct', 0)}%")
    print(f"  峰值资产: ¥{account.get('peak_value', initial):,.2f}")
    print(f"  交易次数: {account.get('trade_count', 0)}")
    print(f"  持仓数量: {len(portfolio.get('positions', []))}")
    print(f"  创建时间: {account.get('created_at', '')}")
    print(f"  最后更新: {account.get('last_updated', '')}")

    # 显示持仓明细
    if portfolio.get('positions'):
        print("\n═══ 当前持仓 ═══")
        for pos in portfolio['positions']:
            price = pos.get('current_price', pos.get('avg_price', 0))
            cost = pos.get('avg_price', 0)
            pnl = (price - cost) * pos.get('quantity', 0)
            pnl_pct = (price / cost - 1) * 100 if cost > 0 else 0
            print(f"  {pos['symbol']}: {pos.get('quantity',0)}股 @ ¥{cost:.2f} → ¥{price:.2f} | 浮盈 ¥{pnl:.2f} ({pnl_pct:.1f}%)")

    # 显示净值历史
    nav_history = load_json(NAV_HISTORY, [])
    if nav_history:
        print(f"\n═══ 净值历史 ({len(nav_history)} 天) ═══")
        for entry in nav_history[-10:]:  # 显示最近10天
            print(f"  {entry['date']}: ¥{entry['nav']:,.2f} ({entry.get('return_pct', 0)}%)")

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='command')

    init_p = sub.add_parser('init')
    init_p.add_argument('--capital', type=float, required=True)

    sub.add_parser('show')
    sub.add_parser('update')
    sub.add_parser('history')

    args = p.parse_args()

    if args.command == 'init':
        init_account(args.capital)
    elif args.command == 'show':
        show_account()
    elif args.command == 'update':
        update_account()
    else:
        p.print_help()

if __name__ == '__main__':
    main()
