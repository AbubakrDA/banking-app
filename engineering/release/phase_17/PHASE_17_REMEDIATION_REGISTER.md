# Phase 17 — Remediation Register & Action Plan

## 1. Overview & Prioritization Criteria
This register consolidates all identified operational, environmental, and infrastructure actions required prior to production cutover, classified into standard release tiers:
- **P0 (Must complete before production deployment):** Critical staging deployment and live infrastructure validation.
- **P1 (Must complete before General Availability / GA):** Distributed load testing, external provider credential binding, third-party penetration testing.
- **P2 (Recommended improvement post-GA):** Automation enhancements and private deployment tooling.
- **P3 (Future enhancement):** Architectural optimizations for global multi-region expansion.

---

## 2. Prioritized Action Register

| ID | Priority | Action Item | Reason / Risk | Required Evidence | Target Phase | Status |
| :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| **ACT-01** | **P0** | **Staging Cloud Provisioning via Terraform** | IaC manifests must be applied against an actual AWS staging VPC to verify security groups and subnets. | Successful `terraform apply` output in staging AWS account. | Stage F | `PENDING AUTH` |
| **ACT-02** | **P0** | **Live PostgreSQL 16 + pgvector Migration** | Validate that Alembic migrations `001_` through `011_` apply cleanly against a live RDS instance with native RLS. | Clean `alembic upgrade head` log on RDS instance. | Stage F | `PENDING AUTH` |
| **ACT-03** | **P0** | **Live RDS Snapshot Restore Verification** | Operational restoration from a true AWS RDS snapshot must be executed to verify real cloud RTO. | RDS snapshot restored and validated in staging account. | Stage F | `PENDING AUTH` |
| **ACT-04** | **P0** | **TLS / ACM Certificate Binding** | Bind production ACM certificate to ALB listener on port 443. | Valid HTTPS handshake on staging/prod domain with zero cert warnings. | Stage F | `PENDING AUTH` |
| **ACT-05** | **P1** | **Distributed Load Testing (500+ Virtual Users)** | Measure API Gateway and RDS performance under sustained multi-tenant traffic bursts using k6/Locust. | Load test report showing P95 latency < 250ms with 0% error rate. | Stage F | `PENDING AUTH` |
| **ACT-06** | **P1** | **Third-Party External API Credentials** | Configure live Google Sheets OAuth client credentials and WhatsApp Business Cloud API tokens. | End-to-end sync of real Google Sheet and real WhatsApp message delivery. | Stage F | `CONFIG REQ` |
| **ACT-07** | **P1** | **Independent External Penetration Testing** | Complement automated OWASP DAST/AI red-team testing with manual black-box penetration testing. | Attestation of clean report from independent security firm. | Post-Stage F | `PLANNED` |
| **ACT-08** | **P2** | **Dedicated Tenant Onboarding CLI Script** | Streamline provisioning of dedicated customer cloud environments via automated CLI wrapper. | Script `scripts/provision_dedicated_tenant.py` functional. | Post-GA | `FUTURE` |
| **ACT-09** | **P2** | **Helm Chart for Private On-Prem Deployments** | Provide Kubernetes manifests for enterprise customers hosting on-premises. | Verified Helm chart deploying all 6 services to Minikube/EKS. | Post-GA | `FUTURE` |
| **ACT-10** | **P3** | **Multi-Region Active-Active Replication** | Aurora Global Database or multi-region RDS read replicas for sub-second global failover. | Architecture spec and multi-region failover automation. | Future | `BACKLOG` |
