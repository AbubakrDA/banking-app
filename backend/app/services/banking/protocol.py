from datetime import datetime
from typing import Protocol, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banking import BankAccount, BankTransaction, BankCard
from app.models.customer import Customer


class BankingAPI(Protocol):
    """Protocol abstracting core banking system operations (never connects to a real bank)."""

    async def seed_dev_data(self, db: AsyncSession, tenant_id: str) -> None: ...

    async def list_accounts(
        self, db: AsyncSession, tenant_id: str, customer_id: Optional[str] = None
    ) -> List[BankAccount]: ...

    async def get_account(
        self, db: AsyncSession, tenant_id: str, account_id: str
    ) -> Optional[BankAccount]: ...

    async def list_transactions(
        self,
        db: AsyncSession,
        tenant_id: str,
        account_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        min_amount_minor: Optional[int] = None,
        max_amount_minor: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[BankTransaction], int]: ...

    async def list_cards(
        self, db: AsyncSession, tenant_id: str, customer_id: Optional[str] = None
    ) -> List[BankCard]: ...

    async def search_customers(
        self, db: AsyncSession, tenant_id: str, query: Optional[str] = None
    ) -> List[Customer]: ...
