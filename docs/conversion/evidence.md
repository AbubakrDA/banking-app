# Conversion Evidence — `AbubakrDA/banking-app`

## Step 0 Checks
```
1_PWD=D:\banking-app\banking-app
1_REMOTE=https://github.com/AbubakrDA/banking-app.git
2_BRANCH=main
3_HEAD=3948354 chore: fork ConversaIQ hardening branch into banking-ai-platform
4_BANKING_MD=True
5_STATUS: (clean)
```

## Phase A — Remove Support-Desk Product
- Removed `tickets`, `nlp`, `business_data`, `connectors`, `data_quality`, old support-desk tests, old frontend pages (`BusinessDataHubPage`, `ComplaintsTicketsPage`, `IntegrationsToolsPage`), and 28 old ConversaIQ `.md` reports.
- Added `backend/alembic/versions/015_drop_support_desk_tables.py`.
- Command: `python -m pytest tests/test_health.py tests/test_auth_security.py -v`
- Result: `10 passed in 0.72s`


## Phase B — Banking Domain
- Added `BankAccount`, `BankTransaction`, `BankTransfer`, `BankCard`, `RiskAlert`, `PolicyDocument`, `PolicyChunk` (`BigInteger` minor units).
- Added `backend/alembic/versions/016_banking_domain_tables.py` (`down_revision = '015_drop_support_desk_tables'`).
- Added `BankingAPI` protocol, `MockBankingAPI` (2 customers, 3 accounts, 2 cards, 10 transactions, 1 approved policy in dev/test only), and `BankingService` (ownership, staff reason + flagged audit, transfer validation, high-risk approval + `SELF_APPROVAL_FORBIDDEN`, card block/unblock, policy upload/review, allow/deny audit).
- Command: `python -m pytest tests/test_banking_domain.py -v`
- Result: `1 passed in 0.33s`
