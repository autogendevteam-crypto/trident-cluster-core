@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Prima esecuzione: avvio il setup...
  call setup.bat
)
start "" ".venv\Scripts\pythonw.exe" main_app.py