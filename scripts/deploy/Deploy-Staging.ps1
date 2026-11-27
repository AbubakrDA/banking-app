<#
.SYNOPSIS
    BankingAIPlatform Multi-Mode Deployment Orchestrator
.DESCRIPTION
    Supports three independent deployment modes across WINDOWS_LOCAL, GITHUB_ACTIONS, and AWS_CLOUDSHELL:
      - NATIVE      : Docker-free local execution (default for WINDOWS_LOCAL)
      - DOCKER      : Local Docker image build -> ECR -> ECS Fargate
      - AWS_MANAGED : Remote AWS CodeBuild image build -> ECR -> ECS Fargate (no local Docker required)
    Includes a mandatory -ConfirmProvisioning safety gate before creating paid AWS resources.
#>
param(
    [ValidateSet("WINDOWS_LOCAL", "GITHUB_ACTIONS", "AWS_CLOUDSHELL")]
    [string]$Environment = $env:BANKING_AI_DEPLOY_ENV,

    [ValidateSet("NATIVE", "DOCKER", "AWS_MANAGED")]
    [string]$Mode = $env:BANKING_AI_DEPLOY_MODE,

    [string]$AwsRegion = "us-east-1",
    [string]$Stage = "staging",
    [string]$ReleaseTag = "staging-$(Get-Date -Format 'yyyyMMdd-HHmmss')",
    [switch]$ConfirmProvisioning
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path "$scriptDir\..\.."

$selection = & "$scriptDir\Select-Environment.ps1" -Environment $Environment -Mode $Mode
$activeEnv = $selection.Environment
$activeMode = $selection.Mode

Write-Host "`n=== BankingAIPlatform Multi-Mode Deployment ($activeEnv + $activeMode) ===" -ForegroundColor Cyan

# Route NATIVE mode directly to Docker-free workflow
if ($activeMode -eq "NATIVE") {
    & "$scriptDir\Deploy-Native.ps1"
    exit $LASTEXITCODE
}

# Pre-flight check for DOCKER or AWS_MANAGED
Write-Host "`n[Step 1] Running Pre-Flight Checks for $activeMode..." -ForegroundColor Yellow
& "$scriptDir\Invoke-StagingPreflight.ps1" -Environment $activeEnv -Mode $activeMode
if ($LASTEXITCODE -ne 0) {
    Write-Error "Pre-flight check failed for mode '$activeMode'. Resolve missing tools or cloud configuration."
}

if (-not $ConfirmProvisioning) {
    Write-Warning "SAFETY GATE ACTIVE: -ConfirmProvisioning switch was NOT provided."
    Write-Host "No paid AWS resources will be provisioned. Running read-only Terraform validation only." -ForegroundColor Yellow
    Push-Location "$repoRoot\infrastructure\terraform"
    terraform init -backend=false
    terraform validate
    Pop-Location
    exit 0
}

Write-Host "`n[Step 2] Provisioning Shared Infrastructure via Terraform..." -ForegroundColor Yellow
Push-Location "$repoRoot\infrastructure\terraform"
terraform init
terraform workspace select $Stage 2>$null; if ($LASTEXITCODE -ne 0) { terraform workspace new $Stage }
terraform plan -var="environment=$Stage" -var="aws_region=$AwsRegion" -out="$Stage.tfplan"
terraform apply -auto-approve "$Stage.tfplan"
$ecrBackend = terraform output -raw ecr_backend_url
$ecrFrontend = terraform output -raw ecr_frontend_url
$ecsCluster = terraform output -raw ecs_cluster_name
Pop-Location

if ($activeMode -eq "DOCKER") {
    Write-Host "`n[Step 3] Building & Pushing Containers via Local Docker..." -ForegroundColor Yellow
    $accountId = (aws sts get-caller-identity --query Account --output text)
    aws ecr get-login-password --region $AwsRegion | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$AwsRegion.amazonaws.com"

    docker build -t "${ecrBackend}:${ReleaseTag}" -f "$repoRoot\backend\Dockerfile.prod" "$repoRoot\backend"
    docker push "${ecrBackend}:${ReleaseTag}"

    docker build -t "${ecrFrontend}:${ReleaseTag}" -f "$repoRoot\frontend\Dockerfile.prod" "$repoRoot\frontend"
    docker push "${ecrFrontend}:${ReleaseTag}"
} elseif ($activeMode -eq "AWS_MANAGED") {
    Write-Host "`n[Step 3] Triggering Remote AWS CodeBuild (Zero Local Docker Required)..." -ForegroundColor Yellow
    aws codebuild start-build --project-name "banking-ai-platform-$Stage-builder" --environment-variables-override "name=IMAGE_TAG,value=$ReleaseTag,type=PLAINTEXT" --region $AwsRegion
}

Write-Host "`n[Step 4] Updating ECS Fargate Services..." -ForegroundColor Yellow
aws ecs update-service --cluster $ecsCluster --service "banking-ai-platform-$Stage-web" --force-new-deployment --region $AwsRegion
aws ecs update-service --cluster $ecsCluster --service "banking-ai-platform-$Stage-worker" --force-new-deployment --region $AwsRegion

Write-Host "`nDeployment triggered successfully ($activeEnv + $activeMode, tag=$ReleaseTag)." -ForegroundColor Green
