"""
Order management module for Pain/Gain strategy
Handles order execution, holding periods, and purple line gating
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ..data.mt5_connector import connector
from ..indicators.technical import indicators
from ..utils.logger import logger
from ..utils.trade_exporter import trade_exporter
from ..config import config

class OrderManager:
    """Manages order execution and lifecycle"""

    def __init__(self, bot_type: str, magic_number: int):
        """
        Initialize order manager

        Args:
            bot_type: 'PAIN' or 'GAIN'
            magic_number: Unique identifier for this bot's orders
        """
        self.bot_type = bot_type
        self.magic_number = magic_number
        self.active_positions = {}  # ticket -> position_info
        self.last_entry_time = {}  # symbol -> datetime
        self.consecutive_orders = {}  # symbol -> count

    def can_open_new_order(self, symbol: str) -> Tuple[bool, str]:
        """
        Check if a new order can be opened based on timing and purple line rules

        Returns:
            (can_open, reason)
        """
        # Check if we have an existing position for this symbol
        positions = connector.get_positions(symbol)
        bot_positions = [p for p in positions if p['magic'] == self.magic_number]

        # Check consecutive order limit
        consecutive = self.consecutive_orders.get(symbol, 0)
        if consecutive >= config.risk.max_consecutive_orders:
            return False, f"Max consecutive orders reached ({consecutive})"

        # Check 5-minute hold + wait rule
        if symbol in self.last_entry_time:
            last_entry = self.last_entry_time[symbol]
            minutes_since_last = (datetime.now() - last_entry).total_seconds() / 60

            # Must wait: 5 min hold + 5 min wait + start of 3rd candle = ~10 minutes minimum
            min_wait_minutes = config.strategy.hold_minutes + (config.strategy.wait_candles * 5)

            if minutes_since_last < min_wait_minutes:
                return False, f"Waiting period not complete ({minutes_since_last:.1f}/{min_wait_minutes} min)"

        # Check purple line condition
        purple_line_ok, reason = self.check_purple_line_position(symbol)
        if not purple_line_ok:
            return False, reason

        return True, "OK"

    def check_purple_line_position(self, symbol: str) -> Tuple[bool, str]:
        """
        Verify that price remains on correct side of purple line

        Returns:
            (position_ok, reason)
        """
        try:
            df_m5 = connector.get_bars(symbol, 'M5', count=10)
            if df_m5 is None:
                return False, "Cannot retrieve M5 data"

            purple_line = indicators.calculate_purple_line(df_m5, config.strategy.purple_line_ema)
            current_price = df_m5['close'].iloc[-1]
            purple_val = purple_line.iloc[-1]

            if self.bot_type == 'PAIN':  # SELL bot
                # Price must remain BELOW purple line for sells
                if current_price >= purple_val:
                    return False, "Price above purple line (SELL invalidated)"
            else:  # GAIN (BUY bot)
                # Price must remain ABOVE purple line for buys
                if current_price <= purple_val:
                    return False, "Price below purple line (BUY invalidated)"

            return True, "Purple line position OK"

        except Exception as e:
            logger.error(f"Error checking purple line for {symbol}", e)
            return False, "Purple line check failed"

    def execute_order(self, symbol: str, action: str, volume: float,
                      sl: float = 0.0, tp: float = 0.0) -> Optional[Dict]:
        """
        Execute market order with all validations

        Args:
            symbol: Trading symbol
            action: 'BUY' or 'SELL'
            volume: Lot size
            sl: Stop loss price
            tp: Take profit price

        Returns:
            Order result or None
        """
        print(f"[DEBUG] OrderManager.execute_order() called: {action} {volume} {symbol}")
        try:
            # Final validation
            print(f"[DEBUG] Checking if can open new order for {symbol}")
            can_open, reason = self.can_open_new_order(symbol)
            print(f"[DEBUG] can_open_new_order result: {can_open}, reason: {reason}")
            if not can_open:
                logger.warning(f"Cannot open order for {symbol}: {reason}")
                print(f"[DEBUG] Cannot open order - returning None")
                return None

            # Send order
            comment = f"{self.bot_type}Bot|{datetime.now().strftime('%H%M%S')}"
            print(f"[DEBUG] Sending order to MT5: {action} {volume} {symbol}")

            result = connector.send_order(
                symbol=symbol,
                order_type=action,
                volume=volume,
                sl=sl,
                tp=tp,
                magic=self.magic_number,
                comment=comment
            )
            print(f"[DEBUG] connector.send_order() result: {result}")

            if result:
                # Track order
                entry_time = datetime.now()
                self.last_entry_time[symbol] = entry_time
                self.consecutive_orders[symbol] = self.consecutive_orders.get(symbol, 0) + 1

                self.active_positions[result['ticket']] = {
                    'symbol': symbol,
                    'action': action,
                    'volume': volume,
                    'entry_price': result['price'],
                    'entry_time': entry_time,
                    'sl': sl,
                    'tp': tp,
                    'hold_until': entry_time + timedelta(minutes=config.strategy.hold_minutes)
                }

                logger.info(f"[OK] Order executed: {action} {volume} {symbol} @ {result['price']:.5f} "
                           f"(Ticket: {result['ticket']})")

                # Export trade to CSV
                trade_exporter.record_trade_open({
                    'ticket': result['ticket'],
                    'symbol': symbol,
                    'action': action,
                    'volume': volume,
                    'entry_price': result['price'],
                    'entry_time': entry_time,
                    'sl': sl,
                    'tp': tp,
                    'bot_type': self.bot_type
                })

                return result

            return None

        except Exception as e:
            logger.error(f"Error executing order for {symbol}", e)
            return None

    def check_exit_conditions(self, ticket: int) -> Tuple[bool, str]:
        """
        Check if position should be closed

        Returns:
            (should_close, reason)
        """
        if ticket not in self.active_positions:
            return False, "Position not tracked"

        position = self.active_positions[ticket]
        symbol = position['symbol']
        action = position['action']

        try:
            # Check hold time
            now = datetime.now()
            if now < position['hold_until']:
                return False, "Hold period not complete"

            # After hold period, check purple line break (stop loss condition)
            df_m5 = connector.get_bars(symbol, 'M5', count=10)
            if df_m5 is None:
                return False, "Cannot retrieve M5 data"

            purple_line = indicators.calculate_purple_line(df_m5, config.strategy.purple_line_ema)
            current_price = df_m5['close'].iloc[-1]
            purple_val = purple_line.iloc[-1]

            # Check for purple line break (SL condition)
            if action == 'SELL':
                # For SELL, SL if price breaks ABOVE purple line
                if current_price > purple_val:
                    return True, "Purple line break (Stop Loss)"
            else:  # BUY
                # For BUY, SL if price breaks BELOW purple line
                if current_price < purple_val:
                    return True, "Purple line break (Stop Loss)"

            # Normal close after hold time
            return True, "Hold period complete (Take Profit)"

        except Exception as e:
            logger.error(f"Error checking exit for ticket {ticket}", e)
            return False, "Exit check error"

    def close_position(self, ticket: int, reason: str = "") -> bool:
        """
        Close position by ticket

        Args:
            ticket: Position ticket
            reason: Reason for closing

        Returns:
            True if closed successfully
        """
        try:
            # Get position info before closing
            if ticket in self.active_positions:
                position = self.active_positions[ticket]
            else:
                position = None

            # Get current price and account balance
            if position:
                tick = connector.get_tick(position['symbol'])
                exit_price = tick['bid'] if position['action'] == 'SELL' else tick['ask'] if tick else None
            else:
                exit_price = None

            success = connector.close_position(ticket)

            if success and position:
                logger.info(f"[OK] Position closed: Ticket {ticket} ({reason})")

                # Get updated account balance
                account_info = connector.get_account_info()
                balance_after = account_info.get('balance', 0) if account_info else 0

                # Calculate P/L (simplified - actual P/L from MT5 would be more accurate)
                # Simplified P/L estimate based on price movement
                if exit_price and position['entry_price']:
                    if position['action'] == 'SELL':
                        pnl = (position['entry_price'] - exit_price) * position['volume'] * 100000 * 0.0001
                    else:  # BUY
                        pnl = (exit_price - position['entry_price']) * position['volume'] * 100000 * 0.0001
                else:
                    pnl = 0.0

                # Export trade closure to CSV
                trade_exporter.record_trade_close(ticket, {
                    'exit_price': exit_price,
                    'exit_time': datetime.now(),
                    'exit_reason': reason,
                    'pnl': pnl,
                    'balance_after': balance_after
                })

                # Remove from active positions
                del self.active_positions[ticket]

                # If it was a stop loss, reset consecutive counter
                if "Stop Loss" in reason:
                    symbol = position['symbol']
                    self.consecutive_orders[symbol] = 0
                    logger.info(f"Reset consecutive counter for {symbol} due to SL")

            return success

        except Exception as e:
            logger.error(f"Error closing position {ticket}", e)
            return False

    def manage_positions(self):
        """
        Monitor and manage all active positions
        Call this method periodically
        """
        print(f"[DEBUG] OrderManager.manage_positions() called, active positions: {len(self.active_positions)}")
        tickets_to_close = []

        for ticket in list(self.active_positions.keys()):
            print(f"[DEBUG] Checking exit conditions for ticket {ticket}")
            should_close, reason = self.check_exit_conditions(ticket)
            print(f"[DEBUG] Ticket {ticket}: should_close={should_close}, reason={reason}")

            if should_close:
                tickets_to_close.append((ticket, reason))

        # Close positions
        if tickets_to_close:
            print(f"[DEBUG] Closing {len(tickets_to_close)} positions")
        for ticket, reason in tickets_to_close:
            print(f"[DEBUG] Closing ticket {ticket}, reason: {reason}")
            self.close_position(ticket, reason)

    def reset_daily_counters(self):
        """Reset daily tracking variables"""
        self.consecutive_orders.clear()
        logger.info(f"{self.bot_type}Bot: Daily counters reset")

    def get_status(self) -> Dict:
        """Get current order manager status"""
        return {
            'bot_type': self.bot_type,
            'active_positions': len(self.active_positions),
            'positions': list(self.active_positions.values()),
            'consecutive_orders': dict(self.consecutive_orders)
        }
