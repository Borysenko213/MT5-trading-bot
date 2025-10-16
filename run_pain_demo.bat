@echo off
echo ========================================
echo PainBot - Demo Mode
echo ========================================
echo.
echo Starting PainBot (SELL strategy) in DEMO mode...
echo.
echo Press Ctrl+C to stop
echo.
pause

python -m pain_gain_bot.main --bot pain --demo

pause
