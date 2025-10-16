# Quick Start Guide - Pain/Gain Trading System

Fast-track guide to get up and running in 15 minutes.

---

## 🚀 5-Step Quick Start

### Step 1: Install Dependencies (2 minutes)

Double-click: `install_dependencies.bat`

Wait for installation to complete.

---

### Step 2: Configure Account (3 minutes)

Create a file named `config.json` in the trading folder:

```json
{
  "broker": {
    "server": "Weltrade",
    "demo_account": 19498321,
    "demo_password": "YOUR_PASSWORD_HERE",
    "use_demo": true
  }
}
```

⚠️ Replace `YOUR_PASSWORD_HERE` with your actual demo password!

---

### Step 3: Verify MT5 (2 minutes)

1. Open MetaTrader 5
2. Login to your demo account manually
3. Add symbols to Market Watch:
   - PainX400, 600, 800, 999
   - GainX400, 600, 800, 999
4. Enable automated trading:
   - Tools → Options → Expert Advisors
   - ✅ Allow automated trading

---

### Step 4: Run Demo Test (5 minutes)

Double-click: `run_demo.bat`

You should see:
```
============================================================
 Pain/Gain Automated Trading System v1.0
============================================================
✓ Connected to MT5 - Account: 19498321 (Demo)
✓ PainBot initialized successfully
✓ GainBot initialized successfully
🚀 Starting bots...
```

Let it run for 5 minutes, then press `Ctrl+C` to stop.

---

### Step 5: Check Logs (3 minutes)

Open the `logs` folder and check `trading_YYYYMMDD.log`

Look for:
- ✅ No connection errors
- ✅ Symbols verified
- ✅ Bots initialized

---

## ✅ You're Ready!

### Run Both Bots
```bash
python -m pain_gain_bot.main --bot both --demo
```

### Run PainBot Only
```bash
python -m pain_gain_bot.main --bot pain --demo
```

### Run GainBot Only
```bash
python -m pain_gain_bot.main --bot gain --demo
```

---

## 📊 What to Expect

### First Hour
- Bots will analyze markets
- May not place trades immediately (waiting for conditions)
- Console updates every ~10 minutes

### First Day
- Expect 0-5 trades (depending on market conditions)
- All trades will follow the multi-timeframe strategy
- Check logs for signal analysis

### First Week
- Should see consistent behavior
- Win/loss pattern will emerge
- Can start tuning parameters

---

## ⚙️ Quick Configuration Changes

### Change Lot Size
Edit `config.json`:
```json
"risk": {
  "lot_size": 0.05
}
```

### Change Daily Limits
```json
"risk": {
  "daily_stop_usd": 20.0,
  "daily_target_usd": 50.0
}
```

### Change Trading Hours
```json
"session": {
  "session_start": "18:00:00",
  "session_end": "07:00:00"
}
```

---

## 🔍 Monitoring Commands

### Check Current Status
Look at console output - updates every 20 iterations (~10 min)

### View Today's Trades
Open: `logs/trades_YYYYMMDD.log`

### Check for Errors
Open: `logs/errors_YYYYMMDD.log`

---

## 🛑 How to Stop

Press `Ctrl+C` in the command window

Bots will:
1. Close all open positions
2. Save final statistics
3. Disconnect from MT5
4. Exit gracefully

---

## ❓ Quick Troubleshooting

### "MT5 initialization failed"
→ Make sure MetaTrader 5 is running

### "Symbol not found"
→ Add symbols to Market Watch in MT5

### "Login failed"
→ Check password in config.json

### "No signals"
→ Normal! Wait for proper market conditions

---

## 📚 Need More Details?

- **Full Setup:** Read [INSTALLATION.md](INSTALLATION.md)
- **Strategy Details:** Read [README.md](README.md)
- **Testing:** Read [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **All Features:** Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 🎯 Recommended Testing Schedule

### Week 1: Demo Testing
- Run 8 hours/day minimum
- Monitor closely
- Review logs daily

### Week 2: Extended Demo
- Run 24/7 if possible
- Track all metrics
- Tune parameters

### Week 3+: Consider Live
- Only if demo successful
- Start with minimal risk
- Scale up gradually

---

## ⚠️ Important Reminders

1. **ALWAYS test on demo first** - No exceptions!
2. **Monitor daily** - Especially first 2 weeks
3. **Start small** - Increase lot size gradually
4. **Risk management** - Never risk more than you can afford to lose
5. **Be patient** - Strategy needs proper market conditions

---

## 🎉 Ready to Trade!

You now have a fully automated trading system.

**Next steps:**
1. ✅ Run on demo for 1-2 weeks
2. ✅ Analyze performance
3. ✅ Adjust parameters
4. ✅ When confident → consider live (with caution!)

**Good luck and happy trading!** 📈

---

**Developer:** Borysenko
**Support:** Available for 30 days post-delivery
**Version:** 1.0.0
