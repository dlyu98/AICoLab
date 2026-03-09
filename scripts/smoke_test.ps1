$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv")) {
  Write-Host "[1/6] Creating Python virtual environment (.venv)..."
  python -m venv .venv
}

Write-Host "[2/6] Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "[3/6] Installing backend dependencies..."
pip install -r backend/requirements.txt

Write-Host "[4/6] Running tests..."
pytest -q

Write-Host "[5/6] Starting backend server for smoke checks..."
$uvicorn = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000" -PassThru
Start-Sleep -Seconds 2

try {
  Write-Host "[6/6] Checking endpoints..."
  Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET | ConvertTo-Json -Depth 5

  Get-Content examples/sample_request.json -Raw |
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/agent/respond" -Method POST -ContentType "application/json" |
    ConvertTo-Json -Depth 10

  Write-Host "`nSmoke test complete."
}
finally {
  if ($uvicorn -and !$uvicorn.HasExited) {
    Stop-Process -Id $uvicorn.Id -Force
  }
}
