@echo off
chcp 65001 >nul
cd /d "%~dp0"
python "%~dp0make_narration.py" %*
echo.
pause
