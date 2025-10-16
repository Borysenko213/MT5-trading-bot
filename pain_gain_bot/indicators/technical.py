"""
Technical indicators for Pain/Gain strategy
Implements snake, shingle, squid, purple line, and Fibonacci calculations
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
from ..utils.logger import logger

class TechnicalIndicators:
    """Collection of technical indicators for Pain/Gain strategy"""

    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()

    @staticmethod
    def calculate_snake(df: pd.DataFrame, fast_period: int = 8,
                       slow_period: int = 21) -> Tuple[pd.Series, pd.Series, str]:
        """
        Calculate 'Snake' indicator - EMA crossover system

        Returns:
            fast_ema: Fast EMA series
            slow_ema: Slow EMA series
            color: 'RED' or 'GREEN' based on current alignment
        """
        fast_ema = TechnicalIndicators.calculate_ema(df['close'], fast_period)
        slow_ema = TechnicalIndicators.calculate_ema(df['close'], slow_period)

        # Determine color: GREEN when fast > slow, RED when fast < slow
        current_color = 'GREEN' if fast_ema.iloc[-1] > slow_ema.iloc[-1] else 'RED'

        return fast_ema, slow_ema, current_color

    @staticmethod
    def calculate_shingle(df: pd.DataFrame, period: int = 50) -> Tuple[pd.Series, str]:
        """
        Calculate 'Shingle' indicator - thick EMA

        Returns:
            ema: EMA series
            color: 'RED' or 'GREEN' based on price position
        """
        ema = TechnicalIndicators.calculate_ema(df['close'], period)

        # Color based on price relative to EMA
        current_price = df['close'].iloc[-1]
        current_color = 'GREEN' if current_price > ema.iloc[-1] else 'RED'

        return ema, current_color

    @staticmethod
    def calculate_purple_line(df: pd.DataFrame, period: int = 34) -> pd.Series:
        """
        Calculate 'Purple Line' indicator
        Based on EMA - this is the key break/retest line
        """
        return TechnicalIndicators.calculate_ema(df['close'], period)

    @staticmethod
    def calculate_squid(df: pd.DataFrame, period: int = 13) -> Tuple[pd.Series, str]:
        """
        Calculate 'Squid' indicator
        Additional confirmation indicator (appears to be another EMA)

        Returns:
            ema: EMA series
            color: 'RED' or 'GREEN' based on trend
        """
        ema = TechnicalIndicators.calculate_ema(df['close'], period)

        # Determine color based on slope/trend
        if len(ema) >= 2:
            current_color = 'GREEN' if ema.iloc[-1] > ema.iloc[-2] else 'RED'
        else:
            current_color = 'GREEN'

        return ema, current_color

    @staticmethod
    def calculate_fibonacci_retracement(high: float, low: float) -> dict:
        """
        Calculate Fibonacci retracement levels

        Args:
            high: Highest point
            low: Lowest point

        Returns:
            Dictionary of Fibonacci levels
        """
        diff = high - low

        levels = {
            '0.0': high,
            '23.6': high - (0.236 * diff),
            '38.2': high - (0.382 * diff),
            '50.0': high - (0.500 * diff),
            '61.8': high - (0.618 * diff),
            '100.0': low,
        }

        return levels

    @staticmethod
    def find_swing_high_low(df: pd.DataFrame, lookback: int = 20) -> Tuple[float, float]:
        """
        Find swing high and low in recent bars

        Args:
            df: OHLC DataFrame
            lookback: Number of bars to look back

        Returns:
            (swing_high, swing_low)
        """
        recent = df.tail(lookback)
        swing_high = recent['high'].max()
        swing_low = recent['low'].min()

        return swing_high, swing_low

    @staticmethod
    def check_wick_direction(df_daily: pd.DataFrame) -> Tuple[str, float, float]:
        """
        Analyze D1 candle wick to determine bias

        Args:
            df_daily: Daily OHLC data

        Returns:
            direction: 'UP' or 'DOWN'
            wick_size: Size of dominant wick
            wick_50_percent: 50% level of the wick
        """
        if len(df_daily) < 2:
            return 'NONE', 0.0, 0.0

        # Get previous day's candle (index -2, since -1 is current incomplete day)
        prev_candle = df_daily.iloc[-2]

        open_price = prev_candle['open']
        close_price = prev_candle['close']
        high_price = prev_candle['high']
        low_price = prev_candle['low']

        # Determine body
        body_top = max(open_price, close_price)
        body_bottom = min(open_price, close_price)
        body_size = body_top - body_bottom

        # Calculate wicks
        upper_wick = high_price - body_top
        lower_wick = body_bottom - low_price

        total_range = high_price - low_price

        # Check if body is small (< 30% of total range)
        if total_range > 0:
            body_ratio = body_size / total_range
        else:
            body_ratio = 1.0

        # Determine direction based on longest wick
        if upper_wick > lower_wick:
            direction = 'UP'
            wick_size = upper_wick
            wick_start = body_top
            wick_end = high_price
        else:
            direction = 'DOWN'
            wick_size = lower_wick
            wick_start = low_price
            wick_end = body_bottom

        # Calculate 50% level of wick
        wick_50_percent = (wick_start + wick_end) / 2

        logger.debug(
            f"D1 Wick Analysis: direction={direction}, "
            f"body_ratio={body_ratio:.2f}, wick_size={wick_size:.5f}, "
            f"50%_level={wick_50_percent:.5f}"
        )

        return direction, wick_size, wick_50_percent

    @staticmethod
    def is_wick_50_percent_filled(current_price: float, wick_direction: str,
                                   wick_50_level: float) -> bool:
        """
        Check if current day has filled 50% of previous day's wick

        Args:
            current_price: Current market price
            wick_direction: 'UP' or 'DOWN'
            wick_50_level: 50% level price

        Returns:
            True if 50% is filled (stop trading)
        """
        if wick_direction == 'UP':
            # For upward wick (BUY day), check if price has risen to 50% level
            return current_price >= wick_50_level
        elif wick_direction == 'DOWN':
            # For downward wick (SELL day), check if price has fallen to 50% level
            return current_price <= wick_50_level

        return False

    @staticmethod
    def check_h4_50_percent_coverage(df_h4: pd.DataFrame, df_m15: pd.DataFrame,
                                      direction: str) -> Tuple[bool, float]:
        """
        Check if previous H4 candle covers 50% of M15 Fibonacci range

        Args:
            df_h4: H4 OHLC data
            df_m15: M15 OHLC data
            direction: 'BUY' or 'SELL'

        Returns:
            (covers_50_percent, fib_50_level)
        """
        if len(df_h4) < 2 or len(df_m15) < 20:
            return False, 0.0

        # Find swing high/low in M15 (recent 20 bars)
        swing_high, swing_low = TechnicalIndicators.find_swing_high_low(df_m15, lookback=20)

        # Calculate Fibonacci
        if direction == 'SELL':
            fib_levels = TechnicalIndicators.calculate_fibonacci_retracement(swing_high, swing_low)
        else:  # BUY
            fib_levels = TechnicalIndicators.calculate_fibonacci_retracement(swing_low, swing_high)

        fib_50_level = fib_levels['50.0']

        # Check previous H4 candle (find largest body)
        # Look at last 3 H4 candles and pick the one with largest body
        recent_h4 = df_h4.tail(4).head(3)  # Skip current incomplete candle

        bodies = []
        for idx, candle in recent_h4.iterrows():
            body_size = abs(candle['close'] - candle['open'])
            bodies.append((body_size, candle))

        if not bodies:
            return False, fib_50_level

        # Get candle with largest body
        largest_body_candle = max(bodies, key=lambda x: x[0])[1]

        # Check if this candle covered the 50% level
        candle_high = largest_body_candle['high']
        candle_low = largest_body_candle['low']

        covers_50 = candle_low <= fib_50_level <= candle_high

        logger.debug(
            f"H4 50% Check: direction={direction}, "
            f"fib_50={fib_50_level:.5f}, "
            f"H4_range=[{candle_low:.5f}, {candle_high:.5f}], "
            f"covers={covers_50}"
        )

        return covers_50, fib_50_level

    @staticmethod
    def detect_purple_line_break_retest(df: pd.DataFrame, purple_line: pd.Series,
                                        direction: str, lookback: int = 5) -> bool:
        """
        Detect break and retest of purple line

        Args:
            df: OHLC DataFrame (M1 or M5)
            purple_line: Purple line indicator series
            direction: 'BUY' or 'SELL'
            lookback: Number of bars to look back for break

        Returns:
            True if valid break-retest pattern detected
        """
        if len(df) < lookback + 1 or len(purple_line) < lookback + 1:
            return False

        recent_bars = df.tail(lookback + 1)
        recent_purple = purple_line.tail(lookback + 1)

        # Check for break followed by retest
        break_detected = False
        retest_detected = False

        for i in range(len(recent_bars) - 1):
            bar = recent_bars.iloc[i]
            purple_val = recent_purple.iloc[i]

            if direction == 'BUY':
                # For BUY: price should break above purple line
                if bar['close'] > purple_val and bar['open'] <= purple_val:
                    break_detected = True
            else:  # SELL
                # For SELL: price should break below purple line
                if bar['close'] < purple_val and bar['open'] >= purple_val:
                    break_detected = True

        if break_detected:
            # Check for retest in most recent bars
            current_bar = recent_bars.iloc[-1]
            current_purple = recent_purple.iloc[-1]

            # Retest: price touches or slightly crosses purple line again
            tolerance = 0.0002  # Small tolerance for "touch"

            if direction == 'BUY':
                # Price should come back down to touch purple from above
                retest_detected = abs(current_bar['low'] - current_purple) <= tolerance
            else:  # SELL
                # Price should come back up to touch purple from below
                retest_detected = abs(current_bar['high'] - current_purple) <= tolerance

        return break_detected and retest_detected


class IndicatorCache:
    """Cache for calculated indicators to avoid recalculation"""

    def __init__(self):
        self.cache = {}
        self.max_age_seconds = 60  # Cache validity

    def get(self, key: str) -> Optional[any]:
        """Retrieve from cache if valid"""
        if key in self.cache:
            timestamp, value = self.cache[key]
            if (pd.Timestamp.now() - timestamp).total_seconds() < self.max_age_seconds:
                return value
        return None

    def set(self, key: str, value: any):
        """Store in cache with timestamp"""
        self.cache[key] = (pd.Timestamp.now(), value)

    def clear(self):
        """Clear all cache"""
        self.cache.clear()


# Global indicator instance
indicators = TechnicalIndicators()
indicator_cache = IndicatorCache()
