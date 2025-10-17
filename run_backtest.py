"""
Simple script to run backtests from command line

Usage:
    python run_backtest.py --symbol "PainX 400" --days 7
    python run_backtest.py --symbol "GainX 400" --days 30 --bot gain
    python run_backtest.py --symbol "PainX 400" --days 30 --relaxed  # Weakened constraints
"""

import argparse
from datetime import datetime, timedelta
from pain_gain_bot.backtest.historical_backtester import HistoricalBacktester
from pain_gain_bot.backtest.relaxed_backtester import RelaxedBacktester

def main():
    parser = argparse.ArgumentParser(description="Run backtest for Pain/Gain trading strategy")

    parser.add_argument(
        '--symbol',
        type=str,
        default="PainX 400",
        help='Symbol to backtest (default: "PainX 400")'
    )

    parser.add_argument(
        '--bot',
        choices=['pain', 'gain'],
        default='pain',
        help='Bot type: pain=SELL, gain=BUY (default: pain)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to backtest (default: 7)'
    )

    parser.add_argument(
        '--start',
        type=str,
        help='Start date in YYYY-MM-DD format (overrides --days)'
    )

    parser.add_argument(
        '--end',
        type=str,
        help='End date in YYYY-MM-DD format (default: today)'
    )

    parser.add_argument(
        '--balance',
        type=float,
        default=500.0,
        help='Initial balance in USD (default: 500)'
    )

    parser.add_argument(
        '--export',
        type=str,
        help='Export results to CSV file'
    )

    parser.add_argument(
        '--relaxed',
        action='store_true',
        help='Use relaxed mode (weakened constraints, more trades)'
    )

    args = parser.parse_args()

    # Calculate dates
    if args.end:
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    else:
        end_date = datetime.now()

    if args.start:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
    else:
        start_date = end_date - timedelta(days=args.days)

    print("\n" + "="*70)
    print(" Pain/Gain Strategy Backtesting")
    print("="*70)
    print(f"\nSymbol: {args.symbol}")
    print(f"Bot type: {args.bot.upper()} ({'SELL' if args.bot == 'pain' else 'BUY'})")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Initial balance: ${args.balance:.2f}")

    if args.relaxed:
        print(f"Mode: RELAXED (weakened constraints)")
        print(f"  - Daily bias is informational only")
        print(f"  - Daily stop is warning only")
        print(f"  - H4 Fib, H1 Shingle, Purple Line are optional")
        print(f"  - Only ONE of M30/M15 snake required (not both)")
    else:
        print(f"Mode: STRICT (all 6 steps required)")

    print(f"\nStarting backtest...\n")

    # Run backtest with selected backtester
    if args.relaxed:
        backtester = RelaxedBacktester(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            initial_balance=args.balance
        )
    else:
        backtester = HistoricalBacktester(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            initial_balance=args.balance
        )

    bot_type = 'PAIN' if args.bot == 'pain' else 'GAIN'
    results = backtester.run_backtest(args.symbol, bot_type=bot_type)

    # Export if requested
    if args.export:
        backtester.export_results(args.export)
        print(f"\nResults exported to: {args.export}")
    else:
        # Default export filename
        filename = f"backtest_{args.symbol.replace(' ', '_')}_{args.days}d.csv"
        backtester.export_results(filename)
        print(f"\nResults exported to: {filename}")

    print("\nBacktest complete!")
    print("="*70 + "\n")

    return results


if __name__ == "__main__":
    main()
