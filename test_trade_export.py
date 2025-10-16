"""
Test script to verify trade export functionality
"""

from datetime import datetime
from pain_gain_bot.utils.trade_exporter import trade_exporter

print("Testing trade export functionality...\n")

# Simulate opening a trade
print("1. Simulating trade open...")
trade_exporter.record_trade_open({
    'ticket': 999888777,
    'symbol': 'PainX 400',
    'action': 'SELL',
    'volume': 0.01,
    'entry_price': 90332.84,
    'entry_time': datetime.now(),
    'sl': 0.0,
    'tp': 0.0,
    'bot_type': 'PAIN'
})
print("   [OK] Trade open recorded\n")

# Simulate closing the trade
print("2. Simulating trade close...")
trade_exporter.record_trade_close(999888777, {
    'exit_price': 90350.20,
    'exit_time': datetime.now(),
    'exit_reason': 'Test trade - Hold period complete',
    'pnl': 1.74,
    'balance_after': 501.74
})
print("   [OK] Trade close recorded\n")

# Print summary
print("3. Printing summary...")
trade_exporter.print_summary()

# Check if files were created
import os
trade_history_dir = "trade_history"
if os.path.exists(trade_history_dir):
    files = os.listdir(trade_history_dir)
    print(f"\n4. Files in {trade_history_dir}/:")
    for f in files:
        print(f"   - {f}")
else:
    print(f"\n4. ERROR: {trade_history_dir}/ directory does not exist!")

print("\nTest complete!")
