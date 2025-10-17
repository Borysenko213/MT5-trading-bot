"""
Relaxed Historical Backtester - Weakened Constraints for Testing
This version relaxes the 6-step strategy to show more trades
"""

from .historical_backtester import HistoricalBacktester
from ..indicators.technical import indicators
from ..config import config
from typing import Dict, Optional
from datetime import datetime


class RelaxedBacktester(HistoricalBacktester):
    """
    Backtester with relaxed constraints to generate more trades
    """

    def check_signal_at_time(self, symbol: str, check_time: datetime, bot_type: str, verbose: bool = False) -> Optional[Dict]:
        """
        Check for trading signal with RELAXED constraints

        RELAXED RULES:
        - Step 1: Daily bias is informational only (not required)
        - Step 2: Daily stop is warning only (not enforced)
        - Step 3: H4 Fib is optional
        - Step 4: H1 Shingle is optional
        - Step 5: Requires only ONE of M30/M15 snake (not both)
        - Step 6: Purple line is optional
        """
        try:
            # Step 1: Daily bias (INFORMATIONAL ONLY)
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
                daily_bias = 'NEUTRAL'
                if verbose:
                    print(f"[VERBOSE] {check_time}: Daily bias is NEUTRAL")

            if verbose:
                if bot_type == 'PAIN' and daily_bias != 'SELL':
                    print(f"[VERBOSE] {check_time}: ⚠ Daily bias is {daily_bias} (want SELL for PAIN, but trading anyway)")
                elif bot_type == 'GAIN' and daily_bias != 'BUY':
                    print(f"[VERBOSE] {check_time}: ⚠ Daily bias is {daily_bias} (want BUY for GAIN, but trading anyway)")
                else:
                    print(f"[VERBOSE] {check_time}: ✓ Step 1: Daily bias = {daily_bias} (matches {bot_type})")

            # For signal generation, use preferred bias
            signal_bias = 'SELL' if bot_type == 'PAIN' else 'BUY'

            # Step 2: Daily stop (WARNING ONLY)
            current_price = df_d1['close'].iloc[-1]
            if indicators.is_wick_50_percent_filled(current_price, direction, wick_50_level):
                if verbose:
                    print(f"[VERBOSE] {check_time}: ⚠ Step 2: Daily stop reached (continuing anyway)")
            else:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✓ Step 2: Daily stop not reached")

            # Step 3: H4 50% Fibonacci (OPTIONAL)
            df_h4 = self.get_bars_up_to(symbol, 'H4', check_time, count=10)
            df_m15 = self.get_bars_up_to(symbol, 'M15', check_time, count=50)

            if df_h4 is None or df_m15 is None:
                return None

            h4_confirmed, fib_level = indicators.check_h4_50_percent_coverage(df_h4, df_m15, signal_bias)
            if not h4_confirmed:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ⚠ Step 3: H4 Fib not confirmed (continuing anyway)")
            else:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✓ Step 3: H4 Fib confirmed")

            # Step 4: H1 shingle (OPTIONAL)
            df_h1 = self.get_bars_up_to(symbol, 'H1', check_time, count=100)
            if df_h1 is None:
                return None

            shingle, color = indicators.calculate_shingle(df_h1, config.strategy.shingle_ema)
            if signal_bias == 'BUY':
                h1_confirmed = current_price > shingle.iloc[-1] and color == 'GREEN'
            else:  # SELL
                h1_confirmed = current_price < shingle.iloc[-1] and color == 'RED'

            if not h1_confirmed:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ⚠ Step 4: H1 shingle not confirmed (continuing anyway)")
            else:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✓ Step 4: H1 shingle confirmed")

            # Step 5: M30/M15 snake (REQUIRE AT LEAST ONE - RELAXED)
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

            # RELAXED: Require only ONE of M30 or M15, not both
            if signal_bias == 'BUY':
                m30_ok = m30_color == 'GREEN'
                m15_ok = m15_color == 'GREEN'
            else:  # SELL
                m30_ok = m30_color == 'RED'
                m15_ok = m15_color == 'RED'

            if not (m30_ok or m15_ok):
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✗ Step 5: Neither M30 nor M15 snake confirmed (M30:{m30_color}, M15:{m15_color})")
                return None

            if verbose:
                if m30_ok and m15_ok:
                    print(f"[VERBOSE] {check_time}: ✓✓ Step 5: BOTH M30 and M15 snake confirmed")
                elif m30_ok:
                    print(f"[VERBOSE] {check_time}: ✓ Step 5: M30 snake confirmed (M15:{m15_color})")
                else:
                    print(f"[VERBOSE] {check_time}: ✓ Step 5: M15 snake confirmed (M30:{m30_color})")

            # Step 6: M5/M1 entry (OPTIONAL)
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
                df_entry, purple_line, signal_bias, lookback=5
            )

            if not break_retest:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ⚠ Step 6: Purple line not confirmed (continuing anyway)")
            else:
                if verbose:
                    print(f"[VERBOSE] {check_time}: ✓ Step 6: Purple line confirmed")

            # Generate signal (only M30/M15 snake required)
            entry_price = df_entry['close'].iloc[-1]

            if verbose:
                print(f"[VERBOSE] {check_time}: ✓✓✓ SIGNAL GENERATED (RELAXED MODE)!")

            return {
                'action': signal_bias,
                'symbol': symbol,
                'price': entry_price,
                'time': check_time,
                'confirmations': {
                    'd1_bias': daily_bias,
                    'h4_fib': h4_confirmed,
                    'h1_shingle': h1_confirmed,
                    'm30_snake': m30_ok,
                    'm15_snake': m15_ok,
                    'm5_m1_entry': break_retest
                }
            }

        except Exception as e:
            print(f"[BACKTEST] Error checking signal: {e}")
            return None
