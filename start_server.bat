@echo off
rem Detached server start (immune to shell cleanup)
cd /d "%~dp0server"
wmic process call create "cmd /c cd /d "%~dp0server" && python main.py 8080 80 60000 8100 >> "%~dp0server\server.log" 2>&1"
