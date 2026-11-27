<#
.SYNOPSIS
    Verify Running Native Windows Production Deployment
.DESCRIPTION
    Probes backend /api/v1/health and frontend /healthz + security headers.
#>
param(
    [string]$BackendUrl = "http://127.0.0.1:8000",
    [string]$FrontendUrl = "http://127.0.0.1:4173"
)

$ErrorActionPreference = "Stop"

Write-Host "=== BankingAIPlatform Native Deployment Health & Smoke Test ===" -ForegroundColor Cyan

# 1. Wait & Check Backend Health
$backendOk = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $res = Invoke-RestMethod -Uri "$BackendUrl/api/v1/health" -Method Get -TimeoutSec 3
        if ($res.status -eq "healthy" -or $res.data.status -eq "healthy") {
            Write-Host "[PASS] Backend /api/v1/health -> healthy" -ForegroundColor Green
            $backendOk = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $backendOk) {
    Write-Error "[FAIL] Backend health check failed at $BackendUrl/api/v1/health"
}

# 2. Check Frontend Health & Security Headers
$feHealth = Invoke-WebRequest -Uri "$FrontendUrl/healthz" -Method Get -TimeoutSec 5 -UseBasicParsing
if ($feHealth.StatusCode -eq 200) {
    Write-Host "[PASS] Frontend /healthz -> 200 OK" -ForegroundColor Green
} else {
    Write-Error "[FAIL] Frontend /healthz returned $($feHealth.StatusCode)"
}

$feRoot = Invoke-WebRequest -Uri "$FrontendUrl/" -Method Get -TimeoutSec 5 -UseBasicParsing
foreach ($hdr in @("X-Content-Type-Options", "X-Frame-Options", "Content-Security-Policy")) {
    if ($feRoot.Headers[$hdr]) {
        Write-Host "[PASS] Security Header present: $hdr" -ForegroundColor Green
    } else {
        Write-Error "[FAIL] Missing security header: $hdr"
    }
}

Write-Host "`nAll Native Windows production smoke checks PASSED." -ForegroundColor Green
