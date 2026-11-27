#!/usr/bin/env python3
"""
BankingAIPlatform Staging Pre-Flight Readiness Verification Tool
Executes read-only checks on required configuration parameters, artifacts, and manifests
prior to staging cloud provisioning. Never prints or exposes actual secret values.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_required_files() -> bool:
    required = [
        ROOT / "backend" / "Dockerfile.prod",
        ROOT / "frontend" / "Dockerfile.prod",
        ROOT / "frontend" / "nginx.conf",
        ROOT / "docker-compose.prod.yml",
        ROOT / "infrastructure" / "terraform" / "main.tf",
        ROOT / "infrastructure" / "terraform" / "variables.tf",
        ROOT / "infrastructure" / "terraform" / "outputs.tf",
        ROOT / "infrastructure" / "ecs" / "task-definition-web.json",
        ROOT / "infrastructure" / "ecs" / "task-definition-worker.json",
        ROOT / "engineering" / "compliance" / "sbom.json",
        ROOT / "docs" / "production_deployment.md",
        ROOT / "engineering" / "runbooks" / "disaster_recovery.md",
    ]
    all_ok = True
    for p in required:
        if p.exists():
            print(f"[PASS] Artifact present: {p.relative_to(ROOT)}")
        else:
            print(f"[FAIL] Missing required artifact: {p.relative_to(ROOT)}")
            all_ok = False
    return all_ok


def check_environment_variables() -> None:
    env_vars = [
        "ENVIRONMENT",
        "DATABASE_URL",
        "REDIS_URL",
        "SECRET_KEY",
        "S3_BUCKET_NAME",
        "GEMINI_API_KEY",
    ]
    print("\n--- Environment Variable Diagnostic (Values Redacted) ---")
    for var in env_vars:
        val = os.environ.get(var)
        if val:
            print(f"[SET]     {var} (length={len(val)})")
        else:
            print(f"[UNSET]   {var} (Required in AWS Secrets Manager / Staging .env)")


def main() -> int:
    print("=" * 70)
    print("BANKING_AI_PLATFORM STAGING PRE-FLIGHT READINESS CHECK")
    print("=" * 70)
    files_ok = check_environment_and_files = check_required_files()
    check_environment_variables()
    print("=" * 70)
    if files_ok:
        print("RESULT: Staging artifacts verified. Configure Secrets Manager prior to terraform apply.")
        return 0
    print("RESULT: One or more required artifacts are missing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
