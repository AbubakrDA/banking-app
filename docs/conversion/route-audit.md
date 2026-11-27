# API Route Audit (`/api/v1`)

Every `/api/v1` route (except the explicit public allowlist `/api/v1/health` and `/api/v1/auth/login`) declares both a surface (`require_surface`) and an allowed role set (`require_roles`). Legacy support-desk routers (`documents`, `knowledge`, `tools`, `enterprise`) were unmounted from `api_router`.

| Method | Path | Surface | Allowed Roles | Enforcing Dependencies |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | `public` | `none` | Public liveness probe |
| `POST` | `/api/v1/auth/login` | `public` | `none` | Public credential exchange |
| `GET` | `/api/v1/auth/me` | `both` | `customer, employee, risk_officer, admin, hr, marketing` | `require_surface("both")`, `require_roles(*BANKING_ROLES)` |
| `GET` | `/api/v1/auth/users` | `staff` | `admin` | `require_surface("staff")`, `require_roles("admin")` |
| `POST` | `/api/v1/auth/users` | `staff` | `admin` | `require_surface("staff")`, `require_roles("admin")` |
| `GET` | `/api/v1/tenants/current` | `staff` | `employee, risk_officer, admin` | `require_surface("staff")`, `require_roles("employee", "risk_officer", "admin")` |
| `GET` | `/api/v1/accounts` | `both` | `customer, employee, risk_officer, admin` | `require_surface("both")`, `require_roles(...)`, `get_staff_access_reason` |
| `GET` | `/api/v1/accounts/{account_id}` | `both` | `customer, employee, risk_officer, admin` | `require_surface("both")`, `require_roles(...)`, `get_staff_access_reason` |
| `GET` | `/api/v1/transactions` | `both` | `customer, employee, risk_officer, admin` | `require_surface("both")`, `require_roles(...)`, `get_staff_access_reason` |
| `GET` | `/api/v1/transfers` | `both` | `customer, employee, risk_officer, admin` | `require_surface("both")`, `require_roles(...)`, `get_staff_access_reason` |
| `POST` | `/api/v1/transfers` | `customer` | `customer` | `require_surface("customer")`, `require_roles("customer")` |
| `GET` | `/api/v1/cards` | `both` | `customer, employee, risk_officer, admin` | `require_surface("both")`, `require_roles(...)`, `get_staff_access_reason` |
| `PATCH` | `/api/v1/cards/{card_id}/status` | `customer` | `customer` | `require_surface("customer")`, `require_roles("customer")` |
| `GET` | `/api/v1/customers/me` | `customer` | `customer` | `require_surface("customer")`, `require_roles("customer")` |
| `GET` | `/api/v1/customers/search` | `staff` | `employee, risk_officer, admin` | `require_surface("staff")`, `require_roles(...)`, `get_staff_access_reason` |
| `GET` | `/api/v1/risk/alerts` | `staff` | `risk_officer, admin` | `require_surface("staff")`, `require_roles("risk_officer", "admin")` |
| `PATCH` | `/api/v1/risk/alerts/{alert_id}` | `staff` | `risk_officer, admin` | `require_surface("staff")`, `require_roles("risk_officer", "admin")` |
| `GET` | `/api/v1/risk/sanctions/status` | `staff` | `risk_officer, admin` | `require_surface("staff")`, `require_roles("risk_officer", "admin")` |
| `GET` | `/api/v1/approvals` | `staff` | `risk_officer, admin` | `require_surface("staff")`, `require_roles("risk_officer", "admin")` |
| `POST` | `/api/v1/approvals/{transfer_id}/approve` | `staff` | `admin` | `require_surface("staff")`, `require_roles("admin")` |
| `POST` | `/api/v1/approvals/{transfer_id}/reject` | `staff` | `admin` | `require_surface("staff")`, `require_roles("admin")` |
| `GET` | `/api/v1/policies` | `both` | `customer, employee, risk_officer, admin, hr, marketing` | `require_surface("both")`, `require_roles(...)` |
| `POST` | `/api/v1/policies` | `staff` | `employee, admin` | `require_surface("staff")`, `require_roles("employee", "admin")` |
| `POST` | `/api/v1/policies/{policy_id}/approve` | `staff` | `admin` | `require_surface("staff")`, `require_roles("admin")` |
| `POST` | `/api/v1/policies/{policy_id}/reject` | `staff` | `admin` | `require_surface("staff")`, `require_roles("admin")` |
| `GET` | `/api/v1/audit` | `staff` | `risk_officer, admin` | `require_surface("staff")`, `require_roles("risk_officer", "admin")` |
| `GET` | `/api/v1/audit/verify` | `staff` | `risk_officer, admin` | `require_surface("staff")`, `require_roles("risk_officer", "admin")` |
| `GET` | `/api/v1/admin/users` | `staff` | `admin` | `require_surface("staff")`, `require_roles("admin")` |
| `GET` | `/api/v1/admin/config` | `staff` | `admin` | `require_surface("staff")`, `require_roles("admin")` |
| `GET` | `/api/v1/integrations/status` | `staff` | `employee, risk_officer, admin` | `require_surface("staff")`, `require_roles("employee", "risk_officer", "admin")` |
| `POST` | `/api/v1/integrations/mobile-money/payout` | `both` | `customer, employee, admin` | `require_surface("both")`, `require_roles("customer", "employee", "admin")` |
| `POST` | `/api/v1/integrations/agent-network/cash-in` | `staff` | `employee, admin` | `require_surface("staff")`, `require_roles("employee", "admin")` |
| `POST` | `/api/v1/chat` | `both` | `customer, employee, risk_officer, admin, hr, marketing` | `require_surface("both")`, `require_roles(...)` |
