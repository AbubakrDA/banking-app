<#
.SYNOPSIS
    BankingAIPlatform Multi-Mode Pre-Flight & Environment Readiness Check
.DESCRIPTION
    Detects Docker, Python, Node.js, npm, Git, AWS CLI, Terraform, AWS identity,
    and required staging configuration without exposing secrets.
    Docker absence NEVER fails NATIVE or AWS_MANAGED modes.
#>
param(
    [ValidateSet("WINDOWS_LOCAL", "GITHUB_ACTIONS", "AWS_CLOUDSHELL")]
    [string]$Environment = $env:BANKING_AI_DEPLOY_ENV,

    [ValidateSet("NATIVE", "DOCKER", "AWS_MANAGED")]
    [string]$Mode = $env:BANKING_AI_DEPLOY_MODE
)

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "BANKING_AI_PLATFORM PHASE 18.2 - MULTI-MODE READINESS CHECK" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$selection = & "$scriptDir\Select-Environment.ps1" -Environment $Environment -Mode $Mode
$activeEnv = $selection.Environment
$activeMode = $selection.Mode

Write-Host "`n--- 1. Tooling & Runtime Detection ---" -ForegroundColor Yellow
$tools = @(
    @{ Name = "Git";       Cmd = "git";       Args = "--version"; RequiredIn = @("NATIVE", "DOCKER", "AWS_MANAGED") },
    @{ Name = "Python";    Cmd = "python";    Args = "--version"; RequiredIn = @("NATIVE", "DOCKER", "AWS_MANAGED") },
    @{ Name = "Node.js";   Cmd = "node";      Args = "--version"; RequiredIn = @("NATIVE", "DOCKER", "AWS_MANAGED") },
    @{ Name = "npm";       Cmd = "npm";       Args = "--version"; RequiredIn = @("NATIVE", "DOCKER", "AWS_MANAGED") },
    @{ Name = "Docker";    Cmd = "docker";    Args = "--version"; RequiredIn = @("DOCKER") },
    @{ Name = "AWS CLI";   Cmd = "aws";       Args = "--version"; RequiredIn = @("DOCKER", "AWS_MANAGED") },
    @{ Name = "Terraform"; Cmd = "terraform"; Args = "--version"; RequiredIn = @("DOCKER", "AWS_MANAGED") }
)

$missingRequired = @()
foreach ($t in $tools) {
    $isRequired = $t.RequiredIn -contains $activeMode
    $cmdPath = Get-Command $t.Cmd -ErrorAction SilentlyContinue
    if ($cmdPath) {
        $ver = & $t.Cmd $t.Args 2>&1 | Select-Object -First 1
        Write-Host "[PASS]     $($t.Name): $ver" -ForegroundColor Green
    } else {
        if ($isRequired) {
            Write-Host "[MISSING]  $($t.Name): Required for mode '$activeMode' (Not found on PATH)" -ForegroundColor Red
            $missingRequired += $t.Name
        } else {
            Write-Host "[OPTIONAL] $($t.Name): Not installed (Not required for mode '$activeMode')" -ForegroundColor Gray
        }
    }
}

Write-Host "`n--- 2. AWS Identity & Permissions Check ---" -ForegroundColor Yellow
if ($activeMode -eq "NATIVE") {
    Write-Host "[SKIPPED]  AWS STS check not required for local NATIVE mode." -ForegroundColor Gray
} elseif (Get-Command "aws" -ErrorAction SilentlyContinue) {
    $identity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[PASS]     AWS STS Caller Identity verified." -ForegroundColor Green
    } else {
        Write-Host "[BLOCKED]  AWS credentials not configured or expired." -ForegroundColor Red
        $missingRequired += "AWS Credentials"
    }
} else {
    Write-Host "[BLOCKED]  AWS CLI unavailable; cannot verify aws sts get-caller-identity." -ForegroundColor Red
}

Write-Host "`n--- 3. Required Configuration & Secrets (Values Redacted) ---" -ForegroundColor Yellow
$cloudVars = @("ENVIRONMENT", "DATABASE_URL", "REDIS_URL", "SECRET_KEY", "S3_BUCKET_NAME", "GEMINI_API_KEY", "ACM_CERTIFICATE_ARN", "STAGING_DOMAIN")
$unsetVars = @()
foreach ($v in $cloudVars) {
    $val = [Environment]::GetEnvironmentVariable($v)
    if (-not [string]::IsNullOrWhiteSpace($val)) {
        Write-Host "[SET]      $v (length=$($val.Length))" -ForegroundColor Green
    } else {
        if ($activeMode -eq "NATIVE") {
            Write-Host "[DEFAULT]  $v (Uses local .env / safe dev defaults in NATIVE mode)" -ForegroundColor Gray
        } else {
            Write-Host "[UNSET]    $v (Required in AWS Secrets Manager / staging .env)" -ForegroundColor Yellow
            $unsetVars += $v
        }
    }
}

Write-Host "`n======================================================================" -ForegroundColor Cyan
if ($missingRequired.Count -gt 0 -or ($activeMode -ne "NATIVE" -and $unsetVars.Count -gt 0)) {
    Write-Host "SUMMARY ($activeEnv + $activeMode): MissingRequired=$($missingRequired.Count), UnsetCloudVars=$($unsetVars.Count)" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "SUMMARY ($activeEnv + $activeMode): Environment is READY." -ForegroundColor Green
    exit 0
}
