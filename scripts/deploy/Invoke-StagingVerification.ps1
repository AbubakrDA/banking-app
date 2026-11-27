<#
.SYNOPSIS
    BankingAIPlatform Stage F Live Operational Verification & Rollback Rehearsal
.DESCRIPTION
    Executes smoke tests against a live staging URL and supports rehearsing ECS task revision rollback.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$StagingBaseUrl,
    [string]$ClusterName = "banking-ai-platform-staging-cluster",
    [string]$ServiceName = "banking-ai-platform-staging-web",
    [string]$AwsRegion = "us-east-1",
    [switch]$RehearseRollback,
    [string]$PreviousTaskDefinitionArn
)

$ErrorActionPreference = "Stop"

Write-Host "=== BankingAIPlatform Stage F Live Operational Verification ===" -ForegroundColor Cyan
Write-Host "Target URL: $StagingBaseUrl"

# 1. Health Endpoint Check
Write-Host "`n[1/3] Checking /api/v1/health..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$StagingBaseUrl/api/v1/health" -Method Get -TimeoutSec 10
if ($health.status -eq "healthy" -or $health.data.status -eq "healthy") {
    Write-Host "[PASS] API Health endpoint returned healthy." -ForegroundColor Green
} else {
    Write-Error "[FAIL] Unexpected health response."
}

# 2. TLS & Security Headers Check
Write-Host "`n[2/3] Checking HTTPS & Security Headers..." -ForegroundColor Yellow
$resp = Invoke-WebRequest -Uri "$StagingBaseUrl/" -Method Head -TimeoutSec 10
$requiredHeaders = @("X-Content-Type-Options", "X-Frame-Options", "Content-Security-Policy")
foreach ($h in $requiredHeaders) {
    if ($resp.Headers[$h]) {
        Write-Host "[PASS] Header present: $h" -ForegroundColor Green
    } else {
        Write-Warning "[WARN] Security header missing: $h"
    }
}

# 3. Optional Rollback Rehearsal
if ($RehearseRollback) {
    if ([string]::IsNullOrWhiteSpace($PreviousTaskDefinitionArn)) {
        Write-Error "Provide -PreviousTaskDefinitionArn to rehearse ECS rollback."
    }
    Write-Host "`n[3/3] Rehearsing ECS Rollback to $PreviousTaskDefinitionArn..." -ForegroundColor Yellow
    aws ecs update-service --cluster $ClusterName --service $ServiceName --task-definition $PreviousTaskDefinitionArn --region $AwsRegion
    aws ecs wait services-stable --cluster $ClusterName --services $ServiceName --region $AwsRegion
    Write-Host "[PASS] Rollback rehearsal completed and service stabilized." -ForegroundColor Green
} else {
    Write-Host "`n[3/3] Rollback rehearsal skipped (pass -RehearseRollback to execute)." -ForegroundColor Gray
}
