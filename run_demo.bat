@echo off
echo ========================================
echo Pain/Gain Trading System - Demo Mode
echo ========================================
echo.
echo Starting both PainBot and GainBot in DEMO mode...
echo.
echo Press Ctrl+C to stop the bots
echo.
pause

python -m pain_gain_bot.main --bot both --demo

pause
