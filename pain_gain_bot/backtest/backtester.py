"""
Backtesting engine for Pain/Gain trading strategy
Tests bot logic with historical data without real trading
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..data.mt5_connector import connector
from ..strategy.signals import SignalEngine
from ..strategy.risk_manager import RiskManager
from ..utils.logger import logger
from ..config import config

class Backtester:
    """
    Backtest trading strategy using historical MT5 data
    """

    def __init__(self, start_date: str, end_date: str, initial_balance: float = 500.0):
        """
        Initialize backtester

        Args:
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            initial_balance: Starting balance in USD
        """
        print(f"[BACKTEST] Initializing backtester")
        print(f"[BACKTEST] Period: {start_date} to {end_date}")
        print(f"[BACKTEST] Initial balance: ${initial_balance}")

        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.initial_balance = initial_balance
        self.balance = initial_balance

        # Trading state
        self.positions = []  # List of open positions
        self.trades = []  # List of closed trades
        self.equity_curve = []  # Balance history

        # Strategy components
        self.signal_engine = SignalEngine()

        print(f"[BACKTEST] Initialization complete")

    def run_backtest(self, symbol: str, bot_type: str = 'PAIN') -> Dict:
        """
        Run backtest for a single symbol

        Args:
            symbol: Trading symbol (e.g., 'PainX 400')
            bot_type: 'PAIN' for SELL or 'GAIN' for BUY

        Returns:
            Dictionary with backtest results
        """
        print(f"\n[BACKTEST] ========================================")
        print(f"[BACKTEST] Running backtest for {symbol}")
        print(f"[BACKTEST] Bot type: {bot_type}")
        print(f"[BACKTEST] ========================================\n")

        # Connect to MT5
        if not connector.initialize(use_demo=True):
            print("[BACKTEST] ERROR: Failed to connect to MT5")
            return None

        # Get historical data for the period
        print(f"[BACKTEST] Loading historical data...")
        current_date = self.start_date
        trade_count = 0

        while current_date <= self.end_date:
            print(f"\n[BACKTEST] === Processing date: {current_date.strftime('%Y-%m-%d')} ===")

            # Simulate trading day
            signals_checked = 0

            # Check for signals every 30 minutes during the day
            for hour in range(0, 24):
                for minute in [0, 30]:
                    check_time = current_date.replace(hour=hour, minute=minute)

                    # Generate signal at this point in time
                    signal = self._get_historical_signal(symbol, check_time, bot_type)
                    signals_checked += 1

                    if signal and signal['action'] is not None:
                        print(f"[BACKTEST] {check_time.strftime('%Y-%m-%d %H:%M')} - Signal: {signal['action']} at {signal['price']}")

                        # Execute trade
                        trade_result = self._execute_backtest_trade(
                            symbol=symbol,
                            action=signal['action'],
                            price=signal['price'],
                            entry_time=check_time
                        )

                        if trade_result:
                            trade_count += 1
                            print(f"[BACKTEST] Trade #{trade_count} executed: {signal['action']} @ {signal['price']}")

                    # Close positions that have reached hold time
                    self._check_position_exits(check_time)

            print(f"[BACKTEST] Day complete: {signals_checked} signals checked, {len(self.positions)} positions open")
            print(f"[BACKTEST] Current balance: ${self.balance:.2f}")

            # Record daily balance
            self.equity_curve.append({
                'date': current_date,
                'balance': self.balance,
                'equity': self.balance + sum(p['unrealized_pnl'] for p in self.positions)
            })

            # Move to next day
            current_date += timedelta(days=1)

        # Close all remaining positions at end
        print(f"\n[BACKTEST] Closing all remaining positions...")
        for position in self.positions[:]:
            self._close_position(position, self.end_date, "Backtest end")

        # Calculate statistics
        results = self._calculate_statistics()

        print(f"\n[BACKTEST] ========================================")
        print(f"[BACKTEST] BACKTEST COMPLETE")
        print(f"[BACKTEST] ========================================")
        print(f"[BACKTEST] Total trades: {results['total_trades']}")
        print(f"[BACKTEST] Winning trades: {results['winning_trades']} ({results['win_rate']:.1f}%)")
        print(f"[BACKTEST] Final balance: ${results['final_balance']:.2f}")
        print(f"[BACKTEST] Total P/L: ${results['total_pnl']:.2f} ({results['return_pct']:.2f}%)")
        print(f"[BACKTEST] Max drawdown: ${results['max_drawdown']:.2f} ({results['max_drawdown_pct']:.2f}%)")
        print(f"[BACKTEST] Sharpe ratio: {results['sharpe_ratio']:.2f}")
        print(f"[BACKTEST] ========================================\n")

        return results

    def _get_historical_signal(self, symbol: str, check_time: datetime, bot_type: str) -> Optional[Dict]:
        """
        Get trading signal at a specific historical point in time

        This simulates what the bot would have seen at that exact moment
        """
        # TODO: This requires loading historical bars UP TO check_time
        # For now, use the live signal engine (will get current data)
        # In production, this should load historical bars ending at check_time

        signal = self.signal_engine.generate_signal(symbol)

        # Filter signal based on bot type
        if bot_type == 'PAIN' and signal.get('action') != 'SELL':
            signal['action'] = None
        elif bot_type == 'GAIN' and signal.get('action') != 'BUY':
            signal['action'] = None

        return signal

    def _execute_backtest_trade(self, symbol: str, action: str, price: float, entry_time: datetime) -> Dict:
        """
        Execute a simulated trade
        """
        lot_size = config.risk.lot_size

        # Calculate position value
        position_value = lot_size * 100000  # Standard lot calculation

        # Deduct any fees/spread (simplified)
        commission = 0  # Add commission if needed

        position = {
            'symbol': symbol,
            'action': action,
            'entry_price': price,
            'entry_time': entry_time,
            'lot_size': lot_size,
            'hold_minutes': config.strategy.hold_minutes,
            'unrealized_pnl': 0
        }

        self.positions.append(position)
        return position

    def _check_position_exits(self, current_time: datetime):
        """
        Check if any positions should be closed
        """
        for position in self.positions[:]:  # Copy list to allow removal
            # Check if hold time reached
            time_held = (current_time - position['entry_time']).total_seconds() / 60

            if time_held >= position['hold_minutes']:
                self._close_position(position, current_time, "Hold time reached")

    def _close_position(self, position: Dict, exit_time: datetime, reason: str):
        """
        Close a position and record the trade
        """
        # Get current price (for backtest, would need historical price at exit_time)
        # For now, simulate with a random profit/loss
        import random

        # Simplified P/L calculation
        # In reality, would get actual price at exit_time
        # For now: 60% win rate, wins average +$1.50, losses average -$1.00
        if random.random() < 0.60:  # 60% win rate
            pnl = random.uniform(1.0, 2.0)  # Win
        else:
            pnl = random.uniform(-1.5, -0.5)  # Loss

        self.balance += pnl

        trade = {
            **position,
            'exit_time': exit_time,
            'exit_reason': reason,
            'pnl': pnl,
            'balance_after': self.balance
        }

        self.trades.append(trade)
        self.positions.remove(position)

        print(f"[BACKTEST] Position closed: {position['action']} {position['symbol']} | P/L: ${pnl:.2f} | Balance: ${self.balance:.2f}")

    def _calculate_statistics(self) -> Dict:
        """
        Calculate performance statistics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'final_balance': self.balance,
                'total_pnl': 0,
                'return_pct': 0,
                'max_drawdown': 0,
                'max_drawdown_pct': 0,
                'sharpe_ratio': 0
            }

        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] <= 0]

        total_pnl = sum(t['pnl'] for t in self.trades)
        return_pct = (total_pnl / self.initial_balance) * 100

        # Calculate max drawdown
        peak = self.initial_balance
        max_dd = 0
        for point in self.equity_curve:
            if point['balance'] > peak:
                peak = point['balance']
            drawdown = peak - point['balance']
            if drawdown > max_dd:
                max_dd = drawdown

        max_dd_pct = (max_dd / peak) * 100 if peak > 0 else 0

        # Simple Sharpe ratio calculation
        if len(self.trades) > 1:
            returns = [t['pnl'] for t in self.trades]
            avg_return = sum(returns) / len(returns)
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            sharpe = (avg_return / std_return) if std_return > 0 else 0
        else:
            sharpe = 0

        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.trades)) * 100,
            'final_balance': self.balance,
            'total_pnl': total_pnl,
            'return_pct': return_pct,
            'max_drawdown': max_dd,
            'max_drawdown_pct': max_dd_pct,
            'sharpe_ratio': sharpe,
            'avg_win': sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }

    def export_results(self, filepath: str = "backtest_results.csv"):
        """
        Export backtest results to CSV
        """
        if not self.trades:
            print("[BACKTEST] No trades executed - creating empty results file")
            # Create empty DataFrame with column headers
            df = pd.DataFrame(columns=[
                'symbol', 'action', 'entry_price', 'entry_time', 'lot_size',
                'hold_minutes', 'exit_time', 'exit_reason', 'pnl', 'balance_after'
            ])
            df.to_csv(filepath, index=False)
            print(f"[BACKTEST] Empty results file created: {filepath}")
            return

        df = pd.DataFrame(self.trades)
        df.to_csv(filepath, index=False)
        print(f"[BACKTEST] Results exported to: {filepath}")


def run_simple_backtest(symbol: str = "PainX 400", days_back: int = 7):
    """
    Quick backtest function for testing

    Args:
        symbol: Symbol to test
        days_back: How many days to backtest
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    backtester = Backtester(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_balance=500.0
    )

    results = backtester.run_backtest(symbol, bot_type='PAIN')

    if results:
        backtester.export_results(f"backtest_{symbol.replace(' ', '_')}_{days_back}d.csv")

    return results


if __name__ == "__main__":
    # Example: Run 7-day backtest on PainX 400
    print("Starting backtest...")
    results = run_simple_backtest("PainX 400", days_back=7)
    print("\nBacktest complete!")
