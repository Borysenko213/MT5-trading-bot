"""
Logging and alerting system for Pain/Gain trading bots
Provides file logging, console output, and alert notifications
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import traceback

class TradingLogger:
    """Enhanced logger with trading-specific features"""

    def __init__(self, name: str = "PainGainBot", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # File handlers
        self._setup_file_handlers()

        # Console handler
        self._setup_console_handler()

    def _setup_file_handlers(self):
        """Set up file handlers for different log types"""
        # Main log file
        main_log = self.log_dir / f"trading_{datetime.now().strftime('%Y%m%d')}.log"
        main_handler = logging.FileHandler(main_log, encoding='utf-8')
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(main_handler)

        # Error log file
        error_log = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_log, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(error_handler)

        # Trade log file
        trade_log = self.log_dir / f"trades_{datetime.now().strftime('%Y%m%d')}.log"
        self.trade_handler = logging.FileHandler(trade_log, encoding='utf-8')
        self.trade_handler.setLevel(logging.INFO)
        self.trade_handler.setFormatter(self.detailed_formatter)

    def _setup_console_handler(self):
        """Set up console output handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.simple_formatter)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str, exception: Optional[Exception] = None):
        """Log error message with optional exception"""
        if exception:
            self.logger.error(f"{message}\n{traceback.format_exc()}")
        else:
            self.logger.error(message)

    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

    def trade(self, action: str, symbol: str, details: dict):
        """Log trade-specific event"""
        trade_msg = f"TRADE | {action} | {symbol} | {details}"
        self.logger.info(trade_msg)
        self.trade_handler.handle(self.logger.makeRecord(
            self.name, logging.INFO, "", 0, trade_msg, (), None
        ))

    def signal(self, signal_type: str, symbol: str, timeframe: str, details: dict):
        """Log trading signal"""
        signal_msg = f"SIGNAL | {signal_type} | {symbol} | {timeframe} | {details}"
        self.logger.info(signal_msg)

    def performance(self, metrics: dict):
        """Log performance metrics"""
        perf_msg = f"PERFORMANCE | {metrics}"
        self.logger.info(perf_msg)

    def connection(self, status: str, details: str = ""):
        """Log connection events"""
        conn_msg = f"CONNECTION | {status} | {details}"
        self.logger.info(conn_msg)

    def exception(self, message: str):
        """Log exception with full traceback"""
        self.logger.exception(message)


class AlertManager:
    """Manages alerts via Telegram and Email"""

    def __init__(self, config):
        self.config = config
        self.telegram_enabled = config.alerts.enable_telegram
        self.email_enabled = config.alerts.enable_email

    def send_alert(self, level: str, title: str, message: str):
        """Send alert via configured channels"""
        if level in ["ERROR", "CRITICAL"]:
            if self.telegram_enabled:
                self._send_telegram(f"[!]️ {title}\n{message}")
            if self.email_enabled:
                self._send_email(title, message)

    def _send_telegram(self, message: str):
        """Send Telegram notification"""
        try:
            import requests
            token = self.config.alerts.telegram_token
            chat_id = self.config.alerts.telegram_chat_id

            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            print(f"Telegram alert failed: {e}")

    def _send_email(self, subject: str, body: str):
        """Send email notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg['From'] = self.config.alerts.email_from
            msg['To'] = self.config.alerts.email_to
            msg['Subject'] = f"[PainGain Bot] {subject}"
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(
                self.config.alerts.email_smtp_server,
                self.config.alerts.email_smtp_port
            )
            server.starttls()
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Email alert failed: {e}")

    def notify_trade(self, action: str, symbol: str, price: float, lot: float):
        """Notify about trade execution"""
        message = f"Trade {action}\nSymbol: {symbol}\nPrice: {price}\nLot: {lot}"
        if self.telegram_enabled:
            emoji = "🟢" if action == "BUY" else "🔴"
            self._send_telegram(f"{emoji} {message}")

    def notify_daily_summary(self, pnl: float, trades: int, win_rate: float):
        """Send daily performance summary"""
        emoji = "[OK]" if pnl >= 0 else "[X]"
        message = (
            f"{emoji} Daily Summary\n"
            f"P/L: ${pnl:.2f}\n"
            f"Trades: {trades}\n"
            f"Win Rate: {win_rate:.1f}%"
        )
        if self.telegram_enabled:
            self._send_telegram(message)


# Global logger instance
logger = TradingLogger()
