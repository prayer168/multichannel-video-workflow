@echo off
rem 以 PowerShell 執行 install_windows.ps1（視窗保留，方便看結果）
cd /d "%~dp0"
powershell -NoProfile -NoExit -ExecutionPolicy Bypass -File "%~dp0install_windows.ps1"
