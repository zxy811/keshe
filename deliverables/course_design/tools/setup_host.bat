@echo off
setlocal
cd /d "%~dp0\.."
py -3 -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
set "MPLCONFIGDIR=%CD%\results\mplconfig"
.venv\Scripts\python.exe tests\validate.py
if errorlevel 1 exit /b 1
echo PC setup complete. Run .venv\Scripts\python.exe tools\viewer.py
endlocal
