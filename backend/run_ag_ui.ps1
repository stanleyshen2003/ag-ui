# Start the AG-UI server (ADK agent) and serve the HTML chat UI.
# Run from the backend directory. Usage: .\run_ag_ui.ps1
# Then open http://localhost:8080 for HTML UI, or use frontend at http://localhost:3000

$backendRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendRoot

Write-Host "Starting AG-UI server in a new window (port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendRoot'; uv run python main.py"
Start-Sleep -Seconds 4

Write-Host "Serving HTML UI at http://localhost:8080" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the web server (AG-UI server runs in the other window)." -ForegroundColor Yellow
uv run python -m http.server 8080 --directory web
