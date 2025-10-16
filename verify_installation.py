"""
Installation Verification Script for Pain/Gain Trading System
Tests all components to ensure everything is working correctly
"""

import sys
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_test(name, status, details=""):
    """Print test result"""
    symbol = "[OK]" if status else "[FAIL]"
    print(f"{symbol} {name}")
    if details:
        print(f"    {details}")

def main():
    print("\n" + "=" * 70)
    print("  Pain/Gain Trading System - Installation Verification")
    print("=" * 70)

    all_pass = True

    # Test 1: Python Version
    print_header("1. Python Environment")
    python_version = sys.version_info
    version_ok = python_version.major == 3 and python_version.minor >= 11
    print_test("Python Version", version_ok,
               f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    all_pass = all_pass and version_ok

    # Test 2: Required Packages
    print_header("2. Required Packages")

    packages = {
        'MetaTrader5': 'MT5 API',
        'pandas': 'Data analysis',
        'numpy': 'Numerical computing',
        'requests': 'HTTP requests'
    }

    for package, description in packages.items():
        try:
            __import__(package)
            print_test(f"{package}", True, description)
        except ImportError:
            print_test(f"{package}", False, f"{description} - MISSING!")
            all_pass = False

    # Test 3: Project Structure
    print_header("3. Project Structure")

    required_dirs = [
        ('pain_gain_bot', 'Main package'),
        ('pain_gain_bot/bots', 'Bot modules'),
        ('pain_gain_bot/data', 'Data connectors'),
        ('pain_gain_bot/indicators', 'Technical indicators'),
        ('pain_gain_bot/strategy', 'Strategy modules'),
        ('pain_gain_bot/utils', 'Utility modules')
    ]

    for dir_path, description in required_dirs:
        exists = os.path.isdir(dir_path)
        print_test(f"{dir_path}/", exists, description)
        all_pass = all_pass and exists

    # Test 4: Core Modules Import
    print_header("4. Core Module Imports")

    modules = [
        ('pain_gain_bot.config', 'Configuration'),
        ('pain_gain_bot.bots.pain_bot', 'PainBot'),
        ('pain_gain_bot.bots.gain_bot', 'GainBot'),
        ('pain_gain_bot.data.mt5_connector', 'MT5 Connector'),
        ('pain_gain_bot.indicators.technical', 'Technical Indicators'),
        ('pain_gain_bot.strategy.signals', 'Signal Engine'),
        ('pain_gain_bot.strategy.order_manager', 'Order Manager'),
        ('pain_gain_bot.strategy.risk_manager', 'Risk Manager'),
        ('pain_gain_bot.utils.logger', 'Logger')
    ]

    for module_name, description in modules:
        try:
            __import__(module_name)
            print_test(module_name, True, description)
        except Exception as e:
            print_test(module_name, False, f"{description} - {str(e)}")
            all_pass = False

    # Test 5: Configuration System
    print_header("5. Configuration System")

    try:
        from pain_gain_bot.config import load_config
        config = load_config()
        print_test("Config Loading", True, f"Broker: {config.broker.server}")
        print_test("Demo Mode", config.broker.use_demo, "Safety first!")
        print_test("Pain Symbols", len(config.symbols.pain_symbols) > 0,
                   f"{len(config.symbols.pain_symbols)} symbols configured")
        print_test("Gain Symbols", len(config.symbols.gain_symbols) > 0,
                   f"{len(config.symbols.gain_symbols)} symbols configured")
    except Exception as e:
        print_test("Configuration", False, str(e))
        all_pass = False

    # Test 6: Documentation Files
    print_header("6. Documentation")

    docs = [
        ('README.md', 'Project overview'),
        ('INSTALLATION.md', 'Installation guide'),
        ('QUICK_START.md', 'Quick start guide'),
        ('TESTING_GUIDE.md', 'Testing procedures'),
        ('CONFIGURATION_GUIDE.md', 'Configuration guide'),
        ('config_example.json', 'Config example')
    ]

    for doc_file, description in docs:
        exists = os.path.isfile(doc_file)
        print_test(doc_file, exists, description)

    # Test 7: Utility Scripts
    print_header("7. Utility Scripts")

    scripts = [
        ('install_dependencies.bat', 'Dependency installer'),
        ('run_demo.bat', 'Demo launcher'),
        ('create_config.bat', 'Config creator'),
        ('verify_installation.py', 'This script')
    ]

    for script_file, description in scripts:
        exists = os.path.isfile(script_file)
        print_test(script_file, exists, description)

    # Final Summary
    print("\n" + "=" * 70)
    if all_pass:
        print("  [SUCCESS] All critical tests passed!")
        print("  Your Pain/Gain Trading System is ready to use.")
        print("\n  Next steps:")
        print("    1. Review config.json (add your passwords)")
        print("    2. Ensure MetaTrader 5 is installed and running")
        print("    3. Run: python -m pain_gain_bot.main --bot both --demo")
    else:
        print("  [WARNING] Some tests failed!")
        print("  Please fix the issues above before running the bot.")
        print("\n  Common fixes:")
        print("    - Missing packages: run install_dependencies.bat")
        print("    - Missing files: re-extract the project archive")
    print("=" * 70 + "\n")

    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
