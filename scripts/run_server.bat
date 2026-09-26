@echo off
setlocal
echo ==================================================================
echo  Starting JANA-GATISHAKTI / CIVIC-PULSE BRICS DPI Platform...
echo ==================================================================
set PYTHONIOENCODING=utf-8

py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
if %errorlevel% neq 0 (
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
)
pause
