@echo off
echo ========================================
echo Installing Pain/Gain Bot Dependencies
echo ========================================
echo.
echo This will install all required Python packages...
echo.
pause

pip install --upgrade pip
pip install -r requirements_bot.txt

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run the bots using:
echo   - run_demo.bat (both bots)
echo   - run_pain_demo.bat (PainBot only)
echo   - run_gain_demo.bat (GainBot only)
echo.
pause
