<#
.SYNOPSIS
    BankingAIPlatform Phase 20 Stage C — Windows Reboot Recovery Verification Script
.DESCRIPTION
    Verifies whether the BankingAIPlatform-Native-Startup Scheduled Task is registered,
    checks active backend/frontend PIDs, and runs Test-Native.ps1 after a Windows reboot.
#>
param(
    [string]$TaskName = "BankingAIPlatform-Native-Startup"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== BankingAIPlatform Windows Reboot Recovery Verification ===" -ForegroundColor Cyan

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if (-not $task) {
    Write-Warning "[BLOCKED] Scheduled Task '$TaskName' is NOT registered. Run Register-NativeRebootTask.ps1 in an elevated Administrator PowerShell prompt first."
    exit 2
}

Write-Host "[PASS] Scheduled Task '$TaskName' found (State: $($task.State))." -ForegroundColor Green
& "$scriptDir\Test-Native.ps1"
