#Requires -Version 5.1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[1/5] Ensuring Python virtual environment exists..." -ForegroundColor Cyan
if (-not (Test-Path ".venv")) {
    py -3.12 -m venv .venv
}

$pythonExe = Join-Path ".venv" "Scripts\python.exe"
$pipExe = Join-Path ".venv" "Scripts\pip.exe"

Write-Host "[2/5] Upgrading pip..." -ForegroundColor Cyan
& $pythonExe -m pip install --upgrade pip

Write-Host "[3/5] Installing project dependencies..." -ForegroundColor Cyan
& $pipExe install -r requirements.txt

Write-Host "[4/6] Installing Playwright Chromium browser..." -ForegroundColor Cyan
& ".venv\Scripts\playwright.exe" install chromium

Write-Host "[5/6] Installing pre-commit hooks..." -ForegroundColor Cyan
& $pipExe install pre-commit
& ".venv\Scripts\pre-commit.exe" install

Write-Host "[6/6] Ensuring runtime directories exist..." -ForegroundColor Cyan
$runtimeDirs = @("data", "logs", "exports")
foreach ($dir in $runtimeDirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

Write-Host "Bootstrap complete." -ForegroundColor Green
Write-Host "Activate environment: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "Run API: .\.venv\Scripts\python.exe run.py" -ForegroundColor Yellow
Write-Host "Run CLI: .\.venv\Scripts\python.exe -m app.cli.main version" -ForegroundColor Yellow
