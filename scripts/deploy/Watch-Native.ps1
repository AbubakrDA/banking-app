<#
.SYNOPSIS
    Windows-Native Process Supervisor for BankingAIPlatform
.DESCRIPTION
    Monitors backend and frontend PIDs and automatically restarts crashed processes
    after unexpected termination, unless .run/stop.flag is present.
#>
param(
    [int]$PollIntervalSeconds = 2,
    [int]$MaxDurationSeconds = 0,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 4173
)

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path "$scriptDir\..\.."
$runDir = "$repoRoot\.run"
$logFile = "$runDir\supervisor.log"
$startTime = Get-Date

function Write-SupLog {
    param([string]$Msg)
    $line = "$(Get-Date -Format 'o') $Msg"
    $line | Out-File -FilePath $logFile -Append -Encoding ascii
    Write-Host $line
}

Write-SupLog "[SUPERVISOR] Started monitoring BankingAIPlatform native processes."

while ($true) {
    if (Test-Path "$runDir\stop.flag") {
        Write-SupLog "[SUPERVISOR] Graceful stop flag detected. Exiting."
        break
    }

    if ($MaxDurationSeconds -gt 0 -and ((Get-Date) - $startTime).TotalSeconds -ge $MaxDurationSeconds) {
        Write-SupLog "[SUPERVISOR] MaxDurationSeconds ($MaxDurationSeconds) reached. Exiting."
        break
    }

    foreach ($svc in @("backend", "frontend")) {
        $pidFile = "$runDir\$svc.pid"
        if (Test-Path $pidFile) {
            $procId = (Get-Content $pidFile -Raw).Trim()
            $alive = $false
            if ($procId -match '^\d+$') {
                $alive = $null -ne (Get-Process -Id ([int]$procId) -ErrorAction SilentlyContinue)
            }
            if (-not $alive -and -not (Test-Path "$runDir\stop.flag")) {
                Write-SupLog "[RESTART] $svc (PID $procId) terminated unexpectedly. Restarting..."
                Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
                if ($svc -eq "backend") {
                    & "$scriptDir\Start-Native.ps1" -BackendPort $BackendPort -BackendOnly
                } else {
                    & "$scriptDir\Start-Native.ps1" -FrontendPort $FrontendPort -FrontendOnly
                }
            }
        }
    }

    Start-Sleep -Seconds $PollIntervalSeconds
}
