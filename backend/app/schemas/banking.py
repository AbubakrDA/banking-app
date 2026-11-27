from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class BankAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_id: str
    account_number_masked: str
    account_type: str
    currency: str
    balance_minor: int
    status: str
    created_at: datetime


class BankTransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    customer_id: str
    tx_type: str
    amount_minor: int
    currency: str
    description: str
    counterparty_masked: Optional[str] = None
    occurred_at: datetime


class PaginatedTransactionsResponse(BaseModel):
    items: List[BankTransactionRead]
    total: int
    page: int
    page_size: int


class TransferCreateRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount_minor: int = Field(..., gt=0, description="Transfer amount in integer minor units (must be > 0)")
    currency: str = Field("USD", min_length=3, max_length=3)
    reference: Optional[str] = Field(None, max_length=255)


class BankTransferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    from_account_id: str
    to_account_id: str
    customer_id: str
    requested_by_user_id: str
    amount_minor: int
    currency: str
    reference: Optional[str] = None
    status: str
    risk_score: int
    approved_by_user_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime


class ApprovalDecisionRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=255)


class BankCardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    customer_id: str
    card_last4: str
    card_type: str
    status: str
    created_at: datetime


class CardStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(active|blocked)$")


class CustomerMaskedRead(BaseModel):
    id: str
    name: str
    email_masked: Optional[str] = None
    national_id_masked: str
    tier: str


class RiskAlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_id: str
    account_id: Optional[str] = None
    transfer_id: Optional[str] = None
    severity: str
    risk_score: int
    summary: str
    status: str
    created_at: datetime


class PolicyDocumentCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    filename: str = Field(..., min_length=2, max_length=255)
    pages: List[str] = Field(..., min_length=1, description="Extracted text per page")


class PolicyDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    filename: str
    status: str
    uploaded_by_user_id: str
    reviewed_by_user_id: Optional[str] = None
    review_reason: Optional[str] = None
    page_count: int
    created_at: datetime


class PolicyReviewRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=255)
