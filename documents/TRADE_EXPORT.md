# Trade Export Feature

The bot automatically exports all trading activity to CSV and JSON files, just like the backtest feature.

---

## 📁 Where Files Are Saved

All trade history files are saved in:
```
trading/
└── trade_history/
    ├── trade_history_20251016_153045.csv
    ├── trade_history_20251016_153045.json
    ├── trade_history_20251016_183020.csv
    └── ...
```

---

## 🤖 Automatic Export

The bot automatically:
1. ✅ **Records every trade** when it opens
2. ✅ **Updates with P/L** when it closes
3. ✅ **Exports to CSV** after each trade closes
4. ✅ **Creates final export** when you stop the bot (Ctrl+C)

**You don't need to do anything** - it happens automatically!

---

## 📊 CSV File Format

The CSV file contains the same columns as backtest results:

| Column | Description |
|--------|-------------|
| `ticket` | MT5 order ticket number |
| `symbol` | Trading symbol (e.g., "PainX 400") |
| `bot_type` | PAIN or GAIN |
| `action` | BUY or SELL |
| `volume` | Lot size |
| `entry_price` | Entry price |
| `entry_time` | When trade opened (ISO format) |
| `exit_price` | Exit price |
| `exit_time` | When trade closed |
| `exit_reason` | Why it closed (Hold time, Stop Loss, etc.) |
| `sl` | Stop loss price |
| `tp` | Take profit price |
| `pnl` | Profit/Loss for this trade |
| `balance_after` | Account balance after closing |
| `status` | OPEN or CLOSED |

---

## 📈 Example CSV Content

```csv
ticket,symbol,bot_type,action,volume,entry_price,entry_time,exit_price,exit_time,exit_reason,sl,tp,pnl,balance_after,status
123456789,PainX 400,PAIN,SELL,0.01,90332.84,2025-10-16T15:30:45,90350.20,2025-10-16T15:35:45,Hold period complete (Take Profit),0.0,0.0,1.50,501.50,CLOSED
123456790,PainX 600,PAIN,SELL,0.01,104518.34,2025-10-16T16:15:22,104500.10,2025-10-16T16:20:22,Hold period complete (Take Profit),0.0,0.0,1.82,503.32,CLOSED
123456791,GainX 400,GAIN,BUY,0.01,104148.14,2025-10-16T17:05:10,104165.50,2025-10-16T17:10:10,Purple line break (Stop Loss),0.0,0.0,-0.85,502.47,CLOSED
```

---

## 📝 What You'll See When Bot Stops

When you press `Ctrl+C` to stop the bot:

```
[DEBUG] Exporting trade history to CSV...

============================================================
 TRADING SESSION SUMMARY
============================================================
Total Trades (Closed): 3
Open Trades: 0
Winning Trades: 2 (66.7%)
Losing Trades: 1
Total P/L: $2.47
Average Win: $1.66
Average Loss: $-0.85
Best Trade: $1.82
Worst Trade: $-0.85
============================================================

[EXPORT] Trade history exported: trade_history/trade_history_20251016_153045.csv
[EXPORT] Trade history exported to JSON: trade_history/trade_history_20251016_153045.json
```

---

## 🔄 Comparing with Backtest Results

Both live trading and backtest use the **same CSV format**, so you can:

✅ Compare backtest results with live results
✅ Import both into Excel side-by-side
✅ Verify the bot is trading as expected
✅ Track performance over time

**Example comparison:**

| File | Trades | Win Rate | Total P/L |
|------|--------|----------|-----------|
| `backtest_PainX_400_7d.csv` | 12 | 66.7% | $12.50 |
| `trade_history_20251016.csv` | 3 | 66.7% | $2.47 |

If win rates are similar, the strategy is performing as backtested!

---

## 📖 Opening CSV Files

### In Excel
1. Double-click the CSV file
2. Excel will open it automatically
3. Create charts, pivot tables, etc.

### In Google Sheets
1. Go to Google Sheets
2. File → Import → Upload
3. Select the CSV file

### In Python
```python
import pandas as pd

# Load trade history
df = pd.read_csv('trade_history/trade_history_20251016_153045.csv')

# Calculate statistics
print(f"Total trades: {len(df)}")
print(f"Total P/L: ${df['pnl'].sum():.2f}")
print(f"Win rate: {(df['pnl'] > 0).sum() / len(df) * 100:.1f}%")

# Find best/worst trades
print(f"Best trade: ${df['pnl'].max():.2f}")
print(f"Worst trade: ${df['pnl'].min():.2f}")
```

---

## 🔍 JSON Format

The JSON file contains the same data in JSON format:

```json
[
  {
    "ticket": 123456789,
    "symbol": "PainX 400",
    "bot_type": "PAIN",
    "action": "SELL",
    "volume": 0.01,
    "entry_price": 90332.84,
    "entry_time": "2025-10-16T15:30:45",
    "exit_price": 90350.20,
    "exit_time": "2025-10-16T15:35:45",
    "exit_reason": "Hold period complete (Take Profit)",
    "sl": 0.0,
    "tp": 0.0,
    "pnl": 1.50,
    "balance_after": 501.50,
    "status": "CLOSED"
  }
]
```

**Use JSON for:**
- Programming/scripting
- Importing into databases
- API integration

---

## 💡 Tips

### Track Daily Performance
Keep each day's export file:
```
trade_history_20251016.csv  → Friday's trades
trade_history_20251017.csv  → Saturday's trades
trade_history_20251020.csv  → Monday's trades
```

### Weekly Analysis
Combine multiple days in Excel:
1. Import all CSVs
2. Create a pivot table by date
3. Track weekly performance trends

### Compare Symbols
Filter by symbol to see which performs best:
- PainX 400 win rate: 70%
- PainX 600 win rate: 65%
- PainX 800 win rate: 60%

### Time Analysis
Check which hours are most profitable:
- 19:00-21:00 (session start)
- 02:00-04:00 (London open)
- etc.

---

## 🎯 Key Benefits

1. **Accountability** - Every trade is recorded
2. **Verification** - Compare with MT5 history
3. **Analysis** - Find patterns and optimize
4. **Reporting** - Share results with others
5. **Backup** - Keep records even if MT5 crashes

---

## ❓ FAQ

**Q: Where do I find the files?**
A: In the `trade_history/` folder in your trading directory.

**Q: Can I delete old files?**
A: Yes, but keep them for record-keeping. They're small files.

**Q: Why are there multiple files?**
A: A new file is created each time you stop and restart the bot.

**Q: Does this slow down the bot?**
A: No, export is very fast and happens in the background.

**Q: Can I customize the format?**
A: Yes, edit `pain_gain_bot/utils/trade_exporter.py`.

**Q: What if I want to merge multiple CSV files?**
A: Use Excel's Power Query or Python pandas to combine them.

---

## 🔗 Related Documentation

- [BACKTESTING.md](BACKTESTING.md) - Compare with backtest results
- [QUICK_START.md](QUICK_START.md) - Getting started guide
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing strategies

---

**Your trading history is now automatically saved and ready for analysis!** 📊
