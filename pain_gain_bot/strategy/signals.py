"""
Signal generation engine for Pain/Gain strategy
Implements multi-timeframe analysis and entry/exit signals
"""

import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime
from ..data.mt5_connector import connector
from ..indicators.technical import indicators
from ..utils.logger import logger
from ..config import config

class SignalEngine:
    """Generates trading signals based on Pain/Gain multi-timeframe rules"""

    def __init__(self):
        self.daily_bias = None  # 'BUY' or 'SELL'
        self.wick_50_level = None
        self.day_stopped = False
        self.last_analysis_time = None

    def analyze_daily_bias(self, symbol: str) -> Tuple[Optional[str], Optional[float]]:
        """
        Analyze D1 timeframe to determine trading bias for the day

        Returns:
            (bias, wick_50_level) - bias is 'BUY', 'SELL', or None
        """
        try:
            df_d1 = connector.get_bars(symbol, 'D1', count=5)
            if df_d1 is None or len(df_d1) < 2:
                logger.warning(f"Insufficient D1 data for {symbol}")
                return None, None

            # Check wick direction
            direction, wick_size, wick_50_level = indicators.check_wick_direction(df_d1)

            if direction == 'UP':
                bias = 'BUY'
                logger.info(f"[OK] {symbol} D1 Bias: BUY (upward wick, 50% level: {wick_50_level:.5f})")
            elif direction == 'DOWN':
                bias = 'SELL'
                logger.info(f"[OK] {symbol} D1 Bias: SELL (downward wick, 50% level: {wick_50_level:.5f})")
            else:
                bias = None
                logger.info(f"○ {symbol} D1: No clear bias")

            self.daily_bias = bias
            self.wick_50_level = wick_50_level
            self.day_stopped = False

            return bias, wick_50_level

        except Exception as e:
            logger.error(f"Error analyzing daily bias for {symbol}", e)
            return None, None

    def check_daily_stop_condition(self, symbol: str, current_price: float) -> bool:
        """
        Check if 50% of D1 wick has been filled (stop trading for the day)

        Returns:
            True if trading should stop
        """
        if self.wick_50_level is None or self.daily_bias is None:
            return False

        if indicators.is_wick_50_percent_filled(current_price,
                                                self.daily_bias.replace('BUY', 'UP').replace('SELL', 'DOWN'),
                                                self.wick_50_level):
            if not self.day_stopped:
                logger.warning(f"[!] {symbol} Daily stop: 50% wick level reached at {current_price:.5f}")
                self.day_stopped = True
            return True

        return False

    def check_h4_confirmation(self, symbol: str, bias: str) -> Tuple[bool, Optional[float]]:
        """
        Check H4 50% Fibonacci confirmation

        Args:
            symbol: Trading symbol
            bias: 'BUY' or 'SELL'

        Returns:
            (confirmed, fib_50_level)
        """
        try:
            df_h4 = connector.get_bars(symbol, 'H4', count=10)
            df_m15 = connector.get_bars(symbol, 'M15', count=50)

            if df_h4 is None or df_m15 is None:
                return False, None

            confirmed, fib_level = indicators.check_h4_50_percent_coverage(df_h4, df_m15, bias)

            if confirmed:
                logger.debug(f"[OK] H4 confirmation: 50% Fib at {fib_level:.5f}")
            else:
                logger.debug(f"✗ H4 not confirmed")

            return confirmed, fib_level

        except Exception as e:
            logger.error(f"Error checking H4 confirmation for {symbol}", e)
            return False, None

    def check_h1_structure(self, symbol: str, bias: str) -> bool:
        """
        Check H1 shingle confirmation

        Args:
            symbol: Trading symbol
            bias: 'BUY' or 'SELL'

        Returns:
            True if H1 structure confirms bias
        """
        try:
            df_h1 = connector.get_bars(symbol, 'H1', count=100)
            if df_h1 is None:
                return False

            shingle, color = indicators.calculate_shingle(df_h1, config.strategy.shingle_ema)
            current_price = df_h1['close'].iloc[-1]

            if bias == 'BUY':
                # Price should be above green shingle
                confirmed = current_price > shingle.iloc[-1] and color == 'GREEN'
            else:  # SELL
                # Price should be below red shingle
                confirmed = current_price < shingle.iloc[-1] and color == 'RED'

            if confirmed:
                logger.debug(f"[OK] H1 shingle: {color} - confirmed")
            else:
                logger.debug(f"✗ H1 shingle: {color} - not confirmed")

            return confirmed

        except Exception as e:
            logger.error(f"Error checking H1 structure for {symbol}", e)
            return False

    def check_m30_m15_filter(self, symbol: str, bias: str) -> bool:
        """
        Check M30 and M15 snake color filter

        Args:
            symbol: Trading symbol
            bias: 'BUY' or 'SELL'

        Returns:
            True if both M30 and M15 snake colors match bias
        """
        try:
            df_m30 = connector.get_bars(symbol, 'M30', count=100)
            df_m15 = connector.get_bars(symbol, 'M15', count=100)

            if df_m30 is None or df_m15 is None:
                return False

            # Calculate snake for M30
            m30_fast, m30_slow, m30_color = indicators.calculate_snake(
                df_m30,
                config.strategy.snake_fast_ema,
                config.strategy.snake_slow_ema
            )

            # Calculate snake for M15
            m15_fast, m15_slow, m15_color = indicators.calculate_snake(
                df_m15,
                config.strategy.snake_fast_ema,
                config.strategy.snake_slow_ema
            )

            if bias == 'BUY':
                # Both should be GREEN
                confirmed = m30_color == 'GREEN' and m15_color == 'GREEN'
            else:  # SELL
                # Both should be RED
                confirmed = m30_color == 'RED' and m15_color == 'RED'

            if confirmed:
                logger.debug(f"[OK] M30/M15 snake: {m30_color}/{m15_color} - confirmed")
            else:
                logger.debug(f"✗ M30/M15 snake: {m30_color}/{m15_color} - not confirmed")

            return confirmed

        except Exception as e:
            logger.error(f"Error checking M30/M15 filter for {symbol}", e)
            return False

    def check_m5_m1_entry(self, symbol: str, bias: str) -> Tuple[bool, Optional[float]]:
        """
        Check M5 and M1 entry conditions with purple line break/retest

        Args:
            symbol: Trading symbol
            bias: 'BUY' or 'SELL'

        Returns:
            (entry_signal, entry_price)
        """
        try:
            df_m5 = connector.get_bars(symbol, 'M5', count=20)
            df_m1 = connector.get_bars(symbol, 'M1', count=20)

            if df_m5 is None or df_m1 is None:
                return False, None

            # Calculate purple line for M5
            purple_line_m5 = indicators.calculate_purple_line(df_m5, config.strategy.purple_line_ema)

            # Calculate purple line and squid for M1
            purple_line_m1 = indicators.calculate_purple_line(df_m1, config.strategy.purple_line_ema)
            squid_m1, squid_color_m1 = indicators.calculate_squid(df_m1, config.strategy.squid_period)

            # Calculate snake for M1
            m1_fast, m1_slow, m1_color = indicators.calculate_snake(
                df_m1,
                config.strategy.snake_fast_ema,
                config.strategy.snake_slow_ema
            )

            # Get current prices
            current_price_m5 = df_m5['close'].iloc[-1]
            current_price_m1 = df_m1['close'].iloc[-1]

            # Check break-retest pattern
            break_retest = indicators.detect_purple_line_break_retest(
                df_m1, purple_line_m1, bias, lookback=5
            )

            # Entry conditions
            entry_signal = False

            if bias == 'BUY':
                # For BUY:
                # 1. M1 price above green snake
                # 2. Purple line break and retest
                # 3. M5 touching purple line or green squid
                # 4. M1 aligned with M5

                condition_1 = current_price_m1 > m1_fast.iloc[-1] and m1_color == 'GREEN'
                condition_2 = break_retest
                condition_3 = abs(current_price_m5 - purple_line_m5.iloc[-1]) < 0.001  # Close to purple line

                entry_signal = condition_1 and condition_2 and condition_3

                if entry_signal:
                    logger.signal('BUY', symbol, 'M1', {
                        'price': current_price_m1,
                        'snake': m1_color,
                        'break_retest': break_retest,
                        'purple_line': purple_line_m1.iloc[-1]
                    })

            else:  # SELL
                # For SELL:
                # 1. M1 price below red snake
                # 2. Purple line break and retest
                # 3. M5 touching purple line or red squid
                # 4. M1 aligned with M5

                condition_1 = current_price_m1 < m1_fast.iloc[-1] and m1_color == 'RED'
                condition_2 = break_retest
                condition_3 = abs(current_price_m5 - purple_line_m5.iloc[-1]) < 0.001

                entry_signal = condition_1 and condition_2 and condition_3

                if entry_signal:
                    logger.signal('SELL', symbol, 'M1', {
                        'price': current_price_m1,
                        'snake': m1_color,
                        'break_retest': break_retest,
                        'purple_line': purple_line_m1.iloc[-1]
                    })

            return entry_signal, current_price_m1 if entry_signal else None

        except Exception as e:
            logger.error(f"Error checking M5/M1 entry for {symbol}", e)
            return False, None

    def generate_signal(self, symbol: str) -> Dict:
        """
        Generate complete trading signal with all confirmations

        Returns:
            Dictionary with signal details:
            {
                'action': 'BUY'/'SELL'/None,
                'symbol': symbol,
                'price': entry_price,
                'confirmations': {...},
                'timestamp': datetime
            }
        """
        print(f"[DEBUG] SignalEngine.generate_signal() called for {symbol}")
        signal = {
            'action': None,
            'symbol': symbol,
            'price': None,
            'confirmations': {},
            'timestamp': datetime.now()
        }

        try:
            # Step 1: Check/refresh daily bias
            print(f"[DEBUG] Step 1: Checking daily bias for {symbol}")
            if self.daily_bias is None or self.last_analysis_time is None or \
               (datetime.now() - self.last_analysis_time).total_seconds() > 3600:
                print(f"[DEBUG] Analyzing daily bias (refresh needed)")
                bias, wick_level = self.analyze_daily_bias(symbol)
                self.last_analysis_time = datetime.now()
            else:
                bias = self.daily_bias
                print(f"[DEBUG] Using cached daily bias: {bias}")

            if bias is None:
                logger.debug(f"{symbol}: No daily bias")
                print(f"[DEBUG] No daily bias detected - returning")
                return signal

            signal['confirmations']['d1_bias'] = bias
            print(f"[DEBUG] Daily bias: {bias}")

            # Step 2: Check if daily stop reached
            print(f"[DEBUG] Step 2: Checking daily stop condition")
            tick = connector.get_tick(symbol)
            if tick is None:
                print(f"[DEBUG] No tick data - returning")
                return signal

            current_price = tick['bid'] if bias == 'SELL' else tick['ask']
            print(f"[DEBUG] Current price: {current_price}")

            if self.check_daily_stop_condition(symbol, current_price):
                logger.debug(f"{symbol}: Daily stop reached")
                print(f"[DEBUG] Daily stop reached - returning")
                signal['confirmations']['day_stopped'] = True
                return signal

            signal['confirmations']['day_stopped'] = False

            # Step 3: H4 50% confirmation
            print(f"[DEBUG] Step 3: Checking H4 confirmation")
            h4_confirmed, fib_level = self.check_h4_confirmation(symbol, bias)
            signal['confirmations']['h4_50_percent'] = h4_confirmed
            print(f"[DEBUG] H4 confirmed: {h4_confirmed}")

            if not h4_confirmed:
                logger.debug(f"{symbol}: H4 not confirmed")
                print(f"[DEBUG] H4 not confirmed - returning")
                return signal

            # Step 4: H1 structure
            print(f"[DEBUG] Step 4: Checking H1 structure")
            h1_confirmed = self.check_h1_structure(symbol, bias)
            signal['confirmations']['h1_shingle'] = h1_confirmed
            print(f"[DEBUG] H1 confirmed: {h1_confirmed}")

            if not h1_confirmed:
                logger.debug(f"{symbol}: H1 not confirmed")
                print(f"[DEBUG] H1 not confirmed - returning")
                return signal

            # Step 5: M30/M15 filter
            print(f"[DEBUG] Step 5: Checking M30/M15 filter")
            m30_m15_confirmed = self.check_m30_m15_filter(symbol, bias)
            signal['confirmations']['m30_m15_snake'] = m30_m15_confirmed
            print(f"[DEBUG] M30/M15 confirmed: {m30_m15_confirmed}")

            if not m30_m15_confirmed:
                logger.debug(f"{symbol}: M30/M15 not confirmed")
                print(f"[DEBUG] M30/M15 not confirmed - returning")
                return signal

            # Step 6: M5/M1 entry
            print(f"[DEBUG] Step 6: Checking M5/M1 entry")
            entry_signal, entry_price = self.check_m5_m1_entry(symbol, bias)
            signal['confirmations']['m5_m1_entry'] = entry_signal
            print(f"[DEBUG] M5/M1 entry signal: {entry_signal}, price: {entry_price}")

            if entry_signal:
                signal['action'] = bias
                signal['price'] = entry_price
                logger.info(f"[*] {bias} SIGNAL for {symbol} at {entry_price:.5f}")
                print(f"[DEBUG] SIGNAL GENERATED: {bias} at {entry_price}")
            else:
                logger.debug(f"{symbol}: M5/M1 entry not confirmed")
                print(f"[DEBUG] M5/M1 entry not confirmed - returning")

            return signal

        except Exception as e:
            logger.error(f"Error generating signal for {symbol}", e)
            print(f"[DEBUG] Exception in generate_signal(): {type(e).__name__}: {e}")
            return signal


# Global signal engine instances (one per bot)
pain_signal_engine = SignalEngine()  # For SELL (Pain)
gain_signal_engine = SignalEngine()  # For BUY (Gain)
