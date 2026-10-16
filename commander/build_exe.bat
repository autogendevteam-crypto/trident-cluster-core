@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call setup.bat
".venv\Scripts\python.exe" -m pip install pyinstaller
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --onefile --windowed --name TRIDENT_Commander --collect-all customtkinter --hidden-import pystray._win32 main_app.py
if errorlevel 1 (
  echo ERRORE nella compilazione.
  pause
  exit /b 1
)
copy /Y config.json dist\config.json
echo.
echo Fatto: dist\TRIDENT_Commander.exe  (config.json accanto all'exe)
pause