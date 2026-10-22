@echo off
REM Ejecuta las pruebas de validacion.
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
python -m pytest -v
pause
