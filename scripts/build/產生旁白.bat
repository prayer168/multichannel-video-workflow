@echo off
chcp 65001 >nul
cd /d "%~dp0"
python "%~dp0產生旁白.py" %*
echo.
pause
