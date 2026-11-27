from contextvars import ContextVar
from typing import AsyncGenerator, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Holds verified JWT tenant_id for the active request/task; never sourced from X-Tenant-ID
tenant_context_var: ContextVar[Optional[str]] = ContextVar("tenant_context_var", default=None)

db_url = settings.get_database_url()
engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
}
if not db_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    })

# Engine configuration with pooling
engine = create_async_engine(
    db_url,
    **engine_kwargs,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def apply_rls_tenant_context(session: AsyncSession, tenant_id: Optional[str]) -> None:
    """Bind transaction-local PostgreSQL RLS setting app.tenant_id."""
    if not db_url.startswith("sqlite") and tenant_id:
        await session.execute(
            text("SELECT set_config('app.tenant_id', :tenant, true)"),
            {"tenant": tenant_id},
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            await apply_rls_tenant_context(session, tenant_context_var.get())
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
