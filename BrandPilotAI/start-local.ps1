$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .venv/Scripts/python.exe)) { py -3.12 -m venv .venv }
& ./.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw "Python setup failed" }
Push-Location frontend
npm ci --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
npm run build
if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
Pop-Location
Write-Host "Open http://127.0.0.1:8000"
& ./.venv/Scripts/python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
