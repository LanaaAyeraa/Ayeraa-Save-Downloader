@echo off
cd /d "%~dp0"
python -m pip install -q -r requirements.txt
if not exist assets\icon.ico python tools\make_icon.py
start "" pythonw main.py
