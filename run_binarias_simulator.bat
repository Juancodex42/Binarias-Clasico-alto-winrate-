@echo off
title Binarias Simulator - Trading Simulator
cd /d "c:\Users\juanc\Desktop\prueba"
echo Starting Binarias Simulator Backend...
start cmd /c "python app.py"
echo Waiting for server to start...
timeout /t 3 /nobreak > nul
echo Opening interface in browser...
start "" "http://127.0.0.1:5001"
exit
