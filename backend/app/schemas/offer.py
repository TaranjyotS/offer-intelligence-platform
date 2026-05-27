from datetime import datetime

from pydantic import BaseModel, Field

from app.models.domain import MemberFeatures, MemberTransaction, OfferDecision, PredictionResult, TransactionType


class OfferRequest(BaseModel):
    member_id: str = Field(..., min_length=2, max_length=64)
    transaction_type: TransactionType
    points_bought: float = Field(..., ge=0)
    revenue_usd: float = Field(..., ge=0)
    transaction_utc_ts: datetime | None = None


class OfferResponse(BaseModel):
    request_id: str
    transaction: MemberTransaction
    history_count_before_write: int
    features: MemberFeatures
    value_prediction: PredictionResult
    response_prediction: PredictionResult
    offer: OfferDecision


class MemberHistoryResponse(BaseModel):
    member_id: str
    transactions: list[MemberTransaction]


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
