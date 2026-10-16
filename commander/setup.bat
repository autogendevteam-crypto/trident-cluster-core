@echo off
cd /d "%~dp0"
echo [TRIDENT Commander] Creo l'ambiente virtuale...
python -m venv .venv
if errorlevel 1 (
  echo ERRORE: Python 3.9+ non trovato nel PATH.
  pause
  exit /b 1
)
echo [TRIDENT Commander] Installo le dipendenze...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERRORE durante l'installazione delle dipendenze.
  pause
  exit /b 1
)
echo.
echo Setup completato. Avvia l'app con avvia.bat
pause