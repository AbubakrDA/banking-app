# Item 13 Plan & Evidence — Docker Hardening

## Plan
- Harden `docker-compose.yml`: bind dev ports to `127.0.0.1`, add healthchecks, `no-new-privileges:true`, and resource limits.
- Harden `docker-compose.prod.yml`: preserve `banking-ai-platform-backend-prod` service structure, remove host port exposure for `postgres`, `redis`, and `minio`, add non-root `user: "10001:10001"`, `read_only: true`, `no-new-privileges:true`, and resource limits.
- Validate YAML syntax and run `tests/test_cloud_infrastructure.py`.

## Evidence
- `python -c "import yaml; ..."` -> `COMPOSE_YAML_OK`
- `uv run pytest tests/test_cloud_infrastructure.py -v` -> `5 passed in 0.60s`
- `docker` CLI: `BLOCKED` (not installed on host).
- **Status:** `PARTIALLY VERIFIED` (YAML & manifest tests pass; live `docker compose up` `BLOCKED`).
