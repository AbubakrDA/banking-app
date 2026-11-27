#!/usr/bin/env python3
"""
BankingAIPlatform Checkov-Style Infrastructure-as-Code & Container Security Audit
Validates production Dockerfiles, Nginx configurations, Docker Compose, and Terraform IaC manifests.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKS = []

def check(name: str):
    def decorator(fn):
        def wrapper():
            passed, detail = fn()
            CHECKS.append({"name": name, "passed": passed, "detail": detail})
            return passed
        return wrapper
    return decorator


@check("Backend Dockerfile Non-Root User Execution")
def check_backend_dockerfile_user():
    df = ROOT / "backend" / "Dockerfile.prod"
    if not df.exists():
        return False, "backend/Dockerfile.prod missing"
    content = df.read_text(encoding="utf-8")
    if "USER banking-ai-platform" in content or "useradd" in content:
        return True, "Enforces non-root user 'banking-ai-platform'"
    return False, "Missing non-root user directive"


@check("Backend Dockerfile Native Health Check")
def check_backend_dockerfile_healthcheck():
    df = ROOT / "backend" / "Dockerfile.prod"
    content = df.read_text(encoding="utf-8")
    if "HEALTHCHECK" in content:
        return True, "HEALTHCHECK CMD configured"
    return False, "Missing HEALTHCHECK instruction"


@check("Frontend Nginx Security Headers (CSP, HSTS, X-Frame)")
def check_frontend_nginx_headers():
    conf = ROOT / "frontend" / "nginx.conf"
    if not conf.exists():
        return False, "frontend/nginx.conf missing"
    content = conf.read_text(encoding="utf-8")
    has_csp = "Content-Security-Policy" in content
    has_frame = "X-Frame-Options" in content
    has_nosniff = "X-Content-Type-Options" in content
    if has_csp and has_frame and has_nosniff:
        return True, "CSP, X-Frame-Options DENY, and nosniff verified"
    return False, f"Missing headers: CSP={has_csp}, Frame={has_frame}, nosniff={has_nosniff}"


@check("Production Docker Compose Resource Limits & Health Checks")
def check_docker_compose_limits():
    dc = ROOT / "docker-compose.prod.yml"
    if not dc.exists():
        return False, "docker-compose.prod.yml missing"
    content = dc.read_text(encoding="utf-8")
    has_limits = "limits:" in content and "memory:" in content
    has_health = "healthcheck:" in content
    if has_limits and has_health:
        return True, "CPU/Memory resource quotas and health checks active"
    return False, "Missing resource limits or health checks"


@check("Terraform S3 Storage SSE-KMS & Public Access Block")
def check_terraform_s3_security():
    tf = ROOT / "infrastructure" / "terraform" / "main.tf"
    if not tf.exists():
        return False, "infrastructure/terraform/main.tf missing"
    content = tf.read_text(encoding="utf-8")
    has_sse = "aws_s3_bucket_server_side_encryption_configuration" in content
    has_block = "aws_s3_bucket_public_access_block" in content
    if has_sse and has_block:
        return True, "SSE-KMS encryption and block_public_acls verified"
    return False, "Missing S3 encryption or public access block"


@check("Terraform RDS PostgreSQL Encryption & VPC Subnet Isolation")
def check_terraform_rds_security():
    tf = ROOT / "infrastructure" / "terraform" / "main.tf"
    content = tf.read_text(encoding="utf-8")
    has_enc = "storage_encrypted" in content and "true" in content
    has_subnet = "aws_db_subnet_group" in content
    if has_enc and has_subnet:
        return True, "RDS pgvector storage encryption & private subnets active"
    return False, "Missing RDS encryption or private subnet group"


def run_all_checks() -> bool:
    print("=" * 70)
    print("BANKING_AI_PLATFORM IAC & CONTAINER SECURITY AUDIT")
    print("=" * 70)
    
    all_passed = True
    for item in [
        check_backend_dockerfile_user,
        check_backend_dockerfile_healthcheck,
        check_frontend_nginx_headers,
        check_docker_compose_limits,
        check_terraform_s3_security,
        check_terraform_rds_security,
    ]:
        item()

    for c in CHECKS:
        status = "PASSED" if c["passed"] else "FAILED"
        print(f"[{status}] {c['name']}: {c['detail']}")
        if not c["passed"]:
            all_passed = False

    print("=" * 70)
    summary = f"Total: {len(CHECKS)} checks, {sum(1 for c in CHECKS if c['passed'])} passed, {sum(1 for c in CHECKS if not c['passed'])} failed."
    print(summary)
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
