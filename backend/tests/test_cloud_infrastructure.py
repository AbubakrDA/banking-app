import os
import pytest
from httpx import AsyncClient
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_infrastructure_dashboard_telemetry(client: AsyncClient) -> None:
    token = create_access_token("admin_infra_01", "tenant_infra_01", "admin", "admin_infra1@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/infrastructure/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["overall_status"] == "Healthy"
    assert data["rpo_benchmark"] == "< 1 Hour"
    assert data["rto_benchmark"] == "< 4 Hours"
    assert "Verified Clean" in data["last_backup_status"]

    service_names = [s["name"] for s in data["services"]]
    assert "FastAPI Application Gateway" in service_names
    assert "PostgreSQL 16 + pgvector" in service_names
    assert "Redis 7 Cache & Broker" in service_names
    assert "Celery Background Task Workers" in service_names
    assert "MinIO / S3 Object Storage" in service_names
    assert "ClamAV Malware Quarantine Pipeline" in service_names

    # Check statuses
    for svc in data["services"]:
        assert svc["status"] in ["Healthy", "Active", "Scanning Ready"]
        assert len(svc["latency"]) > 0


@pytest.mark.asyncio
async def test_horizontal_auto_scaling_policy(client: AsyncClient) -> None:
    token = create_access_token("admin_infra_02", "tenant_infra_02", "admin", "admin_infra2@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/infrastructure/scaling", headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["min_capacity"] == 2
    assert data["max_capacity"] == 20
    assert data["target_cpu_utilization_pct"] == 70
    assert data["current_instances"] >= 2
    assert data["scaling_status"] == "STEADY"


@pytest.mark.asyncio
async def test_tenant_quota_usage_measurement(client: AsyncClient) -> None:
    token = create_access_token("admin_infra_03", "tenant_infra_03", "admin", "admin_infra3@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/infrastructure/quota", headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["tenant_id"] == "tenant_infra_03"
    assert data["storage_used_bytes"] > 0
    assert data["storage_limit_bytes"] > data["storage_used_bytes"]
    assert data["storage_used_percentage"] >= 0.0
    assert data["quota_status"] == "NORMAL"


def test_docker_and_terraform_manifest_files_exist_and_valid() -> None:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 1. Backend Dockerfile.prod
    backend_prod = os.path.join(root, "backend", "Dockerfile.prod")
    assert os.path.exists(backend_prod)
    with open(backend_prod, "r", encoding="utf-8") as f:
        backend_content = f.read()
    assert "FROM python:3.12-slim AS builder" in backend_content
    assert "USER banking-ai-platform" in backend_content
    assert "HEALTHCHECK" in backend_content

    # 2. Frontend Dockerfile.prod and Nginx conf
    frontend_prod = os.path.join(root, "frontend", "Dockerfile.prod")
    assert os.path.exists(frontend_prod)
    with open(frontend_prod, "r", encoding="utf-8") as f:
        frontend_content = f.read()
    assert "FROM node:20-alpine AS builder" in frontend_content
    assert "FROM nginx:1.27-alpine AS runner" in frontend_content

    nginx_conf = os.path.join(root, "frontend", "nginx.conf")
    assert os.path.exists(nginx_conf)
    with open(nginx_conf, "r", encoding="utf-8") as f:
        nginx_content = f.read()
    assert "X-Frame-Options" in nginx_content
    assert "try_files $uri $uri/ /index.html" in nginx_content

    # 3. Docker Compose Production
    compose_prod = os.path.join(root, "docker-compose.prod.yml")
    assert os.path.exists(compose_prod)
    with open(compose_prod, "r", encoding="utf-8") as f:
        compose_content = f.read()
    assert "banking-ai-platform-backend-prod" in compose_content
    assert "banking-ai-platform-frontend-prod" in compose_content
    assert "pgvector/pgvector:pg16" in compose_content

    # 4. Terraform manifests
    tf_main = os.path.join(root, "infrastructure", "terraform", "main.tf")
    assert os.path.exists(tf_main)
    with open(tf_main, "r", encoding="utf-8") as f:
        tf_content = f.read()
    assert "aws_ecs_cluster" in tf_content
    assert "aws_db_instance" in tf_content
    assert "aws_s3_bucket" in tf_content


@pytest.mark.asyncio
async def test_strict_multi_tenant_isolation_infrastructure(client: AsyncClient) -> None:
    token_a = create_access_token("admin_a", "tenant_infra_alpha", "admin", "alpha_infra@test.com")
    token_b = create_access_token("admin_b", "tenant_infra_beta", "admin", "beta_infra@test.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res_a = await client.get("/api/v1/infrastructure/quota", headers=headers_a)
    assert res_a.status_code == 200
    assert res_a.json()["data"]["tenant_id"] == "tenant_infra_alpha"

    res_b = await client.get("/api/v1/infrastructure/quota", headers=headers_b)
    assert res_b.status_code == 200
    assert res_b.json()["data"]["tenant_id"] == "tenant_infra_beta"
