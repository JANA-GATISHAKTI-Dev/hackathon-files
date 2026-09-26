# Launcher script for Jana-GatiShakti / Civic-Pulse DPI server
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Starting JANA-GATISHAKTI / CIVIC-PULSE BRICS DPI Platform... " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan

$env:PYTHONIOENCODING="utf-8"

# Search for python
$pythonPath = (Get-Command py, python, python3 -ErrorAction SilentlyContinue | Select-Object -First 1).Source
if (-not $pythonPath) {
    $pythonPath = "C:\Users\harir\AppData\Local\Python\pythoncore-3.14-64\python.exe"
}

Write-Host "Using Python Runtime: $pythonPath" -ForegroundColor Yellow
Write-Host "Opening Dashboard at http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to terminate server." -ForegroundColor Gray

& $pythonPath -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
