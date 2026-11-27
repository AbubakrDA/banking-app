<#
.SYNOPSIS
    Start BankingAIPlatform Native Production Processes with Port Check, PID Hygiene & Log Rotation
.DESCRIPTION
    Starts FastAPI backend using Uvicorn (no --reload) and serves production frontend/dist
    via serve_frontend.mjs. Enforces port conflict detection, stale PID cleanup, and 5MB log rotation.
#>
param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 4173,
    [string]$DatabaseUrl = $env:DATABASE_URL,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path "$scriptDir\..\.."
$runDir = "$repoRoot\.run"

if (-not (Test-Path $runDir)) {
    New-Item -ItemType Directory -Path $runDir | Out-Null
}

# Remove any prior stop flag on fresh start
Remove-Item "$runDir\stop.flag" -Force -ErrorAction SilentlyContinue

function Test-PortInUse {
    param([int]$Port)
    $listener = $null
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        return $false
    } catch {
        return $true
    } finally {
        if ($listener) { $listener.Stop() }
    }
}

function Invoke-LogRotation {
    param([string]$LogPath, [long]$MaxBytes = 5242880)
    if (Test-Path $LogPath) {
        $item = Get-Item $LogPath
        if ($item.Length -ge $MaxBytes) {
            $backup = "$LogPath.1"
            Move-Item -Path $LogPath -Destination $backup -Force
            Write-Host "[LOG] Rotated $LogPath -> $backup" -ForegroundColor Gray
        }
    }
}

function Clear-StalePid {
    param([string]$PidFile, [string]$Name)
    if (Test-Path $PidFile) {
        $oldPid = (Get-Content $PidFile -Raw).Trim()
        if ($oldPid -match '^\d+$') {
            $proc = Get-Process -Id ([int]$oldPid) -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Error "$Name is already running (PID $oldPid). Run Stop-Native.ps1 first."
            }
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        Write-Host "[CLEANUP] Removed stale PID file for $Name." -ForegroundColor Gray
    }
}

if (-not $FrontendOnly) {
    Clear-StalePid -PidFile "$runDir\backend.pid" -Name "backend"
    if (Test-PortInUse -Port $BackendPort) {
        Write-Error "Port conflict detected: Port $BackendPort is already in use."
    }
    Invoke-LogRotation -LogPath "$runDir\backend.out.log"
    Invoke-LogRotation -LogPath "$runDir\backend.err.log"

    if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
        $env:DATABASE_URL = "sqlite+aiosqlite:///$($repoRoot -replace '\\','/')/.run/native_local.db"
        Write-Warning "No DATABASE_URL set; using isolated local SQLite for native smoke startup."
    } else {
        $env:DATABASE_URL = $DatabaseUrl
    }

    $venvSite = "$repoRoot\backend\.venv\Lib\site-packages"
    $env:PYTHONPATH = "$repoRoot\backend"

    Write-Host "Starting BankingAIPlatform Backend (Uvicorn) on http://127.0.0.1:$BackendPort ..." -ForegroundColor Yellow
    $uvicornCmd = "import sys; sys.path.append(r'$venvSite'); import uvicorn; uvicorn.run('app.main:app', host='127.0.0.1', port=$BackendPort)"
    $backendProc = Start-Process -FilePath "python" `
        -ArgumentList "-c", "`"$uvicornCmd`"" `
        -WorkingDirectory "$repoRoot\backend" `
        -RedirectStandardOutput "$runDir\backend.out.log" `
        -RedirectStandardError "$runDir\backend.err.log" `
        -PassThru -WindowStyle Hidden

    $backendProc.Id | Out-File -FilePath "$runDir\backend.pid" -Encoding ascii
    Write-Host "[OK] Backend PID: $($backendProc.Id)" -ForegroundColor Green
}

if (-not $BackendOnly) {
    if (-not (Test-Path "$repoRoot\frontend\dist\index.html")) {
        Write-Error "frontend/dist/index.html not found. Run .\scripts\deploy\Deploy-Native.ps1 first."
    }
    Clear-StalePid -PidFile "$runDir\frontend.pid" -Name "frontend"
    if (Test-PortInUse -Port $FrontendPort) {
        Write-Error "Port conflict detected: Port $FrontendPort is already in use."
    }
    Invoke-LogRotation -LogPath "$runDir\frontend.out.log"
    Invoke-LogRotation -LogPath "$runDir\frontend.err.log"

    Write-Host "Starting BankingAIPlatform Production Frontend on http://127.0.0.1:$FrontendPort ..." -ForegroundColor Yellow
    $env:FRONTEND_PORT = "$FrontendPort"
    $frontendProc = Start-Process -FilePath "node" `
        -ArgumentList "$scriptDir\serve_frontend.mjs" `
        -WorkingDirectory "$repoRoot" `
        -RedirectStandardOutput "$runDir\frontend.out.log" `
        -RedirectStandardError "$runDir\frontend.err.log" `
        -PassThru -WindowStyle Hidden

    $frontendProc.Id | Out-File -FilePath "$runDir\frontend.pid" -Encoding ascii
    Write-Host "[OK] Frontend PID: $($frontendProc.Id)" -ForegroundColor Green
}
