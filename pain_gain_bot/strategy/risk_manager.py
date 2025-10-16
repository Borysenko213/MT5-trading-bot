"""
Risk management module for Pain/Gain strategy
Handles daily stops, position sizing, and risk limits
"""

from datetime import datetime, time
from typing import Dict, Tuple
from ..data.mt5_connector import connector
from ..utils.logger import logger
from ..config import config

class RiskManager:
    """Manages risk limits and position sizing"""

    def __init__(self):
        self.daily_start_balance = 0.0
        self.daily_profit = 0.0
        self.daily_loss = 0.0
        self.trades_today = 0
        self.last_reset_date = None
        self.trading_halted = False
        self.halt_reason = ""

    def initialize(self):
        """Initialize risk manager with current account balance"""
        print("[DEBUG] RiskManager.initialize() called")
        account_info = connector.get_account_info()
        if account_info:
            self.daily_start_balance = account_info['balance']
            self.last_reset_date = datetime.now().date()
            logger.info(f"Risk Manager initialized: Start balance ${self.daily_start_balance:.2f}")
            print(f"[DEBUG] Risk manager initialized: balance=${self.daily_start_balance:.2f}")
        else:
            print("[DEBUG] Failed to get account info for risk manager initialization")

    def check_daily_reset(self):
        """Check if we need to reset daily counters (new trading day)"""
        current_date = datetime.now().date()

        if self.last_reset_date is None or current_date > self.last_reset_date:
            self.reset_daily_counters()

    def reset_daily_counters(self):
        """Reset counters at start of new trading day"""
        account_info = connector.get_account_info()
        if account_info:
            self.daily_start_balance = account_info['balance']

        self.daily_profit = 0.0
        self.daily_loss = 0.0
        self.trades_today = 0
        self.trading_halted = False
        self.halt_reason = ""
        self.last_reset_date = datetime.now().date()

        logger.info(f"📅 Daily reset: New balance ${self.daily_start_balance:.2f}")

    def update_daily_pnl(self):
        """Update daily P/L tracking"""
        account_info = connector.get_account_info()
        if not account_info:
            return

        current_balance = account_info['balance']
        daily_pnl = current_balance - self.daily_start_balance

        if daily_pnl > 0:
            self.daily_profit = daily_pnl
        else:
            self.daily_loss = abs(daily_pnl)

    def check_daily_limits(self) -> Tuple[bool, str]:
        """
        Check if daily loss or profit limits have been reached

        Returns:
            (can_trade, reason)
        """
        print("[DEBUG] RiskManager.check_daily_limits() called")
        self.update_daily_pnl()
        print(f"[DEBUG] Daily P/L: profit=${self.daily_profit:.2f}, loss=${self.daily_loss:.2f}")

        # Check daily loss limit
        if self.daily_loss >= config.risk.daily_stop_usd:
            self.trading_halted = True
            self.halt_reason = f"Daily loss limit reached: ${self.daily_loss:.2f} >= ${config.risk.daily_stop_usd:.2f}"
            logger.warning(f"[!] TRADING HALTED: {self.halt_reason}")
            print(f"[DEBUG] DAILY LOSS LIMIT HIT: {self.halt_reason}")
            return False, self.halt_reason

        # Check daily profit target
        if self.daily_profit >= config.risk.daily_target_usd:
            self.trading_halted = True
            self.halt_reason = f"Daily profit target reached: ${self.daily_profit:.2f} >= ${config.risk.daily_target_usd:.2f}"
            logger.info(f"[OK] TRADING HALTED: {self.halt_reason}")
            print(f"[DEBUG] DAILY PROFIT TARGET HIT: {self.halt_reason}")
            return False, self.halt_reason

        if self.trading_halted:
            print(f"[DEBUG] Trading halted: {self.halt_reason}")
            return False, self.halt_reason

        print("[DEBUG] Daily limits OK - can trade")
        return True, "OK"

    def calculate_position_size(self, symbol: str, account_balance: float) -> float:
        """
        Calculate position size based on risk parameters

        Args:
            symbol: Trading symbol
            account_balance: Current account balance

        Returns:
            Lot size
        """
        # For now, use fixed lot size from config
        # Can be enhanced with dynamic sizing based on account % risk
        lot_size = config.risk.lot_size

        # Ensure within min/max limits
        lot_size = max(config.risk.min_lot, min(lot_size, config.risk.max_lot))

        # Round to symbol's volume step
        symbol_info = connector.symbols_info.get(symbol)
        if symbol_info:
            volume_step = symbol_info['volume_step']
            lot_size = round(lot_size / volume_step) * volume_step

        return lot_size

    def validate_trade(self, symbol: str, action: str, volume: float) -> Tuple[bool, str]:
        """
        Validate if trade can be executed based on risk rules

        Args:
            symbol: Trading symbol
            action: 'BUY' or 'SELL'
            volume: Requested lot size

        Returns:
            (can_trade, reason)
        """
        # Check daily limits
        can_trade, reason = self.check_daily_limits()
        if not can_trade:
            return False, reason

        # Check trading session
        if not self.is_trading_session():
            return False, "Outside trading session hours"

        # Validate volume
        symbol_info = connector.symbols_info.get(symbol)
        if symbol_info:
            if volume < symbol_info['volume_min']:
                return False, f"Volume below minimum: {volume} < {symbol_info['volume_min']}"
            if volume > symbol_info['volume_max']:
                return False, f"Volume above maximum: {volume} > {symbol_info['volume_max']}"

        # Check spread
        tick = connector.get_tick(symbol)
        if tick:
            spread = tick['spread']
            max_spread = config.risk.max_spread_pips * symbol_info.get('point', 0.00001)
            if spread > max_spread:
                return False, f"Spread too high: {spread:.5f} > {max_spread:.5f}"

        return True, "OK"

    def is_trading_session(self) -> bool:
        """
        Check if current time is within allowed trading session

        Returns:
            True if within session hours
        """
        now = datetime.now().time()
        session_start = config.session.session_start
        session_end = config.session.session_end

        # Handle overnight sessions (e.g., 19:00 to 06:00)
        if session_start > session_end:
            # Session crosses midnight
            in_session = now >= session_start or now <= session_end
        else:
            in_session = session_start <= now <= session_end

        print(f"[DEBUG] is_trading_session(): now={now}, session={session_start}-{session_end}, in_session={in_session}")
        return in_session

    def get_daily_stats(self) -> Dict:
        """Get current daily statistics"""
        self.update_daily_pnl()

        account_info = connector.get_account_info()
        current_balance = account_info.get('balance', 0) if account_info else 0

        return {
            'start_balance': self.daily_start_balance,
            'current_balance': current_balance,
            'daily_pnl': current_balance - self.daily_start_balance,
            'daily_profit': self.daily_profit,
            'daily_loss': self.daily_loss,
            'trades_today': self.trades_today,
            'daily_stop_limit': config.risk.daily_stop_usd,
            'daily_target': config.risk.daily_target_usd,
            'trading_halted': self.trading_halted,
            'halt_reason': self.halt_reason,
            'in_session': self.is_trading_session()
        }

    def record_trade(self, profit: float):
        """Record completed trade for statistics"""
        self.trades_today += 1
        logger.debug(f"Trade recorded: Profit ${profit:.2f}, Total today: {self.trades_today}")

    def get_risk_status(self) -> Dict:
        """Get comprehensive risk status"""
        stats = self.get_daily_stats()

        # Calculate risk metrics
        if self.daily_start_balance > 0:
            daily_return_pct = (stats['daily_pnl'] / self.daily_start_balance) * 100
        else:
            daily_return_pct = 0.0

        loss_remaining = config.risk.daily_stop_usd - self.daily_loss
        profit_remaining = config.risk.daily_target_usd - self.daily_profit

        return {
            **stats,
            'daily_return_pct': daily_return_pct,
            'loss_remaining': max(0, loss_remaining),
            'profit_remaining': max(0, profit_remaining),
            'risk_utilization_pct': (self.daily_loss / config.risk.daily_stop_usd) * 100 if config.risk.daily_stop_usd > 0 else 0
        }


# Global risk manager instance
risk_manager = RiskManager()
