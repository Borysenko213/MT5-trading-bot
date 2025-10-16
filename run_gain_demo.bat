@echo off
echo ========================================
echo GainBot - Demo Mode
echo ========================================
echo.
echo Starting GainBot (BUY strategy) in DEMO mode...
echo.
echo Press Ctrl+C to stop
echo.
pause

python -m pain_gain_bot.main --bot gain --demo

pause
