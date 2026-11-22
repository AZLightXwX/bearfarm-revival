@echo off
rem 熊大农场私服 GUI 控制台启动器
cd /d "%~dp0server"
start "" http://127.0.0.1:8090
python gui.py
