# Phase 14 Specification — Cloud Hosting & Deployment

**Objective:** Implement containerized cloud deployment and AWS reference architecture for BankingAIPlatform (Master Spec §8, §13): multi-stage hardened production Docker containers, Infrastructure as Code (Terraform) for AWS ECS Fargate, RDS PostgreSQL with pgvector, ElastiCache Redis, S3 private object storage, CloudFront CDN, Application Load Balancer with TLS termination, horizontal auto-scaling, and cloud infrastructure telemetry monitoring.

## 1. Scope
- **Hardened Multi-Stage Production Containerization (Spec §8.1, §13):**
  - Backend: `backend/Dockerfile` and `backend/Dockerfile.prod` using non-root runtime user (`banking-ai-platform`), production WSGI/ASGI worker configuration, minimal attack surface.
  - Frontend: `frontend/Dockerfile` and `frontend/nginx.conf` multi-stage build (Node 20 build stage -> Nginx Alpine unprivileged runtime stage) with gzip compression, security headers (CSP, HSTS, X-Frame-Options), and SPA fallback routing.
  - Production Compose: `docker-compose.prod.yml` with healthchecks, resource limits (`cpus`, `memory`), restart policies, and isolated bridge networks.
- **AWS Infrastructure as Code (Terraform) (Spec §8.2 - §8.7):**
  - High-availability VPC across multiple Availability Zones with public/private subnet segmentation.
  - AWS ECS Fargate cluster with web gateway and Celery background worker services.
  - Amazon RDS PostgreSQL 16 with pgvector extension, Multi-AZ deployment, and storage encryption.
  - Amazon ElastiCache Redis cluster for caching, rate-limiting, and task queues.
  - Amazon S3 private storage with server-side encryption (SSE-S3/KMS) and public access blocks.
  - Amazon CloudFront CDN with TLS 1.3, Origin Access Control (OAC), and custom domain routing.
  - Application Load Balancer (ALB) with HTTPS listener, ACM certificate integration, and path-based routing.
- **Horizontal Auto-Scaling & Resilience (Spec §8.11):**
  - Target tracking auto-scaling policies based on CPU utilization (> 70%) and request latency.
- **Cloud Infrastructure Telemetry & Management API (Spec §8.10):**
  - Unified infrastructure API endpoints (`/api/v1/infrastructure/services`, `/api/v1/infrastructure/metrics`, `/api/v1/infrastructure/scaling`) reporting container status, latency benchmarks, DB connection pools, Redis memory, and storage utilization.
  - Support for CloudInfrastructurePage telemetry display.
- **Strict Multi-Tenancy & Tenant Quotas (Spec §7, §9):**
  - Strict resource quota enforcement per tenant across storage and compute.

## 2. Acceptance Criteria
- [ ] Backend and frontend production Dockerfiles compile cleanly with multi-stage non-root designs.
- [ ] Production Compose file defines all microservices with healthchecks and resource limits.
- [ ] Terraform reference architecture defines complete AWS cloud stack (VPC, ECS, RDS, Redis, S3, CloudFront, ALB).
- [ ] Infrastructure telemetry API returns live operational status of all services.
- [ ] Multi-tenant storage quota and telemetry isolation are verified.
- [ ] 100% of automated unit and regression tests pass without errors.
