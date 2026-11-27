# BankingAIPlatform — AWS CloudShell Deployment Guide (Optional Runner)

This guide explains how to execute BankingAIPlatform staging provisioning and database verification from **AWS CloudShell** as an alternative to the primary `WINDOWS_LOCAL` environment.

---

## 1. Environment Selection
Explicitly set the environment identifier:
```bash
export BANKING_AI_DEPLOY_ENV=AWS_CLOUDSHELL
```

## 2. Verify AWS Identity & Available Tools
AWS CloudShell pre-installs `aws` CLI and `git`, **but does not guarantee Docker Engine or Terraform**.
```bash
aws sts get-caller-identity
git --version
python3 --version
which terraform || echo "Install Terraform binary locally in ~/bin"
which docker || echo "Docker unavailable in CloudShell; use AWS CodeBuild or GitHub Actions for image builds"
```

## 3. Reusing the Exact Same Terraform & Verification Artifacts
```bash
cd ~/BANKING_AI_PLATFORM/infrastructure/terraform
terraform init
terraform workspace select staging || terraform workspace new staging
terraform plan -var="environment=staging" -out=staging.tfplan
# Only after explicit cost & budget approval:
# terraform apply staging.tfplan
```
