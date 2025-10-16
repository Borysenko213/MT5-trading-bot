"""
MetaTrader 5 connection and data management module
Handles MT5 initialization, symbol data, and market information
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from ..utils.logger import logger
from ..config import config

class MT5Connector:
    """Manages connection and data retrieval from MetaTrader 5"""

    def __init__(self):
        self.connected = False
        self.account_info = None
        self.symbols_info = {}

    def initialize(self, use_demo: bool = True) -> bool:
        """Initialize MT5 connection"""
        try:
            print("[DEBUG] MT5Connector.initialize() started")
            print("[DEBUG] Calling mt5.initialize()...")
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"MT5 initialization failed: {error}")
                print(f"[DEBUG] mt5.initialize() FAILED with error: {error}")
                return False

            print("[DEBUG] mt5.initialize() succeeded")
            # Login to account
            account = config.broker.demo_account if use_demo else config.broker.live_account
            password = config.broker.demo_password if use_demo else config.broker.live_password
            server = config.broker.server

            print(f"[DEBUG] Attempting login: account={account}, server={server}, use_demo={use_demo}")
            if not mt5.login(account, password=password, server=server):
                error = mt5.last_error()
                logger.error(f"MT5 login failed: {error}")
                print(f"[DEBUG] mt5.login() FAILED with error: {error}")
                mt5.shutdown()
                return False

            print("[DEBUG] mt5.login() succeeded")

            self.connected = True
            self.account_info = mt5.account_info()._asdict()

            logger.info(f"[OK] Connected to MT5 - Account: {account} ({('Demo' if use_demo else 'Live')})")
            logger.info(f"  Server: {server}")
            logger.info(f"  Balance: ${self.account_info['balance']:.2f}")
            logger.info(f"  Leverage: 1:{self.account_info['leverage']}")

            return True

        except Exception as e:
            logger.error(f"MT5 initialization error", e)
            return False

    def shutdown(self):
        """Close MT5 connection"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("MT5 connection closed")

    def verify_symbols(self, symbols: List[str]) -> Dict[str, bool]:
        """Verify that symbols are available and visible"""
        results = {}

        for symbol in symbols:
            symbol_info = mt5.symbol_info(symbol)

            if symbol_info is None:
                logger.warning(f"Symbol {symbol} not found")
                results[symbol] = False
                continue

            if not symbol_info.visible:
                logger.info(f"Enabling visibility for {symbol}")
                if not mt5.symbol_select(symbol, True):
                    logger.error(f"Failed to enable {symbol}")
                    results[symbol] = False
                    continue

            # Store symbol info
            self.symbols_info[symbol] = {
                'point': symbol_info.point,
                'digits': symbol_info.digits,
                'spread': symbol_info.spread,
                'trade_contract_size': symbol_info.trade_contract_size,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'volume_step': symbol_info.volume_step,
            }

            results[symbol] = True
            logger.info(f"[OK] {symbol} - Spread: {symbol_info.spread} points | "
                       f"Contract: {symbol_info.trade_contract_size}")

        return results

    def get_bars(self, symbol: str, timeframe: str, count: int = 500) -> Optional[pd.DataFrame]:
        """
        Retrieve historical bars for a symbol

        Args:
            symbol: Symbol name
            timeframe: MT5 timeframe (M1, M5, M15, M30, H1, H4, D1)
            count: Number of bars to retrieve

        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Map timeframe string to MT5 constant
            tf_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1,
            }

            if timeframe not in tf_map:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None

            rates = mt5.copy_rates_from_pos(symbol, tf_map[timeframe], 0, count)

            if rates is None or len(rates) == 0:
                logger.error(f"No data for {symbol} {timeframe}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)

            return df

        except Exception as e:
            logger.error(f"Error retrieving bars for {symbol} {timeframe}", e)
            return None

    def get_tick(self, symbol: str) -> Optional[Dict]:
        """Get latest tick for a symbol"""
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None

            return {
                'time': datetime.fromtimestamp(tick.time),
                'bid': tick.bid,
                'ask': tick.ask,
                'last': tick.last,
                'volume': tick.volume,
                'spread': tick.ask - tick.bid
            }

        except Exception as e:
            logger.error(f"Error getting tick for {symbol}", e)
            return None

    def get_account_info(self) -> Dict:
        """Get current account information"""
        try:
            info = mt5.account_info()
            if info is None:
                return {}

            return {
                'balance': info.balance,
                'equity': info.equity,
                'profit': info.profit,
                'margin': info.margin,
                'margin_free': info.margin_free,
                'margin_level': info.margin_level if info.margin > 0 else 0,
            }

        except Exception as e:
            logger.error("Error getting account info", e)
            return {}

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open positions, optionally filtered by symbol"""
        try:
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()

            if positions is None:
                return []

            return [
                {
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'time': datetime.fromtimestamp(pos.time),
                    'magic': pos.magic,
                }
                for pos in positions
            ]

        except Exception as e:
            logger.error("Error getting positions", e)
            return []

    def send_order(self, symbol: str, order_type: str, volume: float,
                   sl: float = 0.0, tp: float = 0.0, magic: int = 0,
                   comment: str = "") -> Optional[Dict]:
        """
        Send market order

        Args:
            symbol: Symbol name
            order_type: 'BUY' or 'SELL'
            volume: Lot size
            sl: Stop loss price
            tp: Take profit price
            magic: Magic number for identification
            comment: Order comment

        Returns:
            Order result dictionary or None
        """
        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found")
                return None

            # Check spread
            current_spread = symbol_info.spread * symbol_info.point
            max_spread = config.risk.max_spread_pips * symbol_info.point
            if current_spread > max_spread:
                logger.warning(f"Spread too high: {current_spread:.5f} > {max_spread:.5f}")
                return None

            # Determine price and order type
            if order_type.upper() == 'BUY':
                price = mt5.symbol_info_tick(symbol).ask
                mt5_order_type = mt5.ORDER_TYPE_BUY
            else:
                price = mt5.symbol_info_tick(symbol).bid
                mt5_order_type = mt5.ORDER_TYPE_SELL

            # Prepare request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5_order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": int(config.risk.max_slippage_pips),
                "magic": magic,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Send order
            result = mt5.order_send(request)

            if result is None:
                logger.error("Order send failed - no result")
                return None

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed: {result.comment} (code: {result.retcode})")
                return None

            logger.trade(
                action=order_type,
                symbol=symbol,
                details={
                    'ticket': result.order,
                    'volume': volume,
                    'price': result.price,
                    'sl': sl,
                    'tp': tp,
                    'comment': comment
                }
            )

            return {
                'ticket': result.order,
                'volume': result.volume,
                'price': result.price,
                'retcode': result.retcode,
                'comment': result.comment
            }

        except Exception as e:
            logger.error(f"Error sending {order_type} order for {symbol}", e)
            return None

    def close_position(self, ticket: int) -> bool:
        """Close position by ticket"""
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                logger.error(f"Position {ticket} not found")
                return False

            position = position[0]

            # Prepare close request (opposite order)
            close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(position.symbol).bid if close_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(position.symbol).ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": close_type,
                "position": ticket,
                "price": price,
                "deviation": int(config.risk.max_slippage_pips),
                "magic": position.magic,
                "comment": "Close by bot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Close failed: {result.comment}")
                return False

            logger.trade(
                action="CLOSE",
                symbol=position.symbol,
                details={
                    'ticket': ticket,
                    'profit': position.profit
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error closing position {ticket}", e)
            return False

    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> bool:
        """Modify position SL/TP"""
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return False

            position = position[0]

            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "sl": sl if sl is not None else position.sl,
                "tp": tp if tp is not None else position.tp,
                "position": ticket,
            }

            result = mt5.order_send(request)
            return result.retcode == mt5.TRADE_RETCODE_DONE

        except Exception as e:
            logger.error(f"Error modifying position {ticket}", e)
            return False


# Global connector instance
connector = MT5Connector()
