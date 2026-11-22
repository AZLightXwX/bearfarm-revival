@echo off
rem BearFarm private server - detached launcher (called via WMI/schtasks)
cd /d "%~dp0server"
echo [%date% %time%] server starting >> "%~dp0server\server.log"
python main.py 8080 80 60000 8100 >> "%~dp0server\server.log" 2>&1
