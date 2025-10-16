@echo off
echo ========================================
echo Pain/Gain Bot - Configuration Setup
echo ========================================
echo.

:: Check if config.json already exists
if exist config.json (
    echo WARNING: config.json already exists!
    echo.
    choice /C YN /M "Do you want to overwrite it"
    if errorlevel 2 goto END
    echo.
)

:: Ask user which template to use
echo Select configuration template:
echo.
echo 1. Simple config (Recommended for beginners)
echo 2. Full config with detailed explanations
echo 3. Cancel
echo.
choice /C 123 /N /M "Enter your choice (1-3): "

if errorlevel 3 goto END
if errorlevel 2 goto FULL
if errorlevel 1 goto SIMPLE

:SIMPLE
echo.
echo Creating simple config from config_example.json...
copy config_example.json config.json >nul
echo.
echo ✓ config.json created successfully!
echo.
echo IMPORTANT: Edit config.json and add your passwords!
echo.
goto FINISH

:FULL
echo.
echo Creating detailed config from config_template.json...
copy config_template.json config.json >nul
echo.
echo ✓ config.json created successfully!
echo.
echo IMPORTANT: Edit config.json and add your passwords!
echo The template includes detailed explanations for each parameter.
echo.
goto FINISH

:FINISH
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Open config.json in a text editor
echo 2. Replace YOUR_PASSWORD_HERE with your actual passwords
echo 3. Adjust any other settings if needed
echo 4. Save the file
echo 5. Run: run_demo.bat
echo.
echo For help, read: CONFIGURATION_GUIDE.md
echo ========================================
pause
goto END

:END
