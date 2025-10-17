"""
Real Historical Backtesting Engine
Uses actual historical data from MT5 to simulate strategy performance
"""

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ..data.mt5_connector import connector
from ..indicators.technical import indicators
from ..utils.logger import logger
from ..config import config


class HistoricalBacktester:
    """
    Proper backtesting engine that replays historical data chronologically
    """

    def __init__(self, start_date: str, end_date: str, initial_balance: float = 500.0):
        """
        Initialize backtester

        Args:
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
            initial_balance: Starting balance
        """
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.initial_balance = initial_balance
        self.balance = initial_balance

        self.positions = []
        self.trades = []
        self.equity_curve = []

        # Cache for historical data
        self.historical_cache = {}

        print(f"[BACKTEST] Initializing historical backtester")
        print(f"[BACKTEST] Period: {start_date} to {end_date}")
        print(f"[BACKTEST] Initial balance: ${initial_balance}")

    def load_historical_data(self, symbol: str) -> bool:
        """
        Pre-load all historical data needed for backtesting

        Args:
            symbol: Trading symbol

        Returns:
            True if data loaded successfully
        """
        print(f"[BACKTEST] Loading historical data for {symbol}...")

        # Calculate total days needed
        days_needed = (self.end_date - self.start_date).days + 100  # Extra buffer

        # M1 is optional - not all brokers keep long M1 history
        timeframes = {
            'D1': mt5.TIMEFRAME_D1,
            'H4': mt5.TIMEFRAME_H4,
            'H1': mt5.TIMEFRAME_H1,
            'M30': mt5.TIMEFRAME_M30,
            'M15': mt5.TIMEFRAME_M15,
            'M5': mt5.TIMEFRAME_M5,
        }

        self.historical_cache[symbol] = {}

        for tf_name, tf_const in timeframes.items():
            print(f"[BACKTEST]   Loading {tf_name} data...")

            # Calculate bars needed based on timeframe
            bars_per_day = {
                'D1': 1,
                'H4': 6,
                'H1': 24,
                'M30': 48,
                'M15': 96,
                'M5': 288,
                'M1': 1440
            }

            bars_needed = days_needed * bars_per_day.get(tf_name, 100) + 500

            # Get historical bars from MT5
            rates = mt5.copy_rates_from(
                symbol,
                tf_const,
                self.end_date,
                bars_needed
            )

            if rates is None or len(rates) == 0:
                print(f"[BACKTEST] WARNING: No {tf_name} data for {symbol}")
                # M1 is optional - continue without it
                if tf_name == 'M1':
                    print(f"[BACKTEST]   (M1 data not available - will use M5 instead)")
                    continue
                else:
                    print(f"[BACKTEST] ERROR: Missing required {tf_name} data")
                    return False

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)

            self.historical_cache[symbol][tf_name] = df
            print(f"[BACKTEST]   ✓ Loaded {len(df)} {tf_name} bars")

        print(f"[BACKTEST] Historical data loaded successfully")
        return True

    def get_bars_up_to(self, symbol: str, timeframe: str, current_time: datetime, count: int = 500) -> Optional[pd.DataFrame]:
        """
        Get historical bars UP TO a specific point in time (no future peeking)

        Args:
            symbol: Trading symbol
            timeframe: Timeframe (D1, H4, H1, M30, M15, M5, M1)
            current_time: Current simulation time
            count: Number of bars to return

        Returns:
            DataFrame with bars up to current_time
        """
        if symbol not in self.historical_cache:
            return None

        if timeframe not in self.historical_cache[symbol]:
            return None

        df = self.historical_cache[symbol][timeframe]

        # Get only bars BEFORE current_time (no future peeking!)
        df_filtered = df[df.index <= current_time]

        if len(df_filtered) == 0:
            return None

        # Return last 'count' bars
        return df_filtered.tail(count)

    def check_signal_at_time(self, symbol: str, check_time: datetime, bot_type: str, verbose: bool = False) -> Optional[Dict]:
        """
        Check for trading signal at a specific point in time using historical data

        Args:
            symbol: Trading symbol
            check_time: Time to check signal
            bot_type: 'PAIN' (SELL) or 'GAIN' (BUY)
            verbose: Print detailed step-by-step info

        Returns:
            Signal dictionary or None
        """
        try:
            # This implements the 6-step confirmation process using historical data

            # Step 1: Daily bias from D1
            df_d1 = self.get_bars_up_to(symbol, 'D1', check_time, count=5)
            if df_d1 is None or len(df_d1) < 2:
                if verbose:
                    print(f"[VERBOSE] {check_time}: No D1 data")
                return None

            direction, wick_size, wick_50_level = indicators.check_wick_direction(df_d1)

            if direction == 'UP':
                daily_bias = 'BUY'
            elif direction == 'DOWN':
                daily_bias = 'SELL'
            else:
                if verbose:
                    print(f"[VERBOSE] {check_time}: No daily bias detected")
                return None

            # Filter by bot type
            if bot_type == 'PAIN' and daily_bias != 'SELL':
                if verbose:
                    print(f"[VERBOSE] {check_time}: Daily bias is {daily_bias}, need SELL for PAIN bot")
                return None
            if bot_type == 'GAIN' and daily_bias != 'BUY':
                if verbose:
                    print(f"[VERBOSE] {check_time}: Daily bias is {daily_bias}, need BUY for GAIN bot")
                return None

            if verbose:
                print(f"[VERBOSE] {check_time}: ✓ Step 1: Daily bias = {daily_bias}")

            # Step 2: Check daily stop (50% wick filled)
            current_price = df_d1['close'].iloc[-1]
            if indicators.is_wick_50_percent_filled(current_price, direction, wick_50_level):
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✗ Step 2: Daily stop reached (50% wick filled)")
                return None  # Daily stop reached

            if verbose:
                print(f"[VERBOSE] {check_time}: ✓ Step 2: Daily stop not reached")

            # Step 3: H4 50% Fibonacci confirmation
            df_h4 = self.get_bars_up_to(symbol, 'H4', check_time, count=10)
            df_m15 = self.get_bars_up_to(symbol, 'M15', check_time, count=50)

            if df_h4 is None or df_m15 is None:
                return None

            h4_confirmed, fib_level = indicators.check_h4_50_percent_coverage(df_h4, df_m15, daily_bias)
            if not h4_confirmed:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✗ Step 3: H4 50% Fib not confirmed")
                return None

            if verbose:
                print(f"[VERBOSE] {check_time}: ✓ Step 3: H4 50% Fib confirmed")

            # Step 4: H1 shingle confirmation
            df_h1 = self.get_bars_up_to(symbol, 'H1', check_time, count=100)
            if df_h1 is None:
                return None

            shingle, color = indicators.calculate_shingle(df_h1, config.strategy.shingle_ema)
            if daily_bias == 'BUY':
                h1_confirmed = current_price > shingle.iloc[-1] and color == 'GREEN'
            else:  # SELL
                h1_confirmed = current_price < shingle.iloc[-1] and color == 'RED'

            if not h1_confirmed:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✗ Step 4: H1 shingle not confirmed")
                return None

            if verbose:
                print(f"[VERBOSE] {check_time}: ✓ Step 4: H1 shingle confirmed")

            # Step 5: M30/M15 snake filter
            df_m30 = self.get_bars_up_to(symbol, 'M30', check_time, count=100)
            if df_m30 is None:
                return None

            m30_fast, m30_slow, m30_color = indicators.calculate_snake(
                df_m30,
                config.strategy.snake_fast_ema,
                config.strategy.snake_slow_ema
            )

            m15_fast, m15_slow, m15_color = indicators.calculate_snake(
                df_m15,
                config.strategy.snake_fast_ema,
                config.strategy.snake_slow_ema
            )

            if daily_bias == 'BUY':
                m30_m15_confirmed = m30_color == 'GREEN' and m15_color == 'GREEN'
            else:  # SELL
                m30_m15_confirmed = m30_color == 'RED' and m15_color == 'RED'

            if not m30_m15_confirmed:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✗ Step 5: M30/M15 snake not confirmed (M30:{m30_color}, M15:{m15_color})")
                return None

            if verbose:
                print(f"[VERBOSE] {check_time}: ✓ Step 5: M30/M15 snake confirmed")

            # Step 6: M5/M1 entry with purple line
            # Use M1 if available, otherwise use M5
            df_m5 = self.get_bars_up_to(symbol, 'M5', check_time, count=20)
            df_m1 = self.get_bars_up_to(symbol, 'M1', check_time, count=20)

            if df_m5 is None:
                return None

            # Use M1 if available, otherwise fall back to M5
            if df_m1 is not None and len(df_m1) > 0:
                df_entry = df_m1
            else:
                df_entry = df_m5

            purple_line = indicators.calculate_purple_line(df_entry, config.strategy.purple_line_ema)
            break_retest = indicators.detect_purple_line_break_retest(
                df_entry, purple_line, daily_bias, lookback=5
            )

            if not break_retest:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✗ Step 6: Purple line break/retest not confirmed")
                return None

            # All 6 steps confirmed! Generate signal
            entry_price = df_entry['close'].iloc[-1]

            if verbose:
                print(f"[VERBOSE] {check_time}: ✓✓✓ ALL 6 STEPS CONFIRMED! SIGNAL GENERATED!")

            return {
                'action': daily_bias,
                'symbol': symbol,
                'price': entry_price,
                'time': check_time,
                'confirmations': {
                    'd1_bias': daily_bias,
                    'h4_fib': h4_confirmed,
                    'h1_shingle': h1_confirmed,
                    'm30_m15_snake': m30_m15_confirmed,
                    'm5_m1_entry': True
                }
            }

        except Exception as e:
            print(f"[BACKTEST] Error checking signal: {e}")
            return None

    def simulate_trade_exit(self, position: Dict, exit_time: datetime, symbol: str) -> float:
        """
        Calculate P/L for a trade based on actual historical price movement

        Args:
            position: Position dictionary
            exit_time: When to exit
            symbol: Trading symbol

        Returns:
            P/L in USD
        """
        # Get M1 data at exit time, or M5 if M1 not available
        df_m1 = self.get_bars_up_to(symbol, 'M1', exit_time, count=1)

        if df_m1 is not None and len(df_m1) > 0:
            exit_price = df_m1['close'].iloc[-1]
        else:
            # Fallback to M5 if M1 not available
            df_m5 = self.get_bars_up_to(symbol, 'M5', exit_time, count=1)
            if df_m5 is None or len(df_m5) == 0:
                return 0.0
            exit_price = df_m5['close'].iloc[-1]
        entry_price = position['entry_price']
        volume = position['volume']
        action = position['action']

        # Calculate pip movement
        if action == 'SELL':
            pip_movement = entry_price - exit_price
        else:  # BUY
            pip_movement = exit_price - entry_price

        # Convert to USD (simplified - assumes 1 pip = $0.10 for 0.01 lot)
        # For synthetic indices, contract size is usually 1.0
        pnl = pip_movement * volume * 10000  # Rough approximation

        return pnl

    def run_backtest(self, symbol: str, bot_type: str = 'PAIN') -> Dict:
        """
        Run complete backtest

        Args:
            symbol: Trading symbol
            bot_type: 'PAIN' or 'GAIN'

        Returns:
            Results dictionary
        """
        print(f"\n[BACKTEST] ========================================")
        print(f"[BACKTEST] Running backtest for {symbol}")
        print(f"[BACKTEST] Bot type: {bot_type}")
        print(f"[BACKTEST] ========================================\n")

        # Connect to MT5
        if not connector.initialize(use_demo=True):
            print("[BACKTEST] ERROR: Failed to connect to MT5")
            print("[BACKTEST] Make sure MetaTrader 5 is open and logged in!")
            return None

        # Load all historical data
        if not self.load_historical_data(symbol):
            print("[BACKTEST] ERROR: Failed to load historical data")
            return None

        # Run simulation day by day, checking every 5 minutes
        current_date = self.start_date
        trade_count = 0
        checks_done = 0

        print(f"\n[BACKTEST] Starting simulation...")
        print(f"[BACKTEST] Checking every 5 minutes for signals...")
        print(f"[BACKTEST] (Verbose output enabled for first day)\n")

        while current_date <= self.end_date:
            day_str = current_date.strftime('%Y-%m-%d')

            # Check signals every 5 minutes during the day
            for hour in range(0, 24):
                for minute in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
                    check_time = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                    if check_time > self.end_date:
                        break

                    checks_done += 1

                    # Enable verbose for first 50 checks to see what's happening
                    verbose = checks_done <= 50

                    # Check for signal
                    signal = self.check_signal_at_time(symbol, check_time, bot_type, verbose=verbose)

                    if signal:
                        # Execute trade
                        lot_size = config.risk.lot_size

                        position = {
                            'symbol': symbol,
                            'action': signal['action'],
                            'entry_price': signal['price'],
                            'entry_time': check_time,
                            'volume': lot_size,
                            'hold_minutes': config.strategy.hold_minutes
                        }

                        self.positions.append(position)
                        trade_count += 1

                        print(f"[BACKTEST] Trade #{trade_count}: {signal['action']} @ {signal['price']:.2f} at {check_time.strftime('%Y-%m-%d %H:%M')}")

                    # Check if any positions should close
                    for pos in self.positions[:]:
                        hold_time = (check_time - pos['entry_time']).total_seconds() / 60

                        if hold_time >= pos['hold_minutes']:
                            # Close position
                            pnl = self.simulate_trade_exit(pos, check_time, symbol)
                            self.balance += pnl

                            trade_record = {
                                **pos,
                                'exit_time': check_time,
                                'exit_reason': 'Hold period complete',
                                'pnl': pnl,
                                'balance_after': self.balance
                            }

                            self.trades.append(trade_record)
                            self.positions.remove(pos)

                            print(f"[BACKTEST]   Closed: P/L ${pnl:.2f} | Balance: ${self.balance:.2f}")

            # Progress update
            if current_date.day == 1 or current_date == self.end_date:
                print(f"[BACKTEST] Progress: {day_str} | Trades: {trade_count} | Balance: ${self.balance:.2f}")

            # Next day
            current_date += timedelta(days=1)

        # Close any remaining positions
        for pos in self.positions[:]:
            pnl = self.simulate_trade_exit(pos, self.end_date, symbol)
            self.balance += pnl

            trade_record = {
                **pos,
                'exit_time': self.end_date,
                'exit_reason': 'Backtest end',
                'pnl': pnl,
                'balance_after': self.balance
            }

            self.trades.append(trade_record)

        self.positions = []

        # Calculate statistics
        results = self._calculate_statistics()

        print(f"\n[BACKTEST] ========================================")
        print(f"[BACKTEST] BACKTEST COMPLETE")
        print(f"[BACKTEST] ========================================")
        print(f"[BACKTEST] Signal checks: {checks_done}")
        print(f"[BACKTEST] Total trades: {results['total_trades']}")
        print(f"[BACKTEST] Winning trades: {results['winning_trades']} ({results['win_rate']:.1f}%)")
        print(f"[BACKTEST] Final balance: ${results['final_balance']:.2f}")
        print(f"[BACKTEST] Total P/L: ${results['total_pnl']:.2f} ({results['return_pct']:.2f}%)")
        print(f"[BACKTEST] ========================================\n")

        return results

    def _calculate_statistics(self) -> Dict:
        """Calculate performance statistics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'final_balance': self.balance,
                'total_pnl': 0,
                'return_pct': 0,
                'avg_win': 0,
                'avg_loss': 0
            }

        winning = [t for t in self.trades if t.get('pnl', 0) > 0]
        losing = [t for t in self.trades if t.get('pnl', 0) <= 0]
        total_pnl = sum(t.get('pnl', 0) for t in self.trades)

        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(self.trades)) * 100 if self.trades else 0,
            'final_balance': self.balance,
            'total_pnl': total_pnl,
            'return_pct': (total_pnl / self.initial_balance) * 100,
            'avg_win': sum(t['pnl'] for t in winning) / len(winning) if winning else 0,
            'avg_loss': sum(t['pnl'] for t in losing) / len(losing) if losing else 0,
            'trades': self.trades
        }

    def export_results(self, filepath: str = "backtest_results.csv"):
        """Export results to CSV"""
        if not self.trades:
            print("[BACKTEST] No trades to export")
            df = pd.DataFrame(columns=[
                'symbol', 'action', 'entry_price', 'entry_time', 'volume',
                'hold_minutes', 'exit_time', 'exit_reason', 'pnl', 'balance_after'
            ])
            df.to_csv(filepath, index=False)
            print(f"[BACKTEST] Empty results file created: {filepath}")
            return

        df = pd.DataFrame(self.trades)
        df.to_csv(filepath, index=False)
        print(f"[BACKTEST] Results exported to: {filepath}")
