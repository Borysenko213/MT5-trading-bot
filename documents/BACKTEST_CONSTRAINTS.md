# Backtesting Constraints Guide

## Overview

The backtesting system implements a strict 6-step confirmation strategy. If you're getting **0 trades** in your backtests, it means the market conditions during your test period don't match all 6 requirements.

This guide explains each constraint and how to relax them.

---

## Quick Solution: Use Relaxed Mode

The **easiest way** to get backtest results is to use the relaxed mode:

```bash
python run_backtest.py --symbol "PainX 400" --days 30 --relaxed
```

This automatically weakens the constraints to show more trades.

---

## The 6-Step Strategy Constraints

### **Step 1: Daily Bias Filter** ⚠️ BIGGEST BLOCKER

**What it does:**
- PainBot only trades when daily wick direction is **DOWN** (SELL bias)
- GainBot only trades when daily wick direction is **UP** (BUY bias)

**Why you get 0 trades:**
- If you test PainBot during a BUY market (prices going up), it will find 0 trades
- This is the #1 reason for empty backtest results

**How to relax:**

**Option A - Use the correct bot:**
```bash
# If market has BUY bias, use GainBot:
python run_backtest.py --symbol "PainX 400" --days 30 --bot gain

# If market has SELL bias, use PainBot:
python run_backtest.py --symbol "PainX 400" --days 30 --bot pain
```

**Option B - Use relaxed mode:**
```bash
python run_backtest.py --symbol "PainX 400" --days 30 --relaxed
```
In relaxed mode, daily bias is informational only - bot will trade both directions.

**Code location:** `historical_backtester.py:183-190`

---

### **Step 2: Daily Stop (50% Wick Filled)**

**What it does:**
- Checks if price has retraced 50% of the daily wick
- If yes, trading stops for the day (risk management)

**Impact:** Medium - prevents trading after significant reversals

**How to relax:**
- Relaxed mode makes this a warning only (doesn't block trades)

**Code location:** `historical_backtester.py:195-203`

---

### **Step 3: H4 50% Fibonacci Confirmation**

**What it does:**
- Checks if M15 price is within 50% retracement zone of H4 candle

**Impact:** Medium

**How to relax:**
- Relaxed mode makes this optional

**Code location:** `historical_backtester.py:212-216`

---

### **Step 4: H1 Shingle (EMA) Confirmation**

**What it does:**
- For BUY: Price must be above H1 shingle AND shingle must be GREEN
- For SELL: Price must be below H1 shingle AND shingle must be RED

**Impact:** Medium

**How to relax:**
- Relaxed mode makes this optional

**Code location:** `historical_backtester.py:226-235`

---

### **Step 5: M30/M15 Snake Filter** ⚠️ SECOND BIGGEST BLOCKER

**What it does:**
- Strict mode: Requires **BOTH** M30 and M15 snake colors to match bias
- For BUY: Both must be GREEN
- For SELL: Both must be RED

**Impact:** High - it's rare for both timeframes to align perfectly

**How to relax:**
- Relaxed mode requires **only ONE** of M30 or M15 (not both)

**Code location:** `historical_backtester.py:262-265`

---

### **Step 6: M5/M1 Purple Line Break & Retest**

**What it does:**
- Checks for purple line (EMA) break and retest pattern on entry timeframe

**Impact:** Medium-High - requires specific entry pattern

**How to relax:**
- Relaxed mode makes this optional

**Code location:** `historical_backtester.py:289-292`

---

## Comparison: Strict vs Relaxed

| Constraint | Strict Mode | Relaxed Mode |
|-----------|-------------|--------------|
| **Daily Bias** | Must match bot type | Informational only |
| **Daily Stop** | Blocks trades | Warning only |
| **H4 Fibonacci** | Required | Optional |
| **H1 Shingle** | Required | Optional |
| **M30/M15 Snake** | BOTH required | ONE required |
| **Purple Line** | Required | Optional |

---

## Usage Examples

### Test with strict strategy (original):
```bash
python run_backtest.py --symbol "PainX 400" --days 30
```

### Test with relaxed constraints (more trades):
```bash
python run_backtest.py --symbol "PainX 400" --days 30 --relaxed
```

### Test GainBot on BUY bias market:
```bash
python run_backtest.py --symbol "GainX 400" --days 30 --bot gain
```

### Test longer period to find more trade opportunities:
```bash
python run_backtest.py --symbol "PainX 400" --days 90 --relaxed
```

---

## Understanding "0 Trades" Results

**0 trades is NOT a bug!** It means:

1. ✅ The backtester is working correctly
2. ✅ It's checking signals every 5 minutes
3. ✅ Market conditions don't match the strict 6-step strategy

**The 6-step strategy is VERY conservative** - it requires all confirmations to align, which happens rarely.

### Solutions:

1. **Use relaxed mode** - Weakens constraints to show more trades
2. **Test GainBot** - If PainBot finds nothing, market might have BUY bias
3. **Test longer periods** - 90+ days to find more varied conditions
4. **Accept it** - 0 trades means the strategy correctly avoided bad setups

---

## Files Reference

- **Strict Backtester:** `pain_gain_bot/backtest/historical_backtester.py`
- **Relaxed Backtester:** `pain_gain_bot/backtest/relaxed_backtester.py`
- **Run Script:** `run_backtest.py`

---

## Creating Custom Constraint Levels

You can create your own backtester with custom constraints by:

1. Copy `relaxed_backtester.py` to `my_custom_backtester.py`
2. Modify the `check_signal_at_time()` method
3. Comment out any `return None` statements for constraints you want to skip
4. Update `run_backtest.py` to use your custom backtester

Example: Skip only daily bias check:
```python
# In check_signal_at_time():
# Comment out lines 183-190 to ignore daily bias
# if bot_type == 'PAIN' and daily_bias != 'SELL':
#     return None
```

---

## Recommended Testing Approach

1. **Start with relaxed mode** to verify the backtester works:
   ```bash
   python run_backtest.py --symbol "PainX 400" --days 30 --relaxed
   ```

2. **Try both bot types** to see which matches market bias:
   ```bash
   python run_backtest.py --symbol "PainX 400" --days 30 --bot pain --relaxed
   python run_backtest.py --symbol "PainX 400" --days 30 --bot gain --relaxed
   ```

3. **Test longer periods** for more data:
   ```bash
   python run_backtest.py --symbol "PainX 400" --days 90 --relaxed
   ```

4. **Once you see trades, try strict mode** to see the difference:
   ```bash
   python run_backtest.py --symbol "PainX 400" --days 90
   ```

This helps you understand how strict vs relaxed constraints affect trade frequency and quality.
