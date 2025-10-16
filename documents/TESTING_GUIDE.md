# Testing Guide - Pain/Gain Trading System

Complete testing procedures to validate the bot before live deployment.

---

## Testing Phases

### Phase 1: Installation Validation ✅
### Phase 2: Connection Testing ✅
### Phase 3: Indicator Verification ✅
### Phase 4: Signal Generation Testing ✅
### Phase 5: Order Execution Testing ✅
### Phase 6: Risk Management Testing ✅
### Phase 7: Extended Demo Trading ✅
### Phase 8: Live Deployment (with minimal risk) ✅

---

## Phase 1: Installation Validation

### 1.1 Verify Python Installation

```bash
python --version
# Expected: Python 3.11.0 or higher

pip --version
# Expected: pip 22.3 or higher
```

### 1.2 Verify MT5 Installation

1. Open MetaTrader 5
2. Check version (Help → About)
3. Verify account login works manually
4. Confirm symbols visible in Market Watch

### 1.3 Verify Dependencies

```bash
cd C:\Users\Administrator\Documents\trading
pip install -r requirements_bot.txt
```

All packages should install without errors.

### 1.4 Verify Project Structure

Check that all files exist:

```
pain_gain_bot/
├── __init__.py ✓
├── config.py ✓
├── main.py ✓
├── bots/ ✓
├── data/ ✓
├── indicators/ ✓
├── strategy/ ✓
└── utils/ ✓
```

---

## Phase 2: Connection Testing

### 2.1 Test MT5 Python Integration

Create a test file `test_connection.py`:

```python
import MetaTrader5 as mt5

# Initialize MT5
if not mt5.initialize():
    print("❌ MT5 initialization failed")
    quit()

print("✅ MT5 initialized successfully")

# Login to demo account
account = 19498321
password = "YOUR_PASSWORD"
server = "Weltrade"

if mt5.login(account, password=password, server=server):
    print(f"✅ Logged in to account {account}")

    # Get account info
    account_info = mt5.account_info()
    print(f"  Balance: ${account_info.balance}")
    print(f"  Leverage: 1:{account_info.leverage}")
else:
    print("❌ Login failed")

mt5.shutdown()
```

Run it:
```bash
python test_connection.py
```

**Expected Output:**
```
✅ MT5 initialized successfully
✅ Logged in to account 19498321
  Balance: $500.00
  Leverage: 1:10000
```

### 2.2 Test Symbol Access

```python
import MetaTrader5 as mt5

mt5.initialize()
mt5.login(19498321, password="YOUR_PASSWORD", server="Weltrade")

symbols = ["PainX 400", "PainX 600", "PainX 800", "PainX 999",
           "GainX 400", "GainX 600", "GainX 800", "GainX 999"]

for symbol in symbols:
    info = mt5.symbol_info(symbol)
    if info:
        print(f"✅ {symbol}: Spread={info.spread} points")
    else:
        print(f"❌ {symbol}: Not found")

mt5.shutdown()
```

All symbols should show ✅

---

## Phase 3: Indicator Verification

### 3.1 Test Indicator Calculations

```python
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.indicators.technical import indicators

connector.initialize(use_demo=True)

symbol = "PainX 400"
df_h1 = connector.get_bars(symbol, 'H1', count=100)

# Test snake indicator
fast_ema, slow_ema, color = indicators.calculate_snake(df_h1)
print(f"Snake: {color}")
print(f"  Fast EMA: {fast_ema.iloc[-1]:.5f}")
print(f"  Slow EMA: {slow_ema.iloc[-1]:.5f}")

# Test shingle
shingle, shingle_color = indicators.calculate_shingle(df_h1)
print(f"\nShingle: {shingle_color}")
print(f"  Value: {shingle.iloc[-1]:.5f}")

# Test purple line
purple = indicators.calculate_purple_line(df_h1)
print(f"\nPurple Line: {purple.iloc[-1]:.5f}")

connector.shutdown()
```

**Expected:** All indicators calculate without errors and show reasonable values.

### 3.2 Test D1 Wick Analysis

```python
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.indicators.technical import indicators

connector.initialize(use_demo=True)

symbol = "PainX 400"
df_d1 = connector.get_bars(symbol, 'D1', count=5)

direction, wick_size, wick_50 = indicators.check_wick_direction(df_d1)

print(f"D1 Analysis:")
print(f"  Direction: {direction}")
print(f"  Wick Size: {wick_size:.5f}")
print(f"  50% Level: {wick_50:.5f}")

connector.shutdown()
```

**Expected:** Direction is either 'UP' or 'DOWN', with valid wick values.

---

## Phase 4: Signal Generation Testing

### 4.1 Test Signal Engine

```python
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.strategy.signals import SignalEngine

connector.initialize(use_demo=True)

engine = SignalEngine()
symbol = "PainX 400"

signal = engine.generate_signal(symbol)

print(f"Signal for {symbol}:")
print(f"  Action: {signal['action']}")
print(f"  Price: {signal['price']}")
print(f"  Confirmations:")
for key, value in signal['confirmations'].items():
    print(f"    {key}: {value}")

connector.shutdown()
```

**Expected:** Signal generated with all confirmation checks logged.

### 4.2 Monitor Signals Over Time

Run for 30 minutes and watch for signals:

```bash
python -c "
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.strategy.signals import SignalEngine
import time

connector.initialize(use_demo=True)
engine = SignalEngine()

for i in range(60):  # 60 iterations = 30 minutes
    signal = engine.generate_signal('PainX 400')
    if signal['action']:
        print(f'SIGNAL: {signal}')
    time.sleep(30)

connector.shutdown()
"
```

---

## Phase 5: Order Execution Testing

### 5.1 Test Order Placement (Minimal Lot)

⚠️ This will place a real order on demo account!

```python
from pain_gain_bot.data.mt5_connector import connector

connector.initialize(use_demo=True)
connector.verify_symbols(["PainX 400"])

# Place minimal test order
result = connector.send_order(
    symbol="PainX 400",
    order_type="SELL",
    volume=0.01,  # Minimal lot
    magic=999999,
    comment="Test order"
)

if result:
    print(f"✅ Order placed: Ticket {result['ticket']}")
    print(f"  Price: {result['price']}")

    # Close immediately
    input("Press Enter to close order...")
    connector.close_position(result['ticket'])
    print("✅ Order closed")
else:
    print("❌ Order failed")

connector.shutdown()
```

**Expected:** Order places and closes successfully.

### 5.2 Test Order Manager

```python
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.strategy.order_manager import OrderManager
from pain_gain_bot.config import config

connector.initialize(use_demo=True)
config.risk.lot_size = 0.01  # Use minimal lot

order_mgr = OrderManager("PAIN", 100000)

# Test order execution
result = order_mgr.execute_order(
    symbol="PainX 400",
    action="SELL",
    volume=0.01
)

if result:
    print(f"✅ Order Manager test passed")
    print(f"  Active positions: {len(order_mgr.active_positions)}")

    # Wait and manage
    import time
    time.sleep(10)
    order_mgr.manage_positions()
else:
    print("❌ Order Manager test failed")

connector.shutdown()
```

---

## Phase 6: Risk Management Testing

### 6.1 Test Daily Limits

```python
from pain_gain_bot.strategy.risk_manager import risk_manager
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.config import config

connector.initialize(use_demo=True)
risk_manager.initialize()

# Override limits for testing
config.risk.daily_stop_usd = 10.0
config.risk.daily_target_usd = 20.0

# Check current status
stats = risk_manager.get_risk_status()

print("Risk Status:")
for key, value in stats.items():
    print(f"  {key}: {value}")

# Test limit check
can_trade, reason = risk_manager.check_daily_limits()
print(f"\nCan trade: {can_trade}")
print(f"Reason: {reason}")

connector.shutdown()
```

### 6.2 Test Session Timing

```python
from pain_gain_bot.strategy.risk_manager import risk_manager
from datetime import datetime

# Check if in session
in_session = risk_manager.is_trading_session()
print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
print(f"In trading session: {in_session}")
```

---

## Phase 7: Extended Demo Trading

### 7.1 Run Full Bot on Demo (24-48 Hours)

```bash
python -m pain_gain_bot.main --bot both --demo
```

**Monitor:**
- Logs in `logs/` directory
- MT5 Terminal (positions and history)
- Console output every 10 minutes

**Check For:**
- ✅ Signals generate correctly
- ✅ Orders execute when conditions met
- ✅ Positions close after 5 minutes
- ✅ Re-entries respect timing rules
- ✅ Daily stops trigger correctly
- ✅ Purple line logic works
- ✅ No crashes or errors

### 7.2 Validation Checklist

After 24-48 hours of demo trading:

- [ ] Bot ran without crashes
- [ ] At least 5 trades executed
- [ ] All trades followed strategy rules
- [ ] Stop loss logic worked correctly
- [ ] Take profit logic worked correctly
- [ ] Daily limits respected
- [ ] Logs are detailed and accurate
- [ ] No unexpected behavior

---

## Phase 8: Live Deployment (Cautious Approach)

⚠️ **Only proceed if demo testing was 100% successful!**

### 8.1 Pre-Live Checklist

- [ ] Demo testing completed successfully (minimum 1 week)
- [ ] All validation tests passed
- [ ] Reviewed all logs for errors
- [ ] Understood all strategy parameters
- [ ] Comfortable with risk amount
- [ ] Backup funds available
- [ ] Monitoring plan in place

### 8.2 Initial Live Test (Minimal Risk)

**Day 1-3: Single Symbol, Minimal Lot**

```python
# Edit config.json
{
  "broker": {
    "use_demo": false  # ⚠️ LIVE MODE
  },
  "symbols": {
    "pain_symbols": ["PainX 400"],  # One symbol only
    "gain_symbols": ["GainX 400"]   # One symbol only
  },
  "risk": {
    "lot_size": 0.01,  # MINIMAL LOT
    "daily_stop_usd": 5.0,  # Very low limit
    "daily_target_usd": 10.0
  }
}
```

Run:
```bash
python -m pain_gain_bot.main --bot both --live
```

**Monitor continuously for first 24 hours.**

### 8.3 Gradual Scale-Up

If Day 1-3 successful:

**Day 4-7:**
- Increase to 2 symbols per bot
- Increase lot to 0.05
- Increase daily stop to 20

**Week 2:**
- Add all symbols
- Increase to configured lot size (0.10)
- Use full daily limits (40/100)

---

## Troubleshooting Test Failures

### No Signals Generated

**Possible Causes:**
1. Market conditions don't meet all criteria
2. Outside trading session
3. Daily stop already hit

**Solutions:**
- Wait for proper market setup
- Check D1 for wick bias
- Review all timeframe confirmations

### Orders Fail to Execute

**Possible Causes:**
1. Insufficient balance
2. Spread too high
3. Symbol not trading
4. Wrong lot size

**Solutions:**
- Check account balance
- Monitor spread in MT5
- Verify symbol is active
- Adjust lot size in config

### Positions Don't Close

**Possible Causes:**
1. Purple line not breaking
2. Hold time not reached
3. Connection issue

**Solutions:**
- Check M5 purple line visually
- Wait for full 5-minute candle
- Verify MT5 connection

---

## Performance Metrics to Track

### Daily Metrics
- Total trades
- Win rate
- Average profit per trade
- Average loss per trade
- Maximum drawdown

### Weekly Metrics
- Total P/L
- Profit factor (gross profit / gross loss)
- Sharpe ratio
- Maximum consecutive wins/losses

### Monthly Metrics
- Return on account (%)
- Risk-adjusted return
- Strategy adherence rate
- Error/exception count

---

## Acceptance Criteria

Before considering the bot production-ready:

✅ **Stability:**
- Runs continuously for 7+ days without crashes
- Zero critical errors in logs

✅ **Strategy Compliance:**
- All trades follow documented rules
- Entry confirmations match strategy
- Exit rules properly implemented

✅ **Risk Management:**
- Daily stops work 100% of the time
- Position sizing correct
- No violations of risk limits

✅ **Performance:**
- Positive expectancy (average win > average loss × (1/win_rate - 1))
- Acceptable drawdown (<20% of daily stop)
- Profitable over test period

---

## Final Sign-Off

Before live trading with full capital:

1. **Developer Sign-Off:** All tests passed ✅
2. **Client Review:** Strategy working as expected ✅
3. **Risk Acknowledgment:** Client understands risks ✅
4. **Monitoring Plan:** Daily review schedule established ✅

---

**Remember:** No trading system is perfect. Always monitor actively, especially in first weeks of live operation!
