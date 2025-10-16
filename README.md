# Pain/Gain Automated Trading System

**Version:** 1.0.0
**Platform:** MetaTrader 5
**Broker:** Weltrade
**Symbols:** PainX/GainX 400, 600, 800, 999

---

## 📋 Project Overview

Fully automated dual-bot trading system implementing the Pain/Gain strategy for synthetic indices. The system consists of two independent bots:

- **PainBot** - Executes SELL signals on PainX symbols
- **GainBot** - Executes BUY signals on GainX symbols

Both bots use sophisticated multi-timeframe analysis (D1 → H4 → H1 → M30/M15 → M5 → M1) with custom indicators including "snake", "shingle", "squid", and "purple line" for precise entry/exit timing.

---

## 🎯 Key Features

### Multi-Timeframe Strategy
- **D1 Analysis:** Wick direction determines daily bias
- **H4 Confirmation:** 50% Fibonacci retracement validation
- **H1 Structure:** Shingle (EMA) alignment check
- **M30/M15 Filter:** Snake color confirmation
- **M5/M1 Entry:** Purple line break-retest pattern

### Risk Management
- Daily loss limit ($40 USD default)
- Daily profit target ($100 USD default)
- Maximum consecutive orders (3)
- Spread and slippage controls
- Session-based trading windows
- 50% wick stop condition

### Order Management
- 5-minute minimum hold time
- Purple line gating for re-entries
- Automatic stop loss on purple line breaks
- Configurable lot sizing
- Magic number identification

### Logging & Alerts
- Detailed trade logs
- Error and connection monitoring
- Telegram notifications (optional)
- Email alerts (optional)
- Performance metrics tracking

---

## 📦 Installation

### 1. Prerequisites

- **Python 3.11+** installed
- **MetaTrader 5** terminal
- **Weltrade MT5** account (Demo or Live)
- Windows OS (MT5 requirement)

### 2. Install MetaTrader5 Python Package

```bash
cd C:\Users\Administrator\Documents\trading
pip install -r requirements_bot.txt
```

### 3. Configure Accounts

Edit `pain_gain_bot/config.py` or create `config.json`:

```json
{
  "broker": {
    "server": "Weltrade",
    "demo_account": 19498321,
    "demo_password": "YOUR_PASSWORD",
    "use_demo": true
  },
  "symbols": {
    "pain_symbols": ["PainX400", "PainX600", "PainX800", "PainX999"],
    "gain_symbols": ["GainX400", "GainX600", "GainX800", "GainX999"]
  },
  "risk": {
    "lot_size": 0.10,
    "daily_stop_usd": 40.0,
    "daily_target_usd": 100.0
  }
}
```

⚠️ **IMPORTANT:** Replace passwords with your actual credentials!

---

## 🚀 Usage

### Run Both Bots (Recommended)

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

### Use Custom Configuration

```bash
python -m pain_gain_bot.main --config my_config.json --bot both
```

### ⚠️ Live Trading (Real Money)

```bash
python -m pain_gain_bot.main --bot both --live
```

---

## 📊 Strategy Details

### PainBot (SELL Strategy)

1. **D1 Bias:** Previous day has small body with long **downward wick**
2. **Daily Stop:** Stop trading when current day fills 50% of that wick
3. **H4 Check:** Prior H4 candle covers ≥50% of M15 Fibonacci (high→low)
4. **H1 Filter:** Price below thick **red shingle**
5. **M30/M15:** Snake must be **RED** on both
6. **M1 Entry:**
   - Price below red snake
   - Break purple line downward
   - Retest purple line from below → **SELL**

### GainBot (BUY Strategy)

1. **D1 Bias:** Previous day has small body with long **upward wick**
2. **Daily Stop:** Stop trading when current day fills 50% of that wick
3. **H4 Check:** Prior H4 candle covers ≥50% of M15 Fibonacci (low→high)
4. **H1 Filter:** Price above thick **green shingle**
5. **M30/M15:** Snake must be **GREEN** on both
6. **M1 Entry:**
   - Price above green snake
   - Break purple line upward
   - Retest purple line from above → **BUY**

### Exit Rules

- **Take Profit:** Hold for 5 minutes, close at candle end
- **Re-entry:** Wait 1 more M5 candle, can enter at start of 3rd M5 candle
- **Stop Loss:** M5 purple line break against position
- **Daily Stop:** 50% of D1 wick filled OR daily loss limit hit

---

## 🗂️ Project Structure

```
pain_gain_bot/
├── __init__.py
├── config.py                 # Configuration management
├── main.py                   # Main controller
├── bots/
│   ├── __init__.py
│   ├── pain_bot.py          # PainBot (SELL)
│   └── gain_bot.py          # GainBot (BUY)
├── data/
│   ├── __init__.py
│   └── mt5_connector.py     # MT5 integration
├── indicators/
│   ├── __init__.py
│   └── technical.py         # Snake, shingle, squid, purple line
├── strategy/
│   ├── __init__.py
│   ├── signals.py           # Multi-timeframe signal engine
│   ├── order_manager.py     # Order execution & lifecycle
│   └── risk_manager.py      # Risk controls & limits
└── utils/
    ├── __init__.py
    └── logger.py            # Logging & alerts
```

---

## ⚙️ Configuration Parameters

### Broker Settings
- `server`: Broker server name
- `demo_account` / `live_account`: Account numbers
- `use_demo`: True for demo, False for live

### Risk Management
- `lot_size`: Position size (0.10 default)
- `daily_stop_usd`: Maximum daily loss
- `daily_target_usd`: Daily profit goal
- `max_consecutive_orders`: Order limit per symbol
- `max_spread_pips`: Maximum allowed spread
- `max_slippage_pips`: Maximum slippage tolerance

### Session Settings
- `session_start`: Trading start time (19:00 COL)
- `session_end`: Trading end time (06:00 COL)
- `daily_close_time`: D1 candle close (16:00 COL)

### Strategy Indicators
- `snake_fast_ema`: Fast EMA for snake (8)
- `snake_slow_ema`: Slow EMA for snake (21)
- `shingle_ema`: Shingle EMA period (50)
- `purple_line_ema`: Purple line EMA (34)
- `squid_period`: Squid indicator period (13)

---

## 📈 Monitoring & Logs

### Log Files (in `logs/` directory)

- `trading_YYYYMMDD.log` - All trading activity
- `errors_YYYYMMDD.log` - Errors only
- `trades_YYYYMMDD.log` - Trade executions

### Real-time Console Output

The bots display status every 20 iterations (~10 minutes):

```
============================================================
PainBot Status (Iteration 20)
============================================================
Balance: $500.00 | Daily P/L: $5.50 (1.10%)
Trades Today: 3 | Active Positions: 1
Daily Loss: $0.00 / $40.00 | Profit: $5.50 / $100.00
In Session: True | Halted: False
============================================================
```

---

## 🔧 Troubleshooting

### MT5 Connection Issues

1. Ensure MetaTrader 5 is installed and running
2. Verify account credentials in config
3. Check that symbols are visible in Market Watch
4. Confirm "Allow automated trading" in MT5 settings

### No Signals Generated

1. Check if within trading session hours
2. Verify daily bias is set (check D1 wick)
3. Ensure all timeframe confirmations align
4. Check if daily stop/target already reached

### Orders Not Executing

1. Verify lot size within symbol limits
2. Check spread is below max threshold
3. Ensure sufficient account balance
4. Confirm not exceeding consecutive order limit

---

## 📧 Support

**Included Support:** 30 days post-delivery
- Bug fixes
- Parameter tuning
- Installation help
- Backtesting assistance

**Response Time:** 24-48 business hours

**After Support Period:**
- Monthly: $200/month (10 hours)
- On-demand: $30/hour

---

## ⚠️ Disclaimer

**RISK WARNING:** Trading synthetic indices and forex involves substantial risk of loss. This software is provided for educational and research purposes. Always test thoroughly on demo accounts before live trading. Past performance does not guarantee future results. Only trade with capital you can afford to lose.

---

## 📝 License

Proprietary software developed for Leonel Rosso (Gestiones Latam).
All rights reserved.

**Developer:** Borysenko
**Version:** 1.0.0
**Date:** October 2025

---

## 🔄 Version History

### v1.0.0 (October 2025)
- Initial release
- PainBot and GainBot implementation
- Multi-timeframe signal engine
- Risk management system
- Order management with purple line gating
- Logging and alert system
- Configuration management
