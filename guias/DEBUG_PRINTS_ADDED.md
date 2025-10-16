# Debug Prints Added to Code

I've added `print()` statements (like console.log) throughout the code to help you see exactly where the bot blocks.

---

## Files Modified with Debug Prints

### 1. **pain_gain_bot/main.py**
- `main()` function start
- Bot selection (`args.bot`)
- Before calling `run_pain_bot()`
- Inside `run_pain_bot()` - shows creation and initialization steps

### 2. **pain_gain_bot/bots/pain_bot.py**
- `__init__()` start and end
- Loading symbols from config
- Creating SignalEngine
- Creating OrderManager
- `initialize()` start
- Before and after `connector.initialize()` call
- Before `connector.verify_symbols()` call

### 3. **pain_gain_bot/data/mt5_connector.py**
- `initialize()` function start
- Before `mt5.initialize()` call
- After `mt5.initialize()` (success/fail)
- Before `mt5.login()` call with credentials shown
- After `mt5.login()` (success/fail)

---

## What You'll See Now

### When Bot Runs Successfully:
```
[DEBUG] main() started
[DEBUG] Selected bot mode: pain
[DEBUG] Calling run_pain_bot()...
[DEBUG] Creating PainBot instance...
[DEBUG] PainBot.__init__() started
[DEBUG] Loading pain_symbols from config: ['PainX400']
[DEBUG] Creating SignalEngine...
[DEBUG] Creating OrderManager...
[DEBUG] PainBot.__init__() completed
[DEBUG] PainBot instance created, calling initialize()...
[DEBUG] PainBot.initialize() started
[DEBUG] Calling connector.initialize() with use_demo=True
[DEBUG] MT5Connector.initialize() started
[DEBUG] Calling mt5.initialize()...
[DEBUG] mt5.initialize() succeeded
[DEBUG] Attempting login: account=19498321, server=Weltrade-Demo, use_demo=True
[DEBUG] mt5.login() succeeded
[DEBUG] connector.initialize() succeeded
[DEBUG] Calling connector.verify_symbols(['PainX400'])
[DEBUG] PainBot initialized successfully, calling run()...
```

### When MT5 is NOT Open:
```
[DEBUG] main() started
[DEBUG] Selected bot mode: pain
[DEBUG] Calling run_pain_bot()...
[DEBUG] Creating PainBot instance...
[DEBUG] PainBot.__init__() started
[DEBUG] Loading pain_symbols from config: ['PainX400']
[DEBUG] Creating SignalEngine...
[DEBUG] Creating OrderManager...
[DEBUG] PainBot.__init__() completed
[DEBUG] PainBot instance created, calling initialize()...
[DEBUG] PainBot.initialize() started
[DEBUG] Calling connector.initialize() with use_demo=True
[DEBUG] MT5Connector.initialize() started
[DEBUG] Calling mt5.initialize()...
[DEBUG] mt5.initialize() FAILED with error: (-10005, 'IPC timeout')
<- STOPS HERE - MT5 NOT OPEN
[DEBUG] connector.initialize() returned False
[DEBUG] PainBot initialization FAILED
```

### When Credentials are Wrong:
```
[DEBUG] mt5.initialize() succeeded
[DEBUG] Attempting login: account=19498321, server=Weltrade-Demo, use_demo=True
[DEBUG] mt5.login() FAILED with error: (some error code)
<- STOPS HERE - WRONG CREDENTIALS
[DEBUG] connector.initialize() returned False
[DEBUG] PainBot initialization FAILED
```

---

## How to Use Debug Prints

### 1. Run the Bot
```bash
python -m pain_gain_bot.main --bot pain --demo
```

### 2. Watch the [DEBUG] Messages
- They appear BEFORE the normal log messages
- Show exactly which function is running
- Show where it stopped

### 3. Find the Last [DEBUG] Message
**The last debug message shows where the code blocked.**

Example:
```
[DEBUG] Calling mt5.initialize()...
[DEBUG] mt5.initialize() FAILED with error: (-10005, 'IPC timeout')
```
= Problem: MT5 is not open

---

## Common Blocking Points

### Block Point 1: mt5.initialize()
```
[DEBUG] Calling mt5.initialize()...
[DEBUG] mt5.initialize() FAILED with error: (-10005, 'IPC timeout')
```
**Problem:** MetaTrader 5 application is not running
**Solution:** Open MT5 first

### Block Point 2: mt5.login()
```
[DEBUG] Attempting login: account=19498321...
[DEBUG] mt5.login() FAILED with error: (...)
```
**Problem:** Wrong credentials or account expired
**Solution:** Check account/password in config.json or create new demo account

### Block Point 3: Symbol Verification
```
[DEBUG] Calling connector.verify_symbols(['PainX400'])
(No "succeeded" message after)
```
**Problem:** Symbol not found or not visible
**Solution:** Add symbol to Market Watch in MT5

---

## Example: Finding Where It Blocked

**Scenario:** You run the bot and it stops.

**Step 1:** Look at console output

**Step 2:** Find the LAST `[DEBUG]` line

**Step 3:** Compare with expected flow:

**Expected:**
```
[DEBUG] main() started
[DEBUG] Creating PainBot instance...
[DEBUG] PainBot.__init__() completed
[DEBUG] Calling connector.initialize()...
[DEBUG] mt5.initialize() succeeded
[DEBUG] mt5.login() succeeded
[DEBUG] connector.initialize() succeeded
[DEBUG] PainBot initialized successfully
```

**Your Output:**
```
[DEBUG] main() started
[DEBUG] Creating PainBot instance...
[DEBUG] PainBot.__init__() completed
[DEBUG] Calling connector.initialize()...
[DEBUG] mt5.initialize() FAILED
```

**Conclusion:** Blocked at `mt5.initialize()` → MT5 is not open

---

## Removing Debug Prints Later

If you want clean output later, you can:

1. **Option 1:** Comment out the print lines
```python
# print("[DEBUG] some message")
```

2. **Option 2:** Add a debug flag in config
```python
if config.debug_mode:
    print("[DEBUG] some message")
```

3. **Option 3:** Leave them - they don't hurt and help troubleshooting

---

## Summary

**What Changed:**
- Added `print("[DEBUG] ...")` statements to key functions
- Shows execution flow step by step
- Helps identify where code blocks

**How to Read:**
- [DEBUG] messages = execution checkpoints
- Last [DEBUG] message = where it stopped
- Compare to expected flow to find problem

**Most Common Block:**
```
[DEBUG] mt5.initialize() FAILED with error: (-10005, 'IPC timeout')
```
= **Open MetaTrader 5 first!**

---

**Now run the bot again and watch the [DEBUG] messages to see exactly where it stops.**
