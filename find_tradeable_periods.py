"""
Script to find periods in historical data where PainBot or GainBot would find trades
This helps identify good date ranges for backtesting
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
from pain_gain_bot.indicators import indicators

def analyze_daily_bias_history(symbol: str, days_back: int = 90):
    """
    Analyze historical daily bias to find good periods for backtesting

    Args:
        symbol: Trading symbol
        days_back: How many days to analyze
    """
    print(f"\n{'='*70}")
    print(f" Analyzing {symbol} - Last {days_back} Days")
    print(f"{'='*70}\n")

    # Initialize MT5
    if not mt5.initialize():
        print(f"ERROR: Failed to initialize MT5: {mt5.last_error()}")
        return

    try:
        # Get daily data
        end_date = datetime.now()
        rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_D1, end_date, days_back)

        if rates is None or len(rates) == 0:
            print(f"ERROR: No data for {symbol}")
            return

        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)

        print(f"Analyzing {len(df)} days of data...\n")

        # Analyze bias for each period
        sell_periods = []
        buy_periods = []

        for i in range(5, len(df)):
            # Get last 5 days
            df_subset = df.iloc[i-5:i]

            # Check bias
            direction, wick_size, wick_50 = indicators.check_wick_direction(df_subset)

            date = df.index[i].strftime('%Y-%m-%d')

            if direction == 'DOWN':
                sell_periods.append({
                    'date': date,
                    'bias': 'SELL',
                    'wick_size': wick_size,
                    'good_for': 'PainBot'
                })
            elif direction == 'UP':
                buy_periods.append({
                    'date': date,
                    'bias': 'BUY',
                    'wick_size': wick_size,
                    'good_for': 'GainBot'
                })

        # Print results
        print(f"SELL Bias Days (good for PainBot): {len(sell_periods)}")
        print(f"BUY Bias Days (good for GainBot): {len(buy_periods)}")
        print(f"Neutral Days: {len(df) - len(sell_periods) - len(buy_periods)}\n")

        # Find consecutive SELL periods
        if sell_periods:
            print("=" * 70)
            print("RECOMMENDED PERIODS FOR PAINBOT (SELL bias):")
            print("=" * 70)

            # Group consecutive days
            current_streak = [sell_periods[0]]
            streaks = []

            for i in range(1, len(sell_periods)):
                prev_date = datetime.strptime(sell_periods[i-1]['date'], '%Y-%m-%d')
                curr_date = datetime.strptime(sell_periods[i]['date'], '%Y-%m-%d')

                if (curr_date - prev_date).days <= 3:  # Allow 2-day gaps
                    current_streak.append(sell_periods[i])
                else:
                    if len(current_streak) >= 3:  # At least 3 days
                        streaks.append(current_streak)
                    current_streak = [sell_periods[i]]

            if len(current_streak) >= 3:
                streaks.append(current_streak)

            # Print top 5 streaks
            streaks.sort(key=lambda x: len(x), reverse=True)

            for i, streak in enumerate(streaks[:5], 1):
                start = streak[0]['date']
                end = streak[-1]['date']
                days = len(streak)
                print(f"\n{i}. {start} to {end} ({days} SELL days)")
                print(f"   Run: python run_backtest.py --symbol '{symbol}' --start {start} --days 7 --bot pain")

        # Find consecutive BUY periods
        if buy_periods:
            print("\n" + "=" * 70)
            print("RECOMMENDED PERIODS FOR GAINBOT (BUY bias):")
            print("=" * 70)

            # Group consecutive days
            current_streak = [buy_periods[0]]
            streaks = []

            for i in range(1, len(buy_periods)):
                prev_date = datetime.strptime(buy_periods[i-1]['date'], '%Y-%m-%d')
                curr_date = datetime.strptime(buy_periods[i]['date'], '%Y-%m-%d')

                if (curr_date - prev_date).days <= 3:
                    current_streak.append(buy_periods[i])
                else:
                    if len(current_streak) >= 3:
                        streaks.append(current_streak)
                    current_streak = [buy_periods[i]]

            if len(current_streak) >= 3:
                streaks.append(current_streak)

            # Print top 5 streaks
            streaks.sort(key=lambda x: len(x), reverse=True)

            for i, streak in enumerate(streaks[:5], 1):
                start = streak[0]['date']
                end = streak[-1]['date']
                days = len(streak)
                print(f"\n{i}. {start} to {end} ({days} BUY days)")
                print(f"   Run: python run_backtest.py --symbol '{symbol}' --start {start} --days 7 --bot gain")

        print("\n" + "=" * 70 + "\n")

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" HISTORICAL BIAS ANALYSIS")
    print(" Finding good periods for backtesting PainBot and GainBot")
    print("=" * 70)

    # Analyze main symbols
    symbols = [
        "PainX 400",
        "PainX 600",
        "GainX 400"
    ]

    for symbol in symbols:
        analyze_daily_bias_history(symbol, days_back=90)

    print("\n" + "=" * 70)
    print(" ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nUse the recommended commands above to run backtests on periods")
    print("where the strategy should actually find trades!\n")
