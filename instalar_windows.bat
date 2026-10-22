@echo off
REM Instala las librerias del laboratorio (solo la primera vez).
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 (
  echo No se encontro Python. Instalalo desde python.org y marca "Add python.exe to PATH".
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Instalacion terminada. Ahora ejecuta iniciar_windows.bat
pause
