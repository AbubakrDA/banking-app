# Item 3 Plan & Route Audit — Consistent Role Enforcement (`require_roles`)

## Plan
- **Change:** Audit every API route, replace all ad-hoc `if current_user.role not in (...)` checks in `auth.py`, `backup.py`, `business_data.py`, and `enterprise.py` with `Depends(require_roles(...))`, add `require_roles` to `analytics.py`, `knowledge.py`, `memory.py`, `nlp.py`, `tickets.py`, `tools.py`, and `infrastructure.py`, and add a parametrized route-matrix RBAC test (`tests/test_rbac_route_matrix.py`).
- **Files:** `auth.py`, `backup.py`, `business_data.py`, `enterprise.py`, `analytics.py`, `knowledge.py`, `memory.py`, `nlp.py`, `tickets.py`, `tools.py`, `infrastructure.py`, `backend/tests/test_rbac_route_matrix.py`.
- **Tests:** Parametrized test across every mutating route and role (`owner`, `admin`, `agent`, `customer`).
- **Risk:** Low; preserves existing `admin`/`agent` test expectations while blocking `customer` / unprivileged escalation.

## Route Role Audit Table

| Route | Methods | Required Roles | Enforcement |
| :--- | :--- | :--- | :--- |
| `/api/v1/health`, `/api/v1/tenants/current`, `/api/v1/auth/login`, `/api/v1/auth/register` | GET / POST | Public / Unauthenticated | Open |
| `/api/v1/auth/users` | POST | `owner`, `admin` | `require_roles` |
| `/api/v1/business/mode` | PATCH | `owner`, `admin` | `require_roles` |
| `/api/v1/business/products`, `/services`, `/import/csv` | POST | `owner`, `admin`, `agent` | `require_roles` |
| `/api/v1/analytics/insights/generate`, `/acknowledge`, `/organizational-memory`, `/copilot/query`, `/reports/generate` | POST / PATCH | `owner`, `admin` | `require_roles` |
| `/api/v1/knowledge/collections`, `/documents`, `/documents/{id}` | POST / DELETE | `owner`, `admin`, `agent` | `require_roles` |
| `/api/v1/memory`, `/memory/{id}`, `/memory/customer/{id}/purge` | POST / DELETE | `owner`, `admin`, `agent` | `require_roles` |
| `/api/v1/nlp/questions`, `/clusters`, `/knowledge-gaps`, `/trends` | POST / GET | `owner`, `admin`, `agent` | `require_roles` |
| `/api/v1/tickets/{id}/assign`, `/notes`, `/feedback-request` | PATCH / POST | `owner`, `admin`, `agent` | `require_roles` |
| `/api/v1/tools` (read), `/executions`, `/mcp-servers` (read) | GET | `owner`, `admin`, `agent` | `require_roles` |
| `/api/v1/tools/executions/{id}/approve`, `/reject`, `/mcp-servers` (create) | POST | `owner`, `admin` | `require_roles` |
| `/api/v1/enterprise/branding` (PATCH), `/users/invite`, `/role`, `/security/revoke-session`, `/model-config` | POST / PATCH | `owner`, `admin` | `require_roles` |
| `/api/v1/infrastructure/*` | GET | `owner`, `admin` | `require_roles` |
| `/api/v1/backup/trigger`, `/drill`, `/retention-policy` (PUT), `/prune` | POST / PUT | `owner`, `admin` | `require_roles` |

## Execution & Evidence
- Replaced all ad-hoc `if current_user.role not in (...)` checks in `auth.py`, `backup.py`, `business_data.py`, and `enterprise.py` with `Depends(require_roles(...))`.
- Added `require_roles` dependencies to `analytics.py`, `knowledge.py`, `memory.py`, `nlp.py`, `tickets.py`, `tools.py`, and `infrastructure.py`.
- Added parametrized RBAC route matrix test (`tests/test_rbac_route_matrix.py`) covering 32 mutating routes × 4 roles + OpenAPI route registration check.

```
python -m pytest tests/test_rbac_route_matrix.py -q
........................................................................ [ 55%]
.........................................................                [100%]
129 passed in 2.37s
```
