<#
.SYNOPSIS
    Phase 18.3 Stage B Automated Native Windows Reliability Verification
.DESCRIPTION
    Tests:
      1. Initial startup & health/security-header smoke test
      2. Duplicate start / port conflict detection
      3. Unexpected process crash recovery via Watch-Native.ps1
      4. Graceful shutdown & PID file cleanup
#>
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path "$scriptDir\..\.."
$runDir = "$repoRoot\.run"

try {
    Write-Host "--- 1. Initial Startup & Smoke Test ---" -ForegroundColor Cyan
    & "$scriptDir\Start-Native.ps1"
    & "$scriptDir\Test-Native.ps1"

    Write-Host "`n--- 2. Duplicate Start / Port Conflict Check ---" -ForegroundColor Cyan
    $dupFailed = $false
    try {
        & "$scriptDir\Start-Native.ps1"
    } catch {
        $dupFailed = $true
        Write-Host "[PASS] Duplicate start / port conflict blocked: $($_.Exception.Message)" -ForegroundColor Green
    }
    if (-not $dupFailed) {
        throw "Expected duplicate start to fail!"
    }

    Write-Host "`n--- 3. Crash Recovery via Watch-Native.ps1 ---" -ForegroundColor Cyan
    $origPid = (Get-Content "$runDir\backend.pid" -Raw).Trim()
    Stop-Process -Id ([int]$origPid) -Force
    Write-Host "Simulated crash of backend PID: $origPid" -ForegroundColor Yellow

    & "$scriptDir\Watch-Native.ps1" -PollIntervalSeconds 1 -MaxDurationSeconds 4
    $newPid = (Get-Content "$runDir\backend.pid" -Raw).Trim()
    Write-Host "Recovered backend PID: $newPid" -ForegroundColor Green
    if ($newPid -eq $origPid) {
        throw "Backend PID did not change after crash recovery!"
    }
    & "$scriptDir\Test-Native.ps1"
} finally {
    Write-Host "`n--- 4. Graceful Shutdown & PID Cleanup ---" -ForegroundColor Cyan
    & "$scriptDir\Stop-Native.ps1"
    if ((Test-Path "$runDir\backend.pid") -or (Test-Path "$runDir\frontend.pid")) {
        throw "PID files were not cleaned up!"
    }
    Write-Host "[PASS] PID files cleaned up cleanly." -ForegroundColor Green
}
