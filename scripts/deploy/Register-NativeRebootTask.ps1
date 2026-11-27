<#
.SYNOPSIS
    Register Windows Scheduled Task for Reboot Recovery (Template)
.DESCRIPTION
    Registers a Windows Task Scheduler job to start BankingAIPlatform NATIVE processes on system startup.
    Requires Administrator privileges. Not executed automatically during non-destructive audits.
#>
param(
    [string]$TaskName = "BankingAIPlatform-Native-Startup"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startScript = "$scriptDir\Start-Native.ps1"

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$startScript`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Write-Host "Run the following command in an elevated Administrator PowerShell prompt to enable reboot recovery:" -ForegroundColor Cyan
Write-Host "Register-ScheduledTask -TaskName '$TaskName' -Action `$action -Trigger `$trigger -Settings `$settings -User 'SYSTEM' -RunLevel Highest" -ForegroundColor Yellow
