@echo off
cd /d "%~dp0"
echo Starting Translation GUI...
echo Directory: %CD%

:: Try Python
python -m src.ui.translation_gui
if %errorlevel% equ 0 goto end

:: Try Py Launcher
echo.
echo 'python' command failed. Attempting 'py'...
py -m src.ui.translation_gui
if %errorlevel% equ 0 goto end

:: Error Handling
echo.
echo ========================================================
echo ERROR: Could not launch the application.
echo Please ensure Python is installed and accessible.
echo ========================================================
pause
exit /b 1

:end
echo.
echo Application closed.
pause