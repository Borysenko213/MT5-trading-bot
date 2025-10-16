# Configuration Guide - Pain/Gain Trading System

Complete guide to configuring your trading bots using the centralized config file.

---

## 📋 Overview

All bot parameters are controlled through a single **config.json** file. No code editing required!

---

## 🚀 Quick Setup

### Step 1: Create Your Config File

Copy one of the provided templates:

```bash
# Option 1: Simple config (recommended for beginners)
copy config_example.json config.json

# Option 2: Full config with explanations
copy config_template.json config.json
```

### Step 2: Edit Your Passwords

Open `config.json` and replace:
```json
"demo_password": "YOUR_PASSWORD_HERE"
```

With your actual password:
```json
"demo_password": "%6Qn4Er["
```

### Step 3: Run the Bot

```bash
python -m pain_gain_bot.main --bot both --config config.json
```

**That's it!** All settings are loaded from your config file.

---

## 📂 Config File Location

Place `config.json` in the project root:
```
C:\Users\Administrator\Documents\trading\config.json
```

The bot will automatically look for it there.

---

## 🎛️ Configuration Sections

### 1. Broker Settings

```json
{
  "broker": {
    "server": "Weltrade",
    "demo_account": 19498321,
    "demo_password": "YOUR_PASSWORD",
    "live_account": 34279304,
    "live_password": "YOUR_PASSWORD",
    "leverage": 10000,
    "use_demo": true
  }
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `server` | string | Broker server name |
| `demo_account` | int | Demo account number |
| `demo_password` | string | Demo account password |
| `live_account` | int | Live account number |
| `live_password` | string | Live account password |
| `leverage` | int | Account leverage (1:10000) |
| `use_demo` | bool | true = demo, false = live ⚠️ |

⚠️ **IMPORTANT:** Always keep `use_demo: true` until fully tested!

---

### 2. Trading Symbols

```json
{
  "symbols": {
    "pain_symbols": [
      "PainX 400",
      "PainX 600",
      "PainX 800",
      "PainX 999"
    ],
    "gain_symbols": [
      "GainX 400",
      "GainX 600",
      "GainX 800",
      "GainX 999"
    ]
  }
}
```

**Customization Examples:**

Trade only PainX 400 and GainX 400:
```json
{
  "pain_symbols": ["PainX 400"],
  "gain_symbols": ["GainX 400"]
}
```

Trade only high-volatility symbols:
```json
{
  "pain_symbols": ["PainX 800", "PainX 999"],
  "gain_symbols": ["GainX 800", "GainX 999"]
}
```

---

### 3. Risk Management ⚠️ CRITICAL

```json
{
  "risk": {
    "lot_size": 0.10,
    "daily_stop_usd": 40.0,
    "daily_target_usd": 100.0,
    "max_consecutive_orders": 3,
    "max_spread_pips": 2.0,
    "max_slippage_pips": 2.0,
    "trade_target_usd": 1.5,
    "trade_target_max_usd": 2.0,
    "min_lot": 0.01,
    "max_lot": 1.0
  }
}
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `lot_size` | 0.10 | Position size per trade |
| `daily_stop_usd` | 40.0 | Max loss per day - **SAFETY LIMIT** |
| `daily_target_usd` | 100.0 | Profit goal per day |
| `max_consecutive_orders` | 3 | Max orders in a row per symbol |
| `max_spread_pips` | 2.0 | Max spread allowed |
| `max_slippage_pips` | 2.0 | Max slippage allowed |
| `trade_target_usd` | 1.5 | Min profit per trade |
| `trade_target_max_usd` | 2.0 | Max profit per trade |
| `min_lot` | 0.01 | Minimum lot size |
| `max_lot` | 1.0 | Maximum lot size |

#### Risk Presets

**Conservative (Low Risk):**
```json
{
  "lot_size": 0.01,
  "daily_stop_usd": 10.0,
  "daily_target_usd": 20.0,
  "max_consecutive_orders": 2
}
```

**Moderate (Default):**
```json
{
  "lot_size": 0.10,
  "daily_stop_usd": 40.0,
  "daily_target_usd": 100.0,
  "max_consecutive_orders": 3
}
```

**Aggressive (High Risk):**
```json
{
  "lot_size": 0.25,
  "daily_stop_usd": 100.0,
  "daily_target_usd": 300.0,
  "max_consecutive_orders": 5
}
```

---

### 4. Trading Session

```json
{
  "session": {
    "session_start": "19:00:00",
    "session_end": "06:00:00",
    "daily_close_time": "16:00:00",
    "timezone_offset": -5,
    "allow_extended_hours": false
  }
}
```

| Parameter | Format | Description |
|-----------|--------|-------------|
| `session_start` | "HH:MM:SS" | Trading start time (Colombia) |
| `session_end` | "HH:MM:SS" | Trading end time (Colombia) |
| `daily_close_time` | "HH:MM:SS" | D1 candle close time |
| `timezone_offset` | int | UTC offset (-5 for Colombia) |
| `allow_extended_hours` | bool | Trade outside session |

#### Session Presets

**Night Session (Default):**
```json
{
  "session_start": "19:00:00",
  "session_end": "06:00:00"
}
```

**Extended Night:**
```json
{
  "session_start": "18:00:00",
  "session_end": "08:00:00"
}
```

**Day Session:**
```json
{
  "session_start": "08:00:00",
  "session_end": "17:00:00"
}
```

**24/7 Trading:**
```json
{
  "session_start": "00:00:00",
  "session_end": "23:59:59"
}
```

---

### 5. Strategy Parameters

```json
{
  "strategy": {
    "hold_minutes": 5,
    "wait_candles": 1,
    "d1_wick_threshold": 0.5,
    "small_body_ratio": 0.3,
    "h4_fib_level": 0.5,
    "use_m15_for_fib": true,
    "snake_fast_ema": 8,
    "snake_slow_ema": 21,
    "shingle_ema": 50,
    "purple_line_ema": 34,
    "squid_period": 13,
    "news_filter_enabled": false,
    "news_buffer_minutes": 30
  }
}
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hold_minutes` | 5 | Min hold time per trade |
| `wait_candles` | 1 | M5 candles to wait before re-entry |
| `d1_wick_threshold` | 0.5 | 50% wick fill = stop |
| `small_body_ratio` | 0.3 | Max body ratio for bias |
| `h4_fib_level` | 0.5 | Fibonacci level (50%) |
| `use_m15_for_fib` | true | Use M15 for Fib swings |
| `snake_fast_ema` | 8 | Snake fast EMA period |
| `snake_slow_ema` | 21 | Snake slow EMA period |
| `shingle_ema` | 50 | Shingle EMA period |
| `purple_line_ema` | 34 | Purple line EMA period |
| `squid_period` | 13 | Squid indicator period |
| `news_filter_enabled` | false | Enable news filter |
| `news_buffer_minutes` | 30 | Minutes around news |

⚠️ **WARNING:** Changing indicator periods may significantly affect strategy performance. Test on demo first!

---

### 6. Backtesting Settings

```json
{
  "backtest": {
    "initial_balance": 500.0,
    "commission_per_lot": 0.0,
    "start_date": "2024-01-01",
    "end_date": "2025-10-14",
    "export_format": "both"
  }
}
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `initial_balance` | 500.0 | Starting balance |
| `commission_per_lot` | 0.0 | Commission per lot |
| `start_date` | "2024-01-01" | Backtest start |
| `end_date` | "2025-10-14" | Backtest end |
| `export_format` | "both" | csv, excel, or both |

---

### 7. Alerts & Notifications

```json
{
  "alerts": {
    "enable_telegram": false,
    "telegram_token": "",
    "telegram_chat_id": "",
    "enable_email": false,
    "email_from": "",
    "email_to": "",
    "email_smtp_server": "",
    "email_smtp_port": 587,
    "log_level": "INFO",
    "log_to_file": true,
    "log_to_console": true
  }
}
```

#### Enable Telegram Notifications

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get your chat ID with [@userinfobot](https://t.me/userinfobot)
3. Update config:

```json
{
  "enable_telegram": true,
  "telegram_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "telegram_chat_id": "123456789"
}
```

#### Enable Email Notifications

```json
{
  "enable_email": true,
  "email_from": "yourbot@gmail.com",
  "email_to": "youraddress@gmail.com",
  "email_smtp_server": "smtp.gmail.com",
  "email_smtp_port": 587
}
```

**Note:** For Gmail, you'll need an App Password (not your regular password).

#### Log Levels

- `"DEBUG"` - Everything (very detailed)
- `"INFO"` - Normal operations (recommended)
- `"WARNING"` - Important warnings only
- `"ERROR"` - Errors only

---

## 🎯 Common Configuration Scenarios

### Scenario 1: First Time Testing (Demo)

```json
{
  "broker": {
    "use_demo": true
  },
  "symbols": {
    "pain_symbols": ["PainX 400"],
    "gain_symbols": ["GainX 400"]
  },
  "risk": {
    "lot_size": 0.01,
    "daily_stop_usd": 5.0,
    "daily_target_usd": 10.0
  }
}
```

**Why:** Minimal risk, one symbol per bot, easy monitoring.

---

### Scenario 2: Standard Demo Testing

```json
{
  "broker": {
    "use_demo": true
  },
  "risk": {
    "lot_size": 0.10,
    "daily_stop_usd": 40.0,
    "daily_target_usd": 100.0
  }
}
```

**Why:** Full strategy as designed, safe demo testing.

---

### Scenario 3: Initial Live Trading (Cautious)

```json
{
  "broker": {
    "use_demo": false
  },
  "symbols": {
    "pain_symbols": ["PainX 400", "PainX 600"],
    "gain_symbols": ["GainX 400", "GainX 600"]
  },
  "risk": {
    "lot_size": 0.01,
    "daily_stop_usd": 10.0,
    "daily_target_usd": 25.0,
    "max_consecutive_orders": 2
  },
  "alerts": {
    "enable_telegram": true,
    "telegram_token": "YOUR_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID"
  }
}
```

**Why:** Real money but very low risk, 2 symbols, Telegram alerts enabled.

---

### Scenario 4: Full Production

```json
{
  "broker": {
    "use_demo": false
  },
  "risk": {
    "lot_size": 0.10,
    "daily_stop_usd": 40.0,
    "daily_target_usd": 100.0
  },
  "alerts": {
    "enable_telegram": true,
    "enable_email": true
  }
}
```

**Why:** Full strategy with all symbols, full alerts, proven on demo.

---

## 🔄 Loading Configuration

### Method 1: Automatic (Recommended)

Place `config.json` in project root. The bot will auto-load it.

```bash
python -m pain_gain_bot.main --bot both
```

### Method 2: Specify Path

```bash
python -m pain_gain_bot.main --bot both --config my_custom_config.json
```

### Method 3: Command-Line Override

```bash
python -m pain_gain_bot.main --bot both --demo  # Forces demo mode
python -m pain_gain_bot.main --bot both --live  # Forces live mode
```

---

## 💾 Saving Configuration

Generate a config file from current settings:

```bash
python -m pain_gain_bot.main --save-config
```

This creates `config.json` with current defaults.

---

## ✅ Configuration Validation

The bot will validate your config on startup and show:

```
✓ Configuration loaded from config.json
✓ Broker: Weltrade (Demo mode)
✓ Symbols: 4 Pain, 4 Gain
✓ Risk: Lot 0.10, Daily stop $40.00
✓ Session: 19:00 - 06:00 COL
```

If there are errors, you'll see warnings and defaults will be used.

---

## 🔧 Troubleshooting

### Config not loading

**Problem:** Bot uses defaults instead of config
**Solution:**
- Check file is named exactly `config.json`
- Check file is in correct directory
- Check JSON syntax (use [jsonlint.com](https://jsonlint.com))

### Invalid JSON format

**Problem:** "Error loading config: ..."
**Solution:**
- Ensure all strings are in quotes
- No trailing commas
- Proper bracket matching
- Use the template as reference

### Time format errors

**Problem:** Session times not working
**Solution:** Use format "HH:MM:SS" exactly
```json
"session_start": "19:00:00"  ✓ Correct
"session_start": "19:00"     ✗ Wrong
"session_start": "7:00 PM"   ✗ Wrong
```

---

## 📝 Best Practices

1. **Start with template** - Copy `config_example.json`
2. **Test on demo first** - Always!
3. **Keep backups** - Save working configs
4. **Document changes** - Note what you changed and why
5. **Version your configs** - Name them (config_v1.json, config_v2.json)
6. **Validate JSON** - Use online validator before running
7. **Start conservative** - Increase risk gradually

---

## 🎓 Advanced Tips

### Multiple Configurations

Create different configs for different scenarios:

```
config_demo.json          # Demo testing
config_live_conservative.json  # Live with low risk
config_live_full.json     # Live with full strategy
config_night_only.json    # Night trading only
config_single_symbol.json # One symbol testing
```

Switch between them:
```bash
python -m pain_gain_bot.main --config config_night_only.json
```

### Environment-Specific Configs

```
config.json              # Default (used if nothing specified)
config.demo.json         # Demo environment
config.live.json         # Live environment
```

### Version Control

If using Git:
```
# .gitignore
config.json           # Don't commit passwords!
config.*.json         # Don't commit any configs
```

Keep a template in version control:
```
config.example.json   # Safe to commit (no passwords)
```

---

## 📞 Need Help?

If you have questions about configuration:
1. Check the template comments
2. Review this guide
3. Test on demo first
4. Contact support during 30-day period

---

**Remember:** All parameters are optional. If not specified, sensible defaults are used!

**Happy Trading!** 🚀
