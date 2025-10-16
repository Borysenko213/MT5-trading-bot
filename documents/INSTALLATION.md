# Installation Guide - Pain/Gain Trading System

Complete step-by-step installation instructions for the Pain/Gain automated trading bots.

---

## System Requirements

### Operating System
- **Windows 10/11** (required for MetaTrader 5)

### Software
- **Python 3.11 or higher**
- **MetaTrader 5** terminal
- **Weltrade MT5** account

### Hardware (Recommended)
- **CPU:** Dual-core 2.0 GHz or better
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB free space
- **Internet:** Stable broadband connection

### Optional (For 24/7 Operation)
- **VPS:** Windows VPS with MT5 support
- Recommended: 2GB RAM, 20GB SSD, 99.9% uptime

---

## Step 1: Install Python

### 1.1 Download Python

Visit [python.org](https://www.python.org/downloads/) and download Python 3.11 or newer.

### 1.2 Install Python

1. Run the installer
2. ✅ **IMPORTANT:** Check "Add Python to PATH"
3. Click "Install Now"
4. Wait for installation to complete

### 1.3 Verify Installation

Open Command Prompt and run:

```bash
python --version
```

Should output: `Python 3.11.x`

```bash
pip --version
```

Should output pip version information.

---

## Step 2: Install MetaTrader 5

### 2.1 Download MT5

1. Visit [Weltrade website](https://weltrade.com)
2. Download MetaTrader 5 for Windows
3. Run installer and follow instructions

### 2.2 Configure MT5

1. Open MetaTrader 5
2. Go to **Tools → Options → Expert Advisors**
3. ✅ Enable "Allow automated trading"
4. ✅ Enable "Allow DLL imports"
5. Click OK

### 2.3 Login to Account

**IMPORTANT:** Log into MT5 BEFORE running the bot!

**Demo Account:**
- Server: **Weltrade-Demo** (note the "-Demo" suffix!)
- Login: **19498321**
- Password: **YOUR_PASSWORD**

**Live Account:**
- Server: **Weltrade**
- Login: **34279304**
- Password: **YOUR_PASSWORD**

**Steps:**
1. Open MT5
2. Right-click on the account in Navigator
3. Select "Login"
4. Verify you see a **green connection icon** in bottom-right corner

### 2.4 Add Symbols to Market Watch

1. Right-click in Market Watch
2. Select "Symbols"
3. Search for and add:
   - PainX 400, PainX 600, PainX 800, PainX 999
   - GainX 400, GainX 600, GainX 800, GainX 999

---

## Step 3: Install JannerTrading Custom Indicators

### 3.1 Locate Indicator Files

In the project folder, find:
```
JannerTrading-Caza-Spike-2024/
  Esto va en Indicators-JannerTrading/
    - JannerTrading1.ex5
    - JannerTrading2.ex5
    - JannerTrading3.ex5
    - JannerTrading4.ex5
    - JannerTrading5.ex5
```

### 3.2 Copy to MT5

1. In MT5, click **File → Open Data Folder**
2. Navigate to **MQL5 → Indicators**
3. Copy all 5 `.ex5` files here
4. Restart MetaTrader 5

### 3.3 Install Templates (Optional)

1. From project folder: `Esto va en Templates-JannerTrading/`
2. Copy all `.tpl` files
3. Paste into **MT5 Data Folder → templates**
4. Restart MT5

---

## Step 4: Install Trading Bot

### 4.1 Extract Project Files

Ensure your project structure looks like this:

```
C:\Users\Administrator\Documents\trading\
├── pain_gain_bot\           # Main bot package
├── requirements_bot.txt     # Python dependencies
├── README.md                # Documentation
└── INSTALLATION.md          # This file
```

### 4.2 Open Command Prompt in Project Folder

1. Navigate to trading folder:
```bash
cd C:\Users\Administrator\Documents\trading
```

### 4.3 Install Python Dependencies

```bash
pip install -r requirements_bot.txt
```

Wait for all packages to install. This may take 5-10 minutes.

### 4.4 Verify Installation

Check that MetaTrader5 package installed correctly:

```bash
python -c "import MetaTrader5 as mt5; print(mt5.__version__)"
```

Should print MT5 version number.

---

## Step 5: Configure the Bots

### 5.1 Option A: Edit config.py Directly

Open `pain_gain_bot/config.py` in a text editor and modify:

```python
@dataclass
class BrokerConfig:
    server: str = "Weltrade"
    demo_account: int = YOUR_DEMO_ACCOUNT
    demo_password: str = "YOUR_DEMO_PASSWORD"
    live_account: int = YOUR_LIVE_ACCOUNT
    live_password: str = "YOUR_LIVE_PASSWORD"
    use_demo: bool = True  # True for demo, False for live
```

### 5.2 Option B: Edit config.json (Recommended)

A `config.json` file should already exist in the trading folder. Edit it with your settings:

**Important notes:**
- ✅ The bot **automatically loads config.json** at startup
- ✅ Server name must match EXACTLY: `"Weltrade-Demo"` or `"Weltrade"`
- ✅ Symbol names must have spaces: `"PainX 400"` not `"PainX400"`
- ✅ For 24/7 testing, set session to `"00:00:00"` - `"23:59:59"`

**Key settings to customize:**

```json
{
  "broker": {
    "server": "Weltrade-Demo",        // ← Must match MT5 server name exactly!
    "demo_account": 19498321,
    "demo_password": "YOUR_PASSWORD",
    "use_demo": true
  },
  "symbols": {
    "pain_symbols": ["PainX 400"],    // ← Note the SPACE in symbol names!
    "gain_symbols": ["GainX 400"]
  },
  "risk": {
    "lot_size": 0.01,                 // ← Start small for testing
    "daily_stop_usd": 5.0,
    "daily_target_usd": 10.0,
    "max_spread_pips": 2.0,
    "max_slippage_pips": 2.0
  },
  "session": {
    "session_start": "00:00:00",      // ← 24/7 for testing
    "session_end": "23:59:59",
    "allow_extended_hours": true
  }
}
```

⚠️ **SECURITY:** Never commit passwords to version control!

---

## Step 6: Test Installation

### 6.1 Test MT5 Connection

```bash
python -c "import MetaTrader5 as mt5; mt5.initialize(); print('MT5 OK' if mt5.terminal_info() else 'MT5 FAILED')"
```

Should print: `MT5 OK`

### 6.2 Run First Test (Dry Run)

```bash
python -m pain_gain_bot.main --bot pain --demo
```

You should see:
```
==============================================
 Pain/Gain Automated Trading System v1.0
==============================================
✓ Connected to MT5 - Account: 19498321 (Demo)
✓ PainBot initialized successfully
🚀 PainBot starting...
```

Press `Ctrl+C` to stop.

---

## Step 7: Running the Bots

### 7.1 Demo Mode (Recommended for Testing)

**Run both bots:**
```bash
python -m pain_gain_bot.main --bot both --demo
```

**Run PainBot only:**
```bash
python -m pain_gain_bot.main --bot pain --demo
```

**Run GainBot only:**
```bash
python -m pain_gain_bot.main --bot gain --demo
```

### 7.2 Live Mode (Real Money - Use with Caution!)

```bash
python -m pain_gain_bot.main --bot both --live
```

⚠️ **WARNING:** This will trade with real money. Make sure you've thoroughly tested on demo first!

---

## Step 8: Monitor Operation

### 8.1 Check Logs

Logs are created in the `logs/` folder:

```
logs/
├── trading_20251014.log   # All activity
├── errors_20251014.log    # Errors only
└── trades_20251014.log    # Trade executions
```

### 8.2 Console Output

The bot displays status every ~10 minutes:

```
============================================================
PainBot Status (Iteration 20)
============================================================
Balance: $500.00 | Daily P/L: $5.50 (1.10%)
Trades Today: 3 | Active Positions: 1
...
```

### 8.3 Check MT5

Open MetaTrader 5 and check:
- **Terminal → Trade:** Open positions
- **Terminal → History:** Closed trades
- **Charts:** Visual representation

---

## Step 9: Optional Configurations

### 9.1 Enable Telegram Alerts

1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your bot token and chat ID
3. Edit `config.json`:

```json
"alerts": {
  "enable_telegram": true,
  "telegram_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID"
}
```

### 9.2 Run on VPS for 24/7 Operation

1. Rent Windows VPS (recommended: Vultr, DigitalOcean, AWS)
2. Install Python, MT5, and bot as described above
3. Use Task Scheduler or nssm to run as Windows service

### 9.3 Customize Risk Parameters

Edit `config.json` to adjust:
- `lot_size`: Position size
- `daily_stop_usd`: Maximum daily loss
- `daily_target_usd`: Daily profit goal
- `max_consecutive_orders`: Trade frequency limit

---

## Troubleshooting

### Issue: "MT5 initialization failed"

**Solutions:**
1. Ensure MetaTrader 5 is running
2. Check account credentials
3. Verify "Allow automated trading" is enabled
4. Try logging into MT5 manually first

### Issue: "Symbol not found"

**Solutions:**
1. Add symbols to Market Watch in MT5
2. Verify symbol names match exactly (case-sensitive)
3. Check broker provides these symbols

### Issue: "pip install fails"

**Solutions:**
1. Run Command Prompt as Administrator
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Install packages one by one
4. Check internet connection

### Issue: "No signals generated"

**Solutions:**
1. Wait for proper market conditions
2. Check if within trading session hours
3. Verify all timeframes have data
4. Review log files for errors

---

## Next Steps

1. ✅ Test thoroughly on demo account for at least 1-2 weeks
2. ✅ Monitor performance and adjust parameters
3. ✅ Review logs daily
4. ✅ Only switch to live after consistent demo results
5. ✅ Start with minimum lot size on live

---

## Support

For technical support during the 30-day period:
- Email: [Contact developer]
- Response time: 24-48 business hours

---

## Important Reminders

⚠️ **NEVER** share your account passwords publicly
⚠️ **ALWAYS** test on demo before live trading
⚠️ **ONLY** trade with money you can afford to lose
⚠️ **MONITOR** the bot regularly - automation ≠ guaranteed profit

---

**Installation Complete!** 🎉

You're now ready to run the Pain/Gain trading system. Start with demo mode and gradually transition to live trading once you're confident in the system's performance.
