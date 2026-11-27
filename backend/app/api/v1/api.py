from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    tenants,
    auth,
    business_data,
    chat,
    documents,
    knowledge,
    memory,
    tickets,
    nlp,
    analytics,
    tools,
    enterprise,
    infrastructure,
    backup,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth & RBAC"])
api_router.include_router(business_data.router, prefix="/business", tags=["Business Data Hub"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat & Agent"])
api_router.include_router(documents.router, prefix="/documents", tags=["Document Intelligence"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base & RAG"])
api_router.include_router(memory.router, prefix="/memory", tags=["Customer Memory"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["Complaints & Tickets"])
api_router.include_router(nlp.router, prefix="/nlp", tags=["NLP & Question Intelligence"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Admin Intelligence & Analytics"])
api_router.include_router(tools.router, prefix="/tools", tags=["Tools & MCP Gateway"])
api_router.include_router(enterprise.router, prefix="/enterprise", tags=["Enterprise Administration"])
api_router.include_router(infrastructure.router, prefix="/infrastructure", tags=["Cloud Infrastructure & Telemetry"])
api_router.include_router(backup.router, prefix="/backup", tags=["Backup & Disaster Recovery"])
