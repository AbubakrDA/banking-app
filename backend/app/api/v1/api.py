from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    tenants,
    auth,
    accounts,
    transactions,
    transfers,
    cards,
    customers,
    risk,
    approvals,
    policies,
    audit,
    admin,
    integrations,
    chat,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth & RBAC"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Banking Accounts"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Banking Transactions"])
api_router.include_router(transfers.router, prefix="/transfers", tags=["Banking Transfers"])
api_router.include_router(cards.router, prefix="/cards", tags=["Banking Cards"])
api_router.include_router(customers.router, prefix="/customers", tags=["Banking Customers"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk & Alerts"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["Human Approvals"])
api_router.include_router(policies.router, prefix="/policies", tags=["Bank Policies & RAG"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Log"])
api_router.include_router(admin.router, prefix="/admin", tags=["Banking Admin"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Bank-Selectable Integrations"])
api_router.include_router(chat.router, prefix="/chat", tags=["Bilingual Banking Chat"])
