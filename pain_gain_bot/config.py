"""
Configuration module for Pain/Gain trading bots
Centralizes all configurable parameters
"""

from dataclasses import dataclass
from typing import List
from datetime import time

@dataclass
class BrokerConfig:
    """Weltrade MT5 broker configuration"""
    server: str = "Weltrade"
    demo_account: int = 19498321
    demo_password: str = "%6Qn4Er["
    live_account: int = 34279304
    live_password: str = "E6m%W#w9"
    leverage: int = 10000
    use_demo: bool = True  # Start with demo

@dataclass
class SymbolConfig:
    """Trading symbols configuration"""
    pain_symbols: List[str] = None
    gain_symbols: List[str] = None

    def __post_init__(self):
        if self.pain_symbols is None:
            self.pain_symbols = ["PainX400", "PainX600", "PainX800", "PainX999"]
        if self.gain_symbols is None:
            self.gain_symbols = ["GainX400", "GainX600", "GainX800", "GainX999"]

@dataclass
class RiskConfig:
    """Risk management parameters"""
    lot_size: float = 0.10
    daily_stop_usd: float = 40.0
    daily_target_usd: float = 100.0
    max_consecutive_orders: int = 3
    max_spread_pips: float = 2.0
    max_slippage_pips: float = 2.0
    trade_target_usd: float = 1.5  # Min target per trade
    trade_target_max_usd: float = 2.0
    min_lot: float = 0.01
    max_lot: float = 1.0

@dataclass
class SessionConfig:
    """Trading session configuration"""
    # Colombia timezone (COL = UTC-5)
    session_start: time = time(19, 0)  # 7:00 PM
    session_end: time = time(6, 0)     # 6:00 AM (next day)
    daily_close_time: time = time(16, 0)  # 4:00 PM - D1 candle close
    timezone_offset: int = -5  # Colombia UTC-5
    allow_extended_hours: bool = False  # Enable after backtesting

@dataclass
class StrategyConfig:
    """Strategy-specific parameters"""
    # Timeframes used: D1, H4, H1, M30, M15, M5, M1
    hold_minutes: int = 5  # Hold trade for 5 minutes
    wait_candles: int = 1  # Wait 1 more M5 candle after close
    # Total: 5 + 5 + at start of 3rd = ~10 minutes between entries

    # D1 wick analysis
    d1_wick_threshold: float = 0.5  # Stop when 50% of wick is filled
    small_body_ratio: float = 0.3  # Body < 30% of total candle range

    # H4 Fibonacci
    h4_fib_level: float = 0.5  # 50% retracement
    use_m15_for_fib: bool = True  # Use M15 for Fib points

    # Indicator periods (to be refined after template analysis)
    snake_fast_ema: int = 8
    snake_slow_ema: int = 21
    shingle_ema: int = 50
    purple_line_ema: int = 34  # Example - needs verification
    squid_period: int = 13  # Example - needs verification

    # News filter
    news_filter_enabled: bool = False  # Disabled per client request
    news_buffer_minutes: int = 30

@dataclass
class BacktestConfig:
    """Backtesting parameters"""
    initial_balance: float = 500.0
    commission_per_lot: float = 0.0  # Update based on broker
    start_date: str = "2024-01-01"
    end_date: str = "2025-10-14"
    export_format: str = "both"  # csv, excel, or both

@dataclass
class AlertConfig:
    """Logging and alerting configuration"""
    enable_telegram: bool = False
    telegram_token: str = ""
    telegram_chat_id: str = ""

    enable_email: bool = False
    email_from: str = ""
    email_to: str = ""
    email_smtp_server: str = ""
    email_smtp_port: int = 587

    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_to_file: bool = True
    log_to_console: bool = True

@dataclass
class Config:
    """Master configuration container"""
    broker: BrokerConfig = None
    symbols: SymbolConfig = None
    risk: RiskConfig = None
    session: SessionConfig = None
    strategy: StrategyConfig = None
    backtest: BacktestConfig = None
    alerts: AlertConfig = None

    def __post_init__(self):
        if self.broker is None:
            self.broker = BrokerConfig()
        if self.symbols is None:
            self.symbols = SymbolConfig()
        if self.risk is None:
            self.risk = RiskConfig()
        if self.session is None:
            self.session = SessionConfig()
        if self.strategy is None:
            self.strategy = StrategyConfig()
        if self.backtest is None:
            self.backtest = BacktestConfig()
        if self.alerts is None:
            self.alerts = AlertConfig()

# Global config instance
config = Config()

def save_config(filepath: str = "config.json"):
    """Save configuration to JSON file"""
    import json
    from dataclasses import asdict

    with open(filepath, 'w') as f:
        json.dump(asdict(config), f, indent=2, default=str)

def load_config(filepath: str = "config.json"):
    """Load configuration from JSON file"""
    import json
    global config

    print(f"[DEBUG] load_config() called with filepath: {filepath}")

    try:
        print(f"[DEBUG] Opening config file: {filepath}")
        with open(filepath, 'r') as f:
            data = json.load(f)

        print(f"[DEBUG] Config file loaded, keys: {list(data.keys())}")

        # Remove comment fields (keys starting with _)
        print("[DEBUG] Removing comment fields starting with '_'")
        data = {k: v for k, v in data.items() if not k.startswith('_')}

        # Remove _explanations and _note fields from nested dicts
        print("[DEBUG] Cleaning nested comment fields")
        for key in data:
            if isinstance(data[key], dict):
                data[key] = {k: v for k, v in data[key].items()
                            if not k.startswith('_')}

        # Process session times (convert string to time object)
        print("[DEBUG] Processing session times")
        session_data = data.get('session', {})
        if 'session_start' in session_data and isinstance(session_data['session_start'], str):
            h, m, s = map(int, session_data['session_start'].split(':'))
            session_data['session_start'] = time(h, m, s)
            print(f"[DEBUG] session_start converted: {session_data['session_start']}")
        if 'session_end' in session_data and isinstance(session_data['session_end'], str):
            h, m, s = map(int, session_data['session_end'].split(':'))
            session_data['session_end'] = time(h, m, s)
            print(f"[DEBUG] session_end converted: {session_data['session_end']}")
        if 'daily_close_time' in session_data and isinstance(session_data['daily_close_time'], str):
            h, m, s = map(int, session_data['daily_close_time'].split(':'))
            session_data['daily_close_time'] = time(h, m, s)
            print(f"[DEBUG] daily_close_time converted: {session_data['daily_close_time']}")

        print("[DEBUG] Creating Config object...")
        config = Config(
            broker=BrokerConfig(**data.get('broker', {})),
            symbols=SymbolConfig(**data.get('symbols', {})),
            risk=RiskConfig(**data.get('risk', {})),
            session=SessionConfig(**session_data),
            strategy=StrategyConfig(**data.get('strategy', {})),
            backtest=BacktestConfig(**data.get('backtest', {})),
            alerts=AlertConfig(**data.get('alerts', {}))
        )

        print(f"[OK] Configuration loaded from {filepath}")
        print(f"[DEBUG] Broker server: {config.broker.server}")
        print(f"[DEBUG] Demo account: {config.broker.demo_account}")
        print(f"[DEBUG] Pain symbols: {config.symbols.pain_symbols}")

    except FileNotFoundError:
        print(f"[DEBUG] FileNotFoundError: {filepath} not found")
        print(f"Config file {filepath} not found. Using defaults.")
    except Exception as e:
        print(f"[DEBUG] Exception during config load: {type(e).__name__}: {e}")
        print(f"Error loading config: {e}")
        print("Using default configuration.")

    print("[DEBUG] load_config() completed")
    return config
