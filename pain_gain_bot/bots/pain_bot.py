"""
PainBot - Automated SELL trading bot for PainX symbols
Implements the Pain/Gain SELL strategy with multi-timeframe confirmations
"""

import time
from datetime import datetime
from typing import List
from ..data.mt5_connector import connector
from ..strategy.signals import SignalEngine
from ..strategy.order_manager import OrderManager
from ..strategy.risk_manager import risk_manager
from ..utils.logger import logger
from ..config import config

class PainBot:
    """
    PainBot handles SELL logic for PainX symbols
    Trades: PainX400, PainX600, PainX800, PainX999
    """

    def __init__(self):
        print("[DEBUG] PainBot.__init__() started")
        self.name = "PainBot"
        self.bot_type = "PAIN"
        self.magic_number = 100001  # Unique identifier for PainBot orders

        print(f"[DEBUG] Loading pain_symbols from config: {config.symbols.pain_symbols}")
        self.symbols = config.symbols.pain_symbols
        print("[DEBUG] Creating SignalEngine...")
        self.signal_engine = SignalEngine()
        print("[DEBUG] Creating OrderManager...")
        self.order_manager = OrderManager(self.bot_type, self.magic_number)

        self.running = False
        self.iteration = 0
        print("[DEBUG] PainBot.__init__() completed")

    def initialize(self) -> bool:
        """Initialize bot and connect to MT5"""
        print("[DEBUG] PainBot.initialize() started")
        logger.info(f"=== Initializing {self.name} ===")

        # Connect to MT5
        print(f"[DEBUG] Calling connector.initialize() with use_demo={config.broker.use_demo}")
        if not connector.initialize(use_demo=config.broker.use_demo):
            logger.error("Failed to connect to MT5")
            print("[DEBUG] connector.initialize() returned False")
            return False

        print("[DEBUG] connector.initialize() succeeded")
        # Verify symbols
        logger.info(f"Verifying symbols: {self.symbols}")
        print(f"[DEBUG] Calling connector.verify_symbols({self.symbols})")
        verification = connector.verify_symbols(self.symbols)

        valid_symbols = [s for s, v in verification.items() if v]
        if not valid_symbols:
            logger.error("No valid symbols found")
            return False

        self.symbols = valid_symbols
        logger.info(f"[OK] Active symbols: {self.symbols}")

        # Initialize risk manager
        risk_manager.initialize()

        logger.info(f"[OK] {self.name} initialized successfully")
        return True

    def run(self):
        """Main trading loop"""
        print("[DEBUG] PainBot.run() started")
        logger.info(f"🚀 {self.name} starting...")
        logger.info(f"Strategy: SELL signals on {len(self.symbols)} symbols")
        logger.info(f"Session: {config.session.session_start} - {config.session.session_end}")

        self.running = True
        print("[DEBUG] Entering main loop...")

        try:
            while self.running:
                self.iteration += 1
                print(f"[DEBUG] === Iteration {self.iteration} ===")

                # Check daily reset
                print("[DEBUG] Checking daily reset")
                risk_manager.check_daily_reset()

                # Check if we can trade
                print("[DEBUG] Checking daily limits")
                can_trade, reason = risk_manager.check_daily_limits()
                print(f"[DEBUG] Can trade: {can_trade}, reason: {reason}")
                if not can_trade:
                    logger.info(f"⏸ Trading paused: {reason}")
                    print("[DEBUG] Cannot trade - sleeping 60s")
                    time.sleep(60)  # Wait 1 minute before rechecking
                    continue

                # Check trading session
                print("[DEBUG] Checking trading session")
                if not risk_manager.is_trading_session():
                    if self.iteration % 60 == 1:  # Log every 60 iterations
                        logger.info("⏸ Outside trading session")
                        print("[DEBUG] Outside trading session - sleeping 60s")
                    time.sleep(60)
                    continue

                print("[DEBUG] Inside trading session - proceeding")

                # Manage existing positions
                print("[DEBUG] Managing existing positions")
                self.order_manager.manage_positions()

                # Scan symbols for signals
                print(f"[DEBUG] Scanning {len(self.symbols)} symbols: {self.symbols}")
                for symbol in self.symbols:
                    try:
                        print(f"[DEBUG] Processing symbol: {symbol}")
                        self.process_symbol(symbol)
                    except Exception as e:
                        logger.error(f"Error processing {symbol}", e)
                        print(f"[DEBUG] Exception processing {symbol}: {type(e).__name__}: {e}")

                # Log status periodically
                if self.iteration % 20 == 0:
                    print("[DEBUG] Logging status (every 20 iterations)")
                    self.log_status()

                # Sleep between iterations (e.g., check every 30 seconds)
                print("[DEBUG] Sleeping 30 seconds before next iteration...")
                time.sleep(30)

        except KeyboardInterrupt:
            logger.info(f"\n{self.name} stopped by user")
        except Exception as e:
            logger.error(f"{self.name} crashed", e)
        finally:
            self.shutdown()

    def process_symbol(self, symbol: str):
        """Process trading logic for a single symbol"""
        print(f"[DEBUG] process_symbol({symbol}) called")
        # Generate signal
        print(f"[DEBUG] Calling signal_engine.generate_signal({symbol})")
        signal = self.signal_engine.generate_signal(symbol)
        print(f"[DEBUG] Signal result: action={signal.get('action')}, price={signal.get('price')}")

        # Check if we have a SELL signal
        if signal['action'] == 'SELL':
            logger.info(f"[#] SELL signal detected for {symbol}")
            print(f"[DEBUG] SELL signal detected - proceeding with order")

            # Get account info for position sizing
            account_info = connector.get_account_info()
            if not account_info:
                logger.warning(f"Cannot get account info for {symbol}")
                return

            # Calculate position size
            lot_size = risk_manager.calculate_position_size(symbol, account_info['balance'])

            # Validate trade
            can_trade, reason = risk_manager.validate_trade(symbol, 'SELL', lot_size)
            if not can_trade:
                logger.warning(f"Trade validation failed for {symbol}: {reason}")
                return

            # Execute order
            logger.info(f"[*] Executing SELL order for {symbol}: {lot_size} lots")

            result = self.order_manager.execute_order(
                symbol=symbol,
                action='SELL',
                volume=lot_size,
                sl=0.0,  # SL managed by purple line logic
                tp=0.0   # TP managed by hold time logic
            )

            if result:
                logger.info(f"[OK] SELL order placed successfully: Ticket {result['ticket']}")
                risk_manager.record_trade(0)  # Will update with actual profit on close
            else:
                logger.error(f"[X] SELL order failed for {symbol}")

    def log_status(self):
        """Log current bot status"""
        risk_status = risk_manager.get_risk_status()
        order_status = self.order_manager.get_status()

        logger.info(
            f"\n{'='*60}\n"
            f"{self.name} Status (Iteration {self.iteration})\n"
            f"{'='*60}\n"
            f"Balance: ${risk_status['current_balance']:.2f} | "
            f"Daily P/L: ${risk_status['daily_pnl']:.2f} ({risk_status['daily_return_pct']:.2f}%)\n"
            f"Trades Today: {risk_status['trades_today']} | "
            f"Active Positions: {order_status['active_positions']}\n"
            f"Daily Loss: ${risk_status['daily_loss']:.2f} / ${risk_status['daily_stop_limit']:.2f} | "
            f"Profit: ${risk_status['daily_profit']:.2f} / ${risk_status['daily_target']:.2f}\n"
            f"In Session: {risk_status['in_session']} | "
            f"Halted: {risk_status['trading_halted']}\n"
            f"{'='*60}"
        )

    def stop(self):
        """Stop the bot"""
        logger.info(f"Stopping {self.name}...")
        self.running = False

    def shutdown(self):
        """Clean shutdown"""
        logger.info(f"Shutting down {self.name}...")

        # Close any remaining positions
        for ticket in list(self.order_manager.active_positions.keys()):
            self.order_manager.close_position(ticket, "Bot shutdown")

        # Disconnect from MT5
        connector.shutdown()

        # Log final statistics
        risk_status = risk_manager.get_risk_status()
        logger.info(
            f"\n{'='*60}\n"
            f"{self.name} Final Statistics\n"
            f"{'='*60}\n"
            f"Final Balance: ${risk_status['current_balance']:.2f}\n"
            f"Total P/L: ${risk_status['daily_pnl']:.2f}\n"
            f"Total Trades: {risk_status['trades_today']}\n"
            f"{'='*60}\n"
        )

        logger.info(f"[OK] {self.name} shutdown complete")


def main():
    """Main entry point for PainBot"""
    bot = PainBot()

    if bot.initialize():
        bot.run()
    else:
        logger.error("Failed to initialize PainBot")


if __name__ == "__main__":
    main()
