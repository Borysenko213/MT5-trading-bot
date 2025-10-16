# Backtesting Guide - Pain/Gain Trading System

Test your trading strategy with historical data without risking real money.

---

## What is Backtesting?

Backtesting allows you to:
- ✅ Test the strategy with **past market data**
- ✅ Verify the bot makes **correct entry decisions**
- ✅ See **performance statistics** without waiting in real-time
- ✅ Optimize parameters before live trading

---

## Quick Start

### Run a 7-Day Backtest

```bash
python run_backtest.py --symbol "PainX 400" --days 7
```

**Output:**
```
========================================
BACKTEST COMPLETE
========================================
Total trades: 12
Winning trades: 8 (66.7%)
Final balance: $512.50
Total P/L: $12.50 (2.50%)
Max drawdown: $3.20 (0.64%)
Sharpe ratio: 1.85
========================================
```

---

## Command Line Options

### Basic Usage

```bash
python run_backtest.py [OPTIONS]
```

### Available Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--symbol` | Trading symbol | "PainX 400" | `--symbol "GainX 600"` |
| `--bot` | Bot type (pain/gain) | pain | `--bot gain` |
| `--days` | Days to backtest | 7 | `--days 30` |
| `--start` | Start date (YYYY-MM-DD) | Auto | `--start 2025-01-01` |
| `--end` | End date (YYYY-MM-DD) | Today | `--end 2025-01-31` |
| `--balance` | Initial balance | 500 | `--balance 1000` |
| `--export` | Export CSV filename | Auto | `--export results.csv` |

---

## Examples

### Example 1: Test PainBot for 30 Days

```bash
python run_backtest.py --symbol "PainX 400" --bot pain --days 30
```

### Example 2: Test GainBot with Specific Dates

```bash
python run_backtest.py --symbol "GainX 800" --bot gain --start 2025-01-01 --end 2025-01-31
```

### Example 3: Test with Higher Balance

```bash
python run_backtest.py --symbol "PainX 999" --days 14 --balance 1000
```

### Example 4: Export to Custom File

```bash
python run_backtest.py --symbol "PainX 400" --days 30 --export my_backtest_results.csv
```

---

## Understanding Results

### Performance Metrics

**Total Trades**
- Number of trades executed during the backtest period

**Winning/Losing Trades**
- Count of profitable vs unprofitable trades

**Win Rate**
- Percentage of winning trades
- Formula: `(Winning Trades / Total Trades) × 100`
- **Good:** >55%
- **Excellent:** >65%

**Total P/L**
- Total profit or loss in USD
- Should be positive for profitable strategy

**Return %**
- Percentage return on initial balance
- Formula: `(Total P/L / Initial Balance) × 100`

**Max Drawdown**
- Largest peak-to-trough decline
- Indicates worst-case scenario risk
- **Lower is better**

**Sharpe Ratio**
- Risk-adjusted return measure
- **Good:** >1.0
- **Excellent:** >2.0

---

## Analyzing CSV Results

The backtest exports a CSV file with all trades:

**Columns:**
- `symbol`: Trading symbol
- `action`: BUY or SELL
- `entry_price`: Entry price
- `entry_time`: When trade was opened
- `exit_time`: When trade was closed
- `exit_reason`: Why it closed (hold time, stop loss, etc.)
- `lot_size`: Position size
- `pnl`: Profit/Loss for this trade
- `balance_after`: Balance after closing

**Open in Excel or Google Sheets** to analyze patterns:
- Which symbols perform best?
- What times of day are most profitable?
- Are there days with unusual losses?

---

## Important Notes

### ⚠️ Requirements

**CRITICAL: You MUST have MetaTrader 5 open and logged in to run backtests!**

The backtest:
- ✅ Uses REAL historical data from MT5
- ✅ Applies the exact 6-step strategy logic
- ✅ Checks signals every 5 minutes
- ✅ Calculates P/L from actual price movements
- ✅ No future peeking - uses only past data

### ⚠️ Limitations

1. **MT5 Required**
   - MT5 must be running and logged in
   - Backtest downloads historical bars from your MT5 terminal

2. **Simplified Execution**
   - Assumes instant fills at close prices
   - Doesn't account for real slippage/spread variations
   - No connection issues simulated

3. **Market Conditions**
   - Past performance ≠ future results
   - Market conditions change
   - Always test on demo first

### ✅ Best Practices

1. **Test Multiple Periods**
   ```bash
   python run_backtest.py --days 7   # Recent week
   python run_backtest.py --days 30  # Last month
   python run_backtest.py --days 90  # Last quarter
   ```

2. **Test All Symbols**
   - Test each PainX and GainX symbol separately
   - Compare performance across volatility levels

3. **Compare Bot Types**
   ```bash
   # Test SELL strategy
   python run_backtest.py --symbol "PainX 400" --bot pain --days 30

   # Test BUY strategy
   python run_backtest.py --symbol "GainX 400" --bot gain --days 30
   ```

4. **Document Results**
   - Keep CSV exports organized
   - Track which parameters work best
   - Note market conditions during test period

---

## Optimization Workflow

### Step 1: Baseline Test

Run default settings for 30 days:

```bash
python run_backtest.py --symbol "PainX 400" --days 30
```

### Step 2: Adjust Config Parameters

Edit `config.json` and test different settings:

**Test smaller lot size:**
```json
"risk": {
  "lot_size": 0.01
}
```

**Test different hold times:**
```json
"strategy": {
  "hold_minutes": 3  // Try 3, 5, 10 minutes
}
```

### Step 3: Re-run Backtest

```bash
python run_backtest.py --symbol "PainX 400" --days 30 --export test_small_lots.csv
```

### Step 4: Compare Results

Compare CSV files to see which settings perform better.

### Step 5: Forward Test on Demo

Once backtesting looks good, test on live demo account:

```bash
python -m pain_gain_bot.main --bot pain --demo
```

---

## Troubleshooting

### "No trades executed"

**Possible causes:**
- Market conditions didn't meet all 6 confirmations
- Symbol was outside trading session
- Daily stop was reached early

**Solutions:**
- Try longer backtest period (30+ days)
- Check if session hours are configured correctly
- Review signal generation logs

### "MT5 connection failed"

**Solutions:**
1. Open MetaTrader 5
2. Log into your account
3. Ensure AutoTrading is enabled
4. Run backtest again

### "Module not found"

**Solution:**
```bash
pip install -r requirements_bot.txt
```

---

## Next Steps

After successful backtesting:

1. ✅ **Test on demo** for at least 1-2 weeks
2. ✅ **Monitor real-time** performance vs backtest
3. ✅ **Document any differences**
4. ✅ **Only go live** after consistent demo results

---

## Advanced Usage

### Programmatic Backtesting

You can also import the backtester in Python:

```python
from pain_gain_bot.backtest.historical_backtester import HistoricalBacktester

# Create backtester
bt = HistoricalBacktester(
    start_date='2025-01-01',
    end_date='2025-01-31',
    initial_balance=500.0
)

# Run backtest (requires MT5 to be open!)
results = bt.run_backtest('PainX 400', bot_type='PAIN')

# Access results
print(f"Win rate: {results['win_rate']:.1f}%")
print(f"Total P/L: ${results['total_pnl']:.2f}")

# Export
bt.export_results('my_results.csv')
```

---

## Support

For questions about backtesting:
- Check the debug output in console
- Review exported CSV for trade details
- Compare with live demo performance

---

**Remember:** Backtesting is a tool, not a guarantee. Always verify with demo trading before going live!
