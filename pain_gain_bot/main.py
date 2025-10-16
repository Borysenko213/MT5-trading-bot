"""
Main controller for Pain/Gain Trading System
Can run PainBot, GainBot, or both simultaneously
"""

import argparse
import threading
import time
from .bots.pain_bot import PainBot
from .bots.gain_bot import GainBot
from .utils.logger import logger
from .config import config, load_config, save_config

def run_pain_bot():
    """Run PainBot in separate thread"""
    print("[DEBUG] Creating PainBot instance...")
    bot = PainBot()
    print("[DEBUG] PainBot instance created, calling initialize()...")
    if bot.initialize():
        print("[DEBUG] PainBot initialized successfully, calling run()...")
        bot.run()
    else:
        print("[DEBUG] PainBot initialization FAILED")

def run_gain_bot():
    """Run GainBot in separate thread"""
    bot = GainBot()
    if bot.initialize():
        bot.run()

def run_both_bots():
    """Run both bots in parallel"""
    logger.info("="*70)
    logger.info(" Pain/Gain Trading System - Dual Bot Mode")
    logger.info("="*70)

    # Create threads for each bot
    pain_thread = threading.Thread(target=run_pain_bot, name="PainBot-Thread")
    gain_thread = threading.Thread(target=run_gain_bot, name="GainBot-Thread")

    # Start both threads
    pain_thread.start()
    time.sleep(2)  # Stagger startup
    gain_thread.start()

    logger.info("[OK] Both bots started in parallel mode")

    # Wait for both to complete
    try:
        pain_thread.join()
        gain_thread.join()
    except KeyboardInterrupt:
        logger.info("\nShutting down both bots...")

def main():
    """Main entry point with CLI arguments"""
    print("[DEBUG] main() started")
    parser = argparse.ArgumentParser(
        description="Pain/Gain Trading Bot System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pain_gain_bot.main --bot pain          # Run PainBot only
  python -m pain_gain_bot.main --bot gain          # Run GainBot only
  python -m pain_gain_bot.main --bot both          # Run both bots
  python -m pain_gain_bot.main --config my.json    # Use custom config
        """
    )

    parser.add_argument(
        '--bot',
        choices=['pain', 'gain', 'both'],
        default='both',
        help='Which bot to run (default: both)'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration JSON file'
    )

    parser.add_argument(
        '--demo',
        action='store_true',
        help='Force demo account (overrides config)'
    )

    parser.add_argument(
        '--live',
        action='store_true',
        help='Use live account (WARNING: real money)'
    )

    parser.add_argument(
        '--save-config',
        action='store_true',
        help='Save current configuration to file and exit'
    )

    args = parser.parse_args()

    # Display banner
    print("\n" + "="*70)
    print(" Pain/Gain Automated Trading System v1.0")
    print(" MetaTrader 5 Integration for PainX/GainX Synthetic Indices")
    print("="*70 + "\n")

    # Load config - use specified file or default config.json
    config_file = args.config or "config.json"
    print(f"[DEBUG] Loading configuration from: {config_file}")
    logger.info(f"Loading configuration from: {config_file}")
    load_config(config_file)

    # Override demo/live setting
    if args.demo:
        config.broker.use_demo = True
        logger.warning("[!] DEMO MODE ENABLED")
    elif args.live:
        config.broker.use_demo = False
        logger.warning("[!][!][!] LIVE MODE ENABLED - REAL MONEY AT RISK [!][!][!]")
        response = input("Are you sure you want to trade with real money? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Live trading cancelled by user")
            return

    # Save config and exit if requested
    if args.save_config:
        config_file = args.config or "config.json"
        save_config(config_file)
        logger.info(f"Configuration saved to: {config_file}")
        return

    # Display configuration summary
    logger.info("\n" + "-"*70)
    logger.info("Configuration Summary:")
    logger.info(f"  Mode: {'DEMO' if config.broker.use_demo else 'LIVE'}")
    logger.info(f"  Broker: {config.broker.server}")
    logger.info(f"  Pain Symbols: {', '.join(config.symbols.pain_symbols)}")
    logger.info(f"  Gain Symbols: {', '.join(config.symbols.gain_symbols)}")
    logger.info(f"  Lot Size: {config.risk.lot_size}")
    logger.info(f"  Daily Stop: ${config.risk.daily_stop_usd}")
    logger.info(f"  Daily Target: ${config.risk.daily_target_usd}")
    logger.info(f"  Session: {config.session.session_start} - {config.session.session_end}")
    logger.info("-"*70 + "\n")

    # Run selected bot(s)
    print(f"[DEBUG] Selected bot mode: {args.bot}")
    if args.bot == 'pain':
        logger.info("Starting PainBot (SELL strategy)...")
        print("[DEBUG] Calling run_pain_bot()...")
        run_pain_bot()

    elif args.bot == 'gain':
        logger.info("Starting GainBot (BUY strategy)...")
        run_gain_bot()

    elif args.bot == 'both':
        logger.info("Starting both PainBot and GainBot...")
        run_both_bots()

if __name__ == "__main__":
    main()
