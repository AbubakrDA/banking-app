import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.banking import BankAccount, BankTransaction, BankCard, PolicyDocument, PolicyChunk
from app.models.customer import Customer
from app.models.tenant import Tenant


def _hash_acct(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class MockBankingAPI:
    """
    Mock BankingAPI implementation backed by local SQLAlchemy tables.
    Seeds 2 customers, 3 accounts, 2 cards, and 10 transactions in dev/test only.
    """

    async def seed_dev_data(self, db: AsyncSession, tenant_id: str) -> None:
        if settings.ENVIRONMENT not in ("development", "test"):
            return

        # Check if already seeded for this tenant
        existing = await db.execute(
            select(func.count(BankAccount.id)).where(BankAccount.tenant_id == tenant_id)
        )
        if (existing.scalar() or 0) > 0:
            return

        # Ensure tenant exists
        t_res = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        if not t_res.scalar_one_or_none():
            db.add(
                Tenant(
                    id=tenant_id,
                    name="ConversaBank Demo",
                    slug=tenant_id,
                    business_mode="hybrid",
                )
            )
            await db.flush()

        # 2 Customers
        c1_id = f"cust_{tenant_id}_01"
        c2_id = f"cust_{tenant_id}_02"

        c1_res = await db.execute(select(Customer).where(Customer.id == c1_id))
        if not c1_res.scalar_one_or_none():
            db.add(
                Customer(
                    id=c1_id,
                    tenant_id=tenant_id,
                    external_id="cust_user_01",
                    name="Layla Al-Mansoor",
                    email="layla@bank.local",
                    tier="premier",
                    profile_metadata={"national_id_masked": "***-**-4821"},
                )
            )
        c2_res = await db.execute(select(Customer).where(Customer.id == c2_id))
        if not c2_res.scalar_one_or_none():
            db.add(
                Customer(
                    id=c2_id,
                    tenant_id=tenant_id,
                    external_id="cust_user_02",
                    name="Omar Haddad",
                    email="omar@bank.local",
                    tier="standard",
                    profile_metadata={"national_id_masked": "***-**-9104"},
                )
            )
        await db.flush()

        # 3 Accounts (2 for c1 in USD/EUR, 1 for c2 in USD)
        a1_id = f"acct_{tenant_id}_01"
        a2_id = f"acct_{tenant_id}_02"
        a3_id = f"acct_{tenant_id}_03"
        db.add_all(
            [
                BankAccount(
                    id=a1_id,
                    tenant_id=tenant_id,
                    customer_id=c1_id,
                    account_number_masked="****1042",
                    account_number_hash=_hash_acct(f"{tenant_id}:1000001042"),
                    account_type="checking",
                    currency="USD",
                    balance_minor=250_000,  # $2,500.00
                    status="active",
                ),
                BankAccount(
                    id=a2_id,
                    tenant_id=tenant_id,
                    customer_id=c1_id,
                    account_number_masked="****2088",
                    account_number_hash=_hash_acct(f"{tenant_id}:1000002088"),
                    account_type="savings",
                    currency="EUR",
                    balance_minor=180_000,  # EUR 1,800.00
                    status="active",
                ),
                BankAccount(
                    id=a3_id,
                    tenant_id=tenant_id,
                    customer_id=c2_id,
                    account_number_masked="****3099",
                    account_number_hash=_hash_acct(f"{tenant_id}:1000003099"),
                    account_type="checking",
                    currency="USD",
                    balance_minor=95_000,  # $950.00
                    status="active",
                ),
            ]
        )

        # 2 Cards
        db.add_all(
            [
                BankCard(
                    id=f"card_{tenant_id}_01",
                    tenant_id=tenant_id,
                    account_id=a1_id,
                    customer_id=c1_id,
                    card_last4="4412",
                    card_type="debit",
                    status="active",
                ),
                BankCard(
                    id=f"card_{tenant_id}_02",
                    tenant_id=tenant_id,
                    account_id=a3_id,
                    customer_id=c2_id,
                    card_last4="8831",
                    card_type="credit",
                    status="active",
                ),
            ]
        )

        # 10 Transactions
        now = datetime.now(timezone.utc)
        sample_txs = [
            (a1_id, c1_id, "credit", 300_000, "USD", "Payroll Direct Deposit", "Employer Payroll", 9),
            (a1_id, c1_id, "debit", 12_500, "USD", "Grocery Market", "FreshMart", 8),
            (a1_id, c1_id, "debit", 4_500, "USD", "Utility Bill Payment", "City Power", 7),
            (a1_id, c1_id, "debit", 8_900, "USD", "Airline Booking", "SkyAir", 6),
            (a1_id, c1_id, "debit", 24_100, "USD", "Electronics Store", "TechHub", 5),
            (a2_id, c1_id, "credit", 180_000, "EUR", "Initial Savings Funding", "Self", 4),
            (a3_id, c2_id, "credit", 120_000, "USD", "Wire Deposit", "Client Remittance", 3),
            (a3_id, c2_id, "debit", 15_000, "USD", "Rent Payment", "City Living", 2),
            (a3_id, c2_id, "debit", 6_200, "USD", "Pharmacy", "CarePlus", 1),
            (a3_id, c2_id, "debit", 3_800, "USD", "Coffee & Dining", "Cafe Central", 0),
        ]
        for idx, (aid, cid, ttype, amt, curr, desc, cp, days_ago) in enumerate(sample_txs):
            db.add(
                BankTransaction(
                    id=f"tx_{tenant_id}_{idx+1:02d}",
                    tenant_id=tenant_id,
                    account_id=aid,
                    customer_id=cid,
                    tx_type=ttype,
                    amount_minor=amt,
                    currency=curr,
                    description=desc,
                    counterparty_masked=cp,
                    occurred_at=now - timedelta(days=days_ago),
                )
            )

        # Seed 1 approved sample policy for dev/test retrieval
        pol_id = f"pol_{tenant_id}_01"
        db.add(
            PolicyDocument(
                id=pol_id,
                tenant_id=tenant_id,
                title="Retail Transfer & Card Security Policy",
                filename="retail_transfer_policy.pdf",
                status="approved",
                uploaded_by_user_id="admin_seed",
                reviewed_by_user_id="risk_seed",
                page_count=2,
            )
        )
        db.add_all(
            [
                PolicyChunk(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    policy_id=pol_id,
                    page_number=1,
                    chunk_index=0,
                    content="Domestic transfers of 1,000.00 USD (100,000 minor units) or more require supervisor approval under maker-checker rules. Zero fee applies to standard internal transfers.",
                    embedding=[],
                ),
                PolicyChunk(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    policy_id=pol_id,
                    page_number=2,
                    chunk_index=1,
                    content="Customers may immediately block or unblock their payment cards at any time. Lost or stolen cards should be blocked immediately.",
                    embedding=[],
                ),
            ]
        )
        await db.commit()

    async def list_accounts(
        self, db: AsyncSession, tenant_id: str, customer_id: Optional[str] = None
    ) -> List[BankAccount]:
        stmt = select(BankAccount).where(BankAccount.tenant_id == tenant_id)
        if customer_id:
            stmt = stmt.where(BankAccount.customer_id == customer_id)
        stmt = stmt.order_by(BankAccount.created_at.asc())
        return list((await db.execute(stmt)).scalars().all())

    async def get_account(
        self, db: AsyncSession, tenant_id: str, account_id: str
    ) -> Optional[BankAccount]:
        stmt = select(BankAccount).where(
            BankAccount.id == account_id, BankAccount.tenant_id == tenant_id
        )
        return (await db.execute(stmt)).scalar_one_or_none()

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
    ) -> Tuple[List[BankTransaction], int]:
        stmt = select(BankTransaction).where(BankTransaction.tenant_id == tenant_id)
        count_stmt = select(func.count(BankTransaction.id)).where(BankTransaction.tenant_id == tenant_id)

        for cond in (
            BankTransaction.account_id == account_id if account_id else None,
            BankTransaction.customer_id == customer_id if customer_id else None,
            BankTransaction.amount_minor >= min_amount_minor if min_amount_minor is not None else None,
            BankTransaction.amount_minor <= max_amount_minor if max_amount_minor is not None else None,
            BankTransaction.occurred_at >= start_date if start_date else None,
            BankTransaction.occurred_at <= end_date if end_date else None,
        ):
            if cond is not None:
                stmt = stmt.where(cond)
                count_stmt = count_stmt.where(cond)

        total = (await db.execute(count_stmt)).scalar() or 0
        stmt = (
            stmt.order_by(BankTransaction.occurred_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list((await db.execute(stmt)).scalars().all())
        return items, total

    async def list_cards(
        self, db: AsyncSession, tenant_id: str, customer_id: Optional[str] = None
    ) -> List[BankCard]:
        stmt = select(BankCard).where(BankCard.tenant_id == tenant_id)
        if customer_id:
            stmt = stmt.where(BankCard.customer_id == customer_id)
        return list((await db.execute(stmt)).scalars().all())

    async def search_customers(
        self, db: AsyncSession, tenant_id: str, query: Optional[str] = None
    ) -> List[Customer]:
        stmt = select(Customer).where(Customer.tenant_id == tenant_id)
        if query:
            stmt = stmt.where(Customer.name.ilike(f"%{query}%"))
        return list((await db.execute(stmt)).scalars().all())
