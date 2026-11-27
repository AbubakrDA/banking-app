# Department & Role Access Requirements

| Role | Surface | Accounts / Balances / Transactions | Transfers / Cards | Customer Search | Risk / Approvals / Audit | Policies |
|---|---|---|---|---|---|---|
| `customer` | `customer` | Own only | Own only | Denied (`403`) | Denied (`403`) | Read `approved` only |
| `employee` | `staff` | All with written reason | List transfers with reason; cannot initiate | With written reason | Denied (`403`) | List & upload |
| `risk_officer` | `staff` | All with written reason | Read-only with reason; cannot move money | With written reason | Full read & alert triage | List |
| `admin` | `staff` | All with written reason | List with reason; cannot initiate | With written reason | Full read & approve (no self-approval) | List, upload, approve/reject |
| `hr` | `staff` | Denied (`403`) | Denied (`403`) | Denied (`403`) | Denied (`403`) | Read-only |
| `marketing` | `staff` | Denied (`403`) | Denied (`403`) | Denied (`403`) | Denied (`403`) | Read-only |

- Staff sessions default to `STAFF_IDLE_TIMEOUT_MINUTES=10` (shorter than customer `ACCESS_TOKEN_EXPIRE_MINUTES=60`).
