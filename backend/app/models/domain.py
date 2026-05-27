from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator


class TransactionType(StrEnum):
    BUY = "BUY"
    GIFT = "GIFT"
    REDEEM = "REDEEM"


class MemberTransaction(BaseModel):
    member_id: str = Field(..., min_length=2, max_length=64, examples=["A0F18FAA"])
    transaction_utc_ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    transaction_type: TransactionType
    points_bought: float = Field(..., ge=0)
    revenue_usd: float = Field(..., ge=0)

    @field_validator("transaction_utc_ts")
    @classmethod
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class MemberFeatures(BaseModel):
    avg_points_bought: float
    avg_revenue_usd: float
    last_3_transactions_avg_points_bought: float
    last_3_transactions_avg_revenue_usd: float
    pct_buy_transactions: float
    pct_gift_transactions: float
    pct_redeem_transactions: float
    days_since_last_transaction: int
    transaction_count: int


class PredictionResult(BaseModel):
    model_name: Literal["value_score", "response"]
    prediction: float
    confidence: float = Field(..., ge=0, le=1)
    explanation: str


class OfferDecision(BaseModel):
    offer_code: str
    offer_label: str
    priority: Literal["low", "medium", "high"]
    reason: str

    @computed_field
    @property
    def display(self) -> str:
        return f"{self.offer_label} ({self.offer_code})"
