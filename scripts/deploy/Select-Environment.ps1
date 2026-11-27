<#
.SYNOPSIS
    BankingAIPlatform Deployment Environment & Mode Selector
.DESCRIPTION
    Independently selects and validates:
      - Execution Environment: WINDOWS_LOCAL (default), GITHUB_ACTIONS, AWS_CLOUDSHELL
      - Deployment Mode: NATIVE (default for WINDOWS_LOCAL), DOCKER, AWS_MANAGED
    Never silently changes the explicitly selected mode.
#>
param(
    [ValidateSet("WINDOWS_LOCAL", "GITHUB_ACTIONS", "AWS_CLOUDSHELL")]
    [string]$Environment = $env:BANKING_AI_DEPLOY_ENV,

    [ValidateSet("NATIVE", "DOCKER", "AWS_MANAGED")]
    [string]$Mode = $env:BANKING_AI_DEPLOY_MODE
)

# 1. Resolve Execution Environment
if ([string]::IsNullOrWhiteSpace($Environment)) {
    if ($env:GITHUB_ACTIONS -eq "true") {
        $Environment = "GITHUB_ACTIONS"
    } elseif ($env:AWS_EXECUTION_ENV -like "*CloudShell*") {
        $Environment = "AWS_CLOUDSHELL"
    } else {
        $Environment = "WINDOWS_LOCAL"
    }
}

$prevEnv = $env:BANKING_AI_DEPLOY_ENV
if ($prevEnv -and $prevEnv -ne $Environment) {
    Write-Warning "Execution Environment switched from '$prevEnv' to '$Environment'."
}

# 2. Resolve Deployment Mode (default NATIVE for WINDOWS_LOCAL, AWS_MANAGED for CloudShell, DOCKER for GitHub Actions)
if ([string]::IsNullOrWhiteSpace($Mode)) {
    if ($Environment -eq "GITHUB_ACTIONS") {
        $Mode = "DOCKER"
    } elseif ($Environment -eq "AWS_CLOUDSHELL") {
        $Mode = "AWS_MANAGED"
    } else {
        $Mode = "NATIVE"
    }
}

$prevMode = $env:BANKING_AI_DEPLOY_MODE
if ($prevMode -and $prevMode -ne $Mode) {
    Write-Warning "Deployment Mode switched from '$prevMode' to '$Mode'."
}

$env:BANKING_AI_DEPLOY_ENV = $Environment
$env:BANKING_AI_DEPLOY_MODE = $Mode

Write-Host "Active BankingAIPlatform Execution Environment : $Environment" -ForegroundColor Cyan
Write-Host "Active BankingAIPlatform Deployment Mode       : $Mode" -ForegroundColor Cyan

return @{
    Environment = $Environment
    Mode        = $Mode
}
