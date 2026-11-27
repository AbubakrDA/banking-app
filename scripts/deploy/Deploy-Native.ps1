<#
.SYNOPSIS
    BankingAIPlatform Native Windows Deployment Script (Docker-Free)
.DESCRIPTION
    Prepares Python backend and Node.js frontend production build without Docker:
      1. Runs pre-flight in NATIVE mode.
      2. Resolves Python interpreter (supports .venv or system Python under AppLocker).
      3. Installs pinned backend requirements (unless -SkipInstall).
      4. Builds production frontend bundle (frontend/dist).
      5. Runs Alembic database migrations if DATABASE_URL is configured.
#>
param(
    [switch]$SkipInstall,
    [switch]$SkipMigrations
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path "$scriptDir\..\.."

Write-Host "=== BankingAIPlatform Native Windows Deployment (Docker-Free) ===" -ForegroundColor Cyan

# 1. Pre-flight check in NATIVE mode
& "$scriptDir\Invoke-StagingPreflight.ps1" -Environment WINDOWS_LOCAL -Mode NATIVE
if ($LASTEXITCODE -ne 0) {
    Write-Error "Native pre-flight check failed."
}

# 2. Resolve Python Executable (AppLocker-safe)
$venvPython = "$repoRoot\backend\.venv\Scripts\python.exe"
$pythonExe = "python"
if (Test-Path $venvPython) {
    try {
        & $venvPython --version 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $venvPython
            Write-Host "[INFO] Using virtual environment Python: $pythonExe" -ForegroundColor Gray
        }
    } catch {
        Write-Warning "Virtualenv Python blocked by host policy; falling back to system Python."
    }
}

# 3. Backend Dependencies
if (-not $SkipInstall) {
    Write-Host "`n[Step 1/3] Installing pinned backend requirements..." -ForegroundColor Yellow
    & $pythonExe -m pip install -r "$repoRoot\backend\requirements.txt" --quiet
} else {
    Write-Host "`n[Step 1/3] Skipping pip install (-SkipInstall active)." -ForegroundColor Gray
}

# 4. Frontend Production Build
Write-Host "`n[Step 2/3] Building production frontend assets..." -ForegroundColor Yellow
Push-Location "$repoRoot\frontend"
if (-not $SkipInstall -and -not (Test-Path "node_modules")) {
    npm ci
}
npm run build
Pop-Location

# 5. Database Migrations (Alembic)
Write-Host "`n[Step 3/3] Checking Database Migrations..." -ForegroundColor Yellow
if ($SkipMigrations) {
    Write-Host "[SKIPPED] Alembic migrations skipped (-SkipMigrations active)." -ForegroundColor Gray
} elseif ([string]::IsNullOrWhiteSpace($env:DATABASE_URL)) {
    Write-Warning "DATABASE_URL is not set. Skipping 'alembic upgrade head'. Set DATABASE_URL to run migrations against PostgreSQL 16."
} else {
    Push-Location "$repoRoot\backend"
    & $pythonExe -m alembic upgrade head
    Pop-Location
}

Write-Host "`nNative Windows deployment artifacts built successfully." -ForegroundColor Green
