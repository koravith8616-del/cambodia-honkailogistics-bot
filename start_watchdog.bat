@echo off
REM Cambodia Logistics Bot Auto-Restart Watchdog
cd /d "C:\Users\USER\.gemini\antigravity\scratch\cambodia-honkailogistics-bot"
set PYTHONIOENCODING=utf-8

:loop
echo [%date% %time%] Starting Cambodia Logistics Bot Daemon...
".venv\Scripts\python.exe" run_all.py
echo [%date% %time%] Process crashed or stopped. Restarting in 10 seconds...
timeout /t 10 /nobreak >nul
goto loop
