# Complete Debug Guide - Every Execution Step Tracked

All execution flow now has `print()` statements to track where code blocks.

---

## Files Modified with Debug Prints

### 1. `pain_gain_bot/main.py`
- Entry point tracking
- Bot selection
- Before calling `run_pain_bot()`

### 2. `pain_gain_bot/config.py`
- Config file loading
- JSON parsing
- Field conversion
- Config object creation

### 3. `pain_gain_bot/bots/pain_bot.py`
- `__init__()` - instance creation
- `initialize()` - MT5 connection
- `run()` - main trading loop (every iteration)
- `process_symbol()` - signal checking

### 4. `pain_gain_bot/data/mt5_connector.py`
- MT5 initialization
- MT5 login with credentials
- Symbol verification

### 5. `pain_gain_bot/strategy/signals.py`
- Signal generation (6 steps)
- Each timeframe check
- Signal result

---

## Complete Execution Flow with Debug Messages

### Phase 1: Startup

```
[DEBUG] main() started
[DEBUG] load_config() called with filepath: config.json
[DEBUG] Opening config file: config.json
[DEBUG] Config file loaded, keys: ['broker', 'symbols', 'risk', ...]
[DEBUG] Removing comment fields starting with '_'
[DEBUG] Processing session times
[DEBUG] session_start converted: 19:00:00
[DEBUG] session_end converted: 06:00:00
[DEBUG] daily_close_time converted: 16:00:00
[DEBUG] Cleaning nested comment fields
[DEBUG] Creating Config object...
[OK] Configuration loaded from config.json
[DEBUG] Broker server: Weltrade-Demo
[DEBUG] Demo account: 19498321
[DEBUG] Pain symbols: ['PainX 400']
[DEBUG] load_config() completed
[DEBUG] Selected bot mode: pain
[DEBUG] Calling run_pain_bot()...
```

### Phase 2: Bot Creation

```
[DEBUG] Creating PainBot instance...
[DEBUG] PainBot.__init__() started
[DEBUG] Loading pain_symbols from config: ['PainX 400']
[DEBUG] Creating SignalEngine...
[DEBUG] Creating OrderManager...
[DEBUG] PainBot.__init__() completed
[DEBUG] PainBot instance created, calling initialize()...
```

### Phase 3: MT5 Connection

```
[DEBUG] PainBot.initialize() started
[DEBUG] Calling connector.initialize() with use_demo=True
[DEBUG] MT5Connector.initialize() started
[DEBUG] Calling mt5.initialize()...
```

**IF MT5 IS NOT OPEN:**
```
[DEBUG] mt5.initialize() FAILED with error: (-10005, 'IPC timeout')
[DEBUG] connector.initialize() returned False
[DEBUG] PainBot initialization FAILED
```

**IF MT5 IS OPEN:**
```
[DEBUG] mt5.initialize() succeeded
[DEBUG] Attempting login: account=19498321, server=Weltrade-Demo, use_demo=True
[DEBUG] mt5.login() succeeded
[DEBUG] connector.initialize() succeeded
[DEBUG] Calling connector.verify_symbols(['PainX 400'])
[DEBUG] PainBot initialized successfully, calling run()...
```

### Phase 4: Main Loop Starts

```
[DEBUG] PainBot.run() started
[DEBUG] Entering main loop...
[DEBUG] === Iteration 1 ===
[DEBUG] Checking daily reset
[DEBUG] Checking daily limits
[DEBUG] Can trade: True, reason: OK
[DEBUG] Checking trading session
```

**IF OUTSIDE TRADING HOURS:**
```
[DEBUG] Outside trading session - sleeping 60s
(sleeps 60 seconds, then repeats)
```

**IF INSIDE TRADING HOURS:**
```
[DEBUG] Inside trading session - proceeding
[DEBUG] Managing existing positions
[DEBUG] Scanning 1 symbols: ['PainX 400']
[DEBUG] Processing symbol: PainX 400
[DEBUG] process_symbol(PainX 400) called
[DEBUG] Calling signal_engine.generate_signal(PainX 400)
```

### Phase 5: Signal Generation (6 Steps)

```
[DEBUG] SignalEngine.generate_signal() called for PainX 400
[DEBUG] Step 1: Checking daily bias for PainX 400
[DEBUG] Analyzing daily bias (refresh needed)
[DEBUG] Daily bias: SELL
[DEBUG] Step 2: Checking daily stop condition
[DEBUG] Current price: 145.234
[DEBUG] Step 3: Checking H4 confirmation
[DEBUG] H4 confirmed: True
[DEBUG] Step 4: Checking H1 structure
[DEBUG] H1 confirmed: True
[DEBUG] Step 5: Checking M30/M15 filter
[DEBUG] M30/M15 confirmed: True
[DEBUG] Step 6: Checking M5/M1 entry
[DEBUG] M5/M1 entry signal: False, price: None
[DEBUG] M5/M1 entry not confirmed - returning
[DEBUG] Signal result: action=None, price=None
```

**IF SIGNAL FOUND:**
```
[DEBUG] Step 6: Checking M5/M1 entry
[DEBUG] M5/M1 entry signal: True, price: 145.234
[DEBUG] SIGNAL GENERATED: SELL at 145.234
[DEBUG] Signal result: action=SELL, price=145.234
[DEBUG] SELL signal detected - proceeding with order
```

### Phase 6: End of Iteration

```
[DEBUG] Sleeping 30 seconds before next iteration...
[DEBUG] === Iteration 2 ===
(repeats)
```

---

## How to Read Debug Output

### 1. **Find Where It Stopped**

Look for the **LAST** `[DEBUG]` message. That's where execution stopped.

#### Example 1: MT5 Not Open
```
[DEBUG] Calling mt5.initialize()...
[DEBUG] mt5.initialize() FAILED with error: (-10005, 'IPC timeout')
<-- STOPPED HERE
```
**Problem:** MetaTrader 5 not running
**Solution:** Open MT5

#### Example 2: Wrong Credentials
```
[DEBUG] mt5.initialize() succeeded
[DEBUG] Attempting login: account=19498321, server=Weltrade-Demo, use_demo=True
[DEBUG] mt5.login() FAILED with error: (10004, 'Invalid account')
<-- STOPPED HERE
```
**Problem:** Wrong account number or expired demo
**Solution:** Create new demo account, update config.json

#### Example 3: Running Normally
```
[DEBUG] === Iteration 15 ===
[DEBUG] Checking daily limits
[DEBUG] Can trade: True, reason: OK
[DEBUG] Inside trading session - proceeding
[DEBUG] Processing symbol: PainX 400
[DEBUG] Step 1: Checking daily bias
[DEBUG] Daily bias: SELL
[DEBUG] Step 2: Checking daily stop condition
[DEBUG] Step 3: Checking H4 confirmation
[DEBUG] H4 confirmed: False
[DEBUG] H4 not confirmed - returning
[DEBUG] Signal result: action=None, price=None
[DEBUG] Sleeping 30 seconds...
[DEBUG] === Iteration 16 ===
(continues...)
```
**Status:** Running normally, looking for signals

---

## Common Blocking Points

### Block 1: Config Loading
```
[DEBUG] load_config() called with filepath: config.json
[DEBUG] FileNotFoundError: config.json not found
```
**Problem:** No config.json file
**Solution:** Create config.json from config_spanish.json or config_example.json

### Block 2: MT5 Initialize
```
[DEBUG] Calling mt5.initialize()...
[DEBUG] mt5.initialize() FAILED with error: (-10005, 'IPC timeout')
```
**Problem:** MT5 not running
**Solution:** Open MetaTrader 5

### Block 3: MT5 Login
```
[DEBUG] Attempting login: account=19498321...
[DEBUG] mt5.login() FAILED with error: (...)
```
**Problem:** Wrong credentials or expired account
**Solution:** Update config.json with correct credentials

### Block 4: Outside Trading Session
```
[DEBUG] Checking trading session
[DEBUG] Outside trading session - sleeping 60s
```
**Status:** Normal - bot waits for trading hours (19:00-06:00 COL)
**Action:** Wait or change session times in config

### Block 5: Daily Limits Reached
```
[DEBUG] Can trade: False, reason: Daily stop reached
[DEBUG] Cannot trade - sleeping 60s
```
**Status:** Normal - hit daily loss limit
**Action:** Wait for next day or adjust limits in config

---

## Tracking Signal Generation

### No Signal (Most Common)

```
[DEBUG] SignalEngine.generate_signal() called for PainX 400
[DEBUG] Step 1: Checking daily bias
[DEBUG] Daily bias: SELL
[DEBUG] Step 2: Checking daily stop condition
[DEBUG] Step 3: Checking H4 confirmation
[DEBUG] H4 confirmed: False
[DEBUG] H4 not confirmed - returning
```
**Status:** Normal - market conditions don't meet strategy criteria
**At which step it failed:** H4 confirmation (Step 3)

### Signal Found

```
[DEBUG] Step 1: Checking daily bias
[DEBUG] Daily bias: SELL
[DEBUG] Step 2: Checking daily stop condition
[DEBUG] Step 3: Checking H4 confirmation
[DEBUG] H4 confirmed: True
[DEBUG] Step 4: Checking H1 structure
[DEBUG] H1 confirmed: True
[DEBUG] Step 5: Checking M30/M15 filter
[DEBUG] M30/M15 confirmed: True
[DEBUG] Step 6: Checking M5/M1 entry
[DEBUG] M5/M1 entry signal: True, price: 145.234
[DEBUG] SIGNAL GENERATED: SELL at 145.234
```
**Status:** SIGNAL FOUND - all 6 steps passed
**Action:** Bot will place order

---

## Quick Troubleshooting

### Problem: Nothing Happens After Starting

**Check Last Debug Message:**
```bash
python -m pain_gain_bot.main --bot pain --demo
```

**Find the last `[DEBUG]` line you see.**

| Last Message | Problem | Solution |
|--------------|---------|----------|
| `mt5.initialize() FAILED` | MT5 not open | Open MetaTrader 5 |
| `mt5.login() FAILED` | Wrong credentials | Update config.json |
| `FileNotFoundError` | No config file | Create config.json |
| `Outside trading session` | Not trading hours | Wait or adjust session times |
| `Cannot trade - sleeping` | Daily limit hit | Wait for next day |

### Problem: Bot Runs But No Trades

**This is NORMAL.** Signals are rare because strategy requires:
1. D1 wick direction (SELL or BUY bias)
2. H4 50% Fibonacci coverage
3. H1 shingle alignment
4. M30 & M15 snake same color
5. M1 purple line break-retest

**All 6 conditions must be TRUE** at the same time.

**Check Which Step Fails:**
```
[DEBUG] Step 3: Checking H4 confirmation
[DEBUG] H4 confirmed: False  <-- Failed here
[DEBUG] H4 not confirmed - returning
```

This shows H4 (Step 3) is failing.

---

## Advanced: Filtering Debug Output

### Show Only Errors
```bash
python -m pain_gain_bot.main --bot pain --demo 2>&1 | grep -E "(FAILED|ERROR|Exception)"
```

### Show Only Key Checkpoints
```bash
python -m pain_gain_bot.main --bot pain --demo 2>&1 | grep -E "(=== Iteration|mt5\.|Signal result)"
```

### Show Signal Steps Only
```bash
python -m pain_gain_bot.main --bot pain --demo 2>&1 | grep -E "Step [1-6]"
```

---

## Example: Full Successful Execution

```
[DEBUG] main() started
[DEBUG] load_config() called
[OK] Configuration loaded from config.json
[DEBUG] Selected bot mode: pain
[DEBUG] Creating PainBot instance...
[DEBUG] PainBot.__init__() completed
[DEBUG] Calling connector.initialize()
[DEBUG] mt5.initialize() succeeded
[DEBUG] mt5.login() succeeded
[DEBUG] PainBot initialized successfully
[DEBUG] PainBot.run() started
[DEBUG] Entering main loop...
[DEBUG] === Iteration 1 ===
[DEBUG] Can trade: True
[DEBUG] Inside trading session - proceeding
[DEBUG] Processing symbol: PainX 400
[DEBUG] SignalEngine.generate_signal() called
[DEBUG] Step 1: Daily bias: SELL
[DEBUG] Step 2: Daily stop: OK
[DEBUG] Step 3: H4 confirmed: True
[DEBUG] Step 4: H1 confirmed: True
[DEBUG] Step 5: M30/M15 confirmed: True
[DEBUG] Step 6: M5/M1 entry signal: False
[DEBUG] Signal result: action=None
[DEBUG] Sleeping 30 seconds...
[DEBUG] === Iteration 2 ===
(continues running normally)
```

---

## Summary

**Every key function now prints:**
- When it starts
- What it's doing
- Results/decisions
- When it finishes or fails

**To troubleshoot:**
1. Run the bot
2. Find the LAST `[DEBUG]` message
3. Compare to expected flow in this guide
4. Identify the blocking point
5. Apply the solution

**Most common block:**
```
[DEBUG] mt5.initialize() FAILED
```
= **Open MetaTrader 5 first!**

---

**All debug prints use `[DEBUG]` prefix so they're easy to find and filter.**
