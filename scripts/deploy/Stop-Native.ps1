<#
.SYNOPSIS
    Stop BankingAIPlatform Native Production Processes Gracefully
#>
$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path "$scriptDir\..\.."
$runDir = "$repoRoot\.run"

if (Test-Path $runDir) {
    "stop" | Out-File -FilePath "$runDir\stop.flag" -Encoding ascii -Force
}

foreach ($svc in @("backend", "frontend")) {
    $pidFile = "$runDir\$svc.pid"
    if (Test-Path $pidFile) {
        $procId = (Get-Content $pidFile -Raw).Trim()
        if ($procId -match '^\d+$') {
            $proc = Get-Process -Id ([int]$procId) -ErrorAction SilentlyContinue
            if ($proc) {
                Stop-Process -Id ([int]$procId) -Force
                Write-Host "[STOPPED] $svc (PID $procId)" -ForegroundColor Green
            } else {
                Write-Host "[INFO] $svc (PID $procId) already exited." -ForegroundColor Gray
            }
        }
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "[INFO] No PID file found for $svc." -ForegroundColor Gray
    }
}
