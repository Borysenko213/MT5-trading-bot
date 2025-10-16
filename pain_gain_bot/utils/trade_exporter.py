"""
Trade history exporter - Exports bot trades to CSV files
Similar to backtest output format
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from ..utils.logger import logger


class TradeExporter:
    """
    Exports trading history to CSV and JSON files
    """

    def __init__(self, output_dir: str = "trade_history"):
        """
        Initialize trade exporter

        Args:
            output_dir: Directory to save export files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.trades = []
        print(f"[DEBUG] TradeExporter initialized: output_dir={self.output_dir}")

    def record_trade_open(self, trade_data: Dict):
        """
        Record a trade opening

        Args:
            trade_data: Dictionary with trade details
                - ticket: Order ticket number
                - symbol: Trading symbol
                - action: BUY or SELL
                - volume: Lot size
                - entry_price: Entry price
                - entry_time: Entry timestamp
                - sl: Stop loss
                - tp: Take profit
                - bot_type: PAIN or GAIN
        """
        print(f"[DEBUG] TradeExporter.record_trade_open() called: Ticket {trade_data.get('ticket')}")

        trade_record = {
            'ticket': trade_data.get('ticket'),
            'symbol': trade_data.get('symbol'),
            'action': trade_data.get('action'),
            'volume': trade_data.get('volume'),
            'entry_price': trade_data.get('entry_price'),
            'entry_time': trade_data.get('entry_time', datetime.now()).isoformat(),
            'sl': trade_data.get('sl', 0.0),
            'tp': trade_data.get('tp', 0.0),
            'bot_type': trade_data.get('bot_type', 'UNKNOWN'),
            'status': 'OPEN',
            'exit_price': None,
            'exit_time': None,
            'exit_reason': None,
            'pnl': None,
            'balance_after': None
        }

        self.trades.append(trade_record)
        logger.info(f"[EXPORT] Trade recorded: {trade_record['action']} {trade_record['symbol']} @ {trade_record['entry_price']}")
        print(f"[DEBUG] Trade record added to exporter, total trades: {len(self.trades)}")

    def record_trade_close(self, ticket: int, close_data: Dict):
        """
        Record a trade closing

        Args:
            ticket: Order ticket number
            close_data: Dictionary with close details
                - exit_price: Exit price
                - exit_time: Exit timestamp
                - exit_reason: Why it closed
                - pnl: Profit/Loss
                - balance_after: Account balance after close
        """
        print(f"[DEBUG] TradeExporter.record_trade_close() called: Ticket {ticket}")

        # Find the trade record
        trade = None
        for t in self.trades:
            if t['ticket'] == ticket and t['status'] == 'OPEN':
                trade = t
                break

        if trade is None:
            print(f"[DEBUG] WARNING: Trade {ticket} not found in exporter records")
            logger.warning(f"[EXPORT] Trade {ticket} not found for closing")
            return

        # Update with close data
        trade['status'] = 'CLOSED'
        trade['exit_price'] = close_data.get('exit_price')
        trade['exit_time'] = close_data.get('exit_time', datetime.now()).isoformat()
        trade['exit_reason'] = close_data.get('exit_reason', 'Unknown')
        trade['pnl'] = close_data.get('pnl', 0.0)
        trade['balance_after'] = close_data.get('balance_after')

        logger.info(f"[EXPORT] Trade closed: Ticket {ticket} | P/L: ${trade['pnl']:.2f}")
        print(f"[DEBUG] Trade {ticket} updated with close data")

        # Auto-export after each trade closes
        self.export_to_csv()

    def export_to_csv(self, filename: str = None):
        """
        Export all trades to CSV file

        Args:
            filename: Custom filename (optional, auto-generated if not provided)
        """
        if not self.trades:
            print("[DEBUG] No trades to export")
            return

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"trade_history_{timestamp}.csv"

        filepath = self.output_dir / filename

        print(f"[DEBUG] Exporting {len(self.trades)} trades to {filepath}")

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                # Define CSV columns (same as backtest format)
                fieldnames = [
                    'ticket',
                    'symbol',
                    'bot_type',
                    'action',
                    'volume',
                    'entry_price',
                    'entry_time',
                    'exit_price',
                    'exit_time',
                    'exit_reason',
                    'sl',
                    'tp',
                    'pnl',
                    'balance_after',
                    'status'
                ]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.trades)

            logger.info(f"[EXPORT] Trade history exported: {filepath}")
            print(f"[DEBUG] Export successful: {filepath}")

            # Also print summary
            closed_trades = [t for t in self.trades if t['status'] == 'CLOSED']
            if closed_trades:
                total_pnl = sum(t['pnl'] for t in closed_trades if t['pnl'] is not None)
                winning = [t for t in closed_trades if t.get('pnl', 0) > 0]
                win_rate = (len(winning) / len(closed_trades)) * 100 if closed_trades else 0

                print(f"\n[EXPORT] === Trade Summary ===")
                print(f"[EXPORT] Total trades: {len(closed_trades)}")
                print(f"[EXPORT] Winning trades: {len(winning)} ({win_rate:.1f}%)")
                print(f"[EXPORT] Total P/L: ${total_pnl:.2f}")
                print(f"[EXPORT] CSV saved: {filepath}")
                print(f"[EXPORT] ========================\n")

        except Exception as e:
            logger.error(f"[EXPORT] Failed to export CSV: {e}")
            print(f"[DEBUG] Export failed: {type(e).__name__}: {e}")

    def export_to_json(self, filename: str = None):
        """
        Export all trades to JSON file

        Args:
            filename: Custom filename (optional)
        """
        if not self.trades:
            print("[DEBUG] No trades to export to JSON")
            return

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"trade_history_{timestamp}.json"

        filepath = self.output_dir / filename

        print(f"[DEBUG] Exporting {len(self.trades)} trades to JSON: {filepath}")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.trades, f, indent=2, default=str)

            logger.info(f"[EXPORT] Trade history exported to JSON: {filepath}")
            print(f"[DEBUG] JSON export successful: {filepath}")

        except Exception as e:
            logger.error(f"[EXPORT] Failed to export JSON: {e}")
            print(f"[DEBUG] JSON export failed: {type(e).__name__}: {e}")

    def get_statistics(self) -> Dict:
        """
        Calculate trading statistics

        Returns:
            Dictionary with statistics
        """
        closed_trades = [t for t in self.trades if t['status'] == 'CLOSED']

        if not closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0
            }

        winning = [t for t in closed_trades if t.get('pnl', 0) > 0]
        losing = [t for t in closed_trades if t.get('pnl', 0) <= 0]
        total_pnl = sum(t.get('pnl', 0) for t in closed_trades)

        return {
            'total_trades': len(closed_trades),
            'open_trades': len([t for t in self.trades if t['status'] == 'OPEN']),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(closed_trades)) * 100,
            'total_pnl': total_pnl,
            'avg_win': sum(t['pnl'] for t in winning) / len(winning) if winning else 0,
            'avg_loss': sum(t['pnl'] for t in losing) / len(losing) if losing else 0,
            'best_trade': max((t.get('pnl', 0) for t in closed_trades), default=0),
            'worst_trade': min((t.get('pnl', 0) for t in closed_trades), default=0)
        }

    def print_summary(self):
        """
        Print trading summary to console
        """
        stats = self.get_statistics()

        print("\n" + "="*60)
        print(" TRADING SESSION SUMMARY")
        print("="*60)
        print(f"Total Trades (Closed): {stats['total_trades']}")
        print(f"Open Trades: {stats['open_trades']}")
        print(f"Winning Trades: {stats['winning_trades']} ({stats['win_rate']:.1f}%)")
        print(f"Losing Trades: {stats['losing_trades']}")
        print(f"Total P/L: ${stats['total_pnl']:.2f}")
        print(f"Average Win: ${stats['avg_win']:.2f}")
        print(f"Average Loss: ${stats['avg_loss']:.2f}")
        print(f"Best Trade: ${stats['best_trade']:.2f}")
        print(f"Worst Trade: ${stats['worst_trade']:.2f}")
        print("="*60 + "\n")

        logger.info("[EXPORT] Trading session summary printed")


# Global trade exporter instance
trade_exporter = TradeExporter()
