import asyncio
import uuid
from datetime import datetime, timezone

from app.models.domain import MemberTransaction
from app.schemas.offer import OfferRequest, OfferResponse
from app.services.feature_engineering import compute_member_features
from app.services.member_store import MemberDataStore, member_store
from app.services.offer_engine import OfferEngine
from app.services.prediction_service import PredictionService


class OfferOrchestrator:
    def __init__(
        self,
        store: MemberDataStore = member_store,
        predictor: PredictionService | None = None,
        offer_engine: OfferEngine | None = None,
    ) -> None:
        self.store = store
        self.predictor = predictor or PredictionService()
        self.offer_engine = offer_engine or OfferEngine()

    async def generate_offer(self, request: OfferRequest) -> OfferResponse:
        transaction = MemberTransaction(
            member_id=request.member_id,
            transaction_utc_ts=request.transaction_utc_ts or datetime.now(timezone.utc),
            transaction_type=request.transaction_type,
            points_bought=request.points_bought,
            revenue_usd=request.revenue_usd,
        )
        history = self.store.list_transactions(transaction.member_id)
        features = compute_member_features(history, transaction)
        value_prediction, response_prediction = await asyncio.gather(
            self.predictor.predict_value_score(features),
            self.predictor.predict_response(features),
        )
        offer = self.offer_engine.assign(value_prediction, response_prediction)
        self.store.add_transaction(transaction)

        return OfferResponse(
            request_id=str(uuid.uuid4()),
            transaction=transaction,
            history_count_before_write=len(history),
            features=features,
            value_prediction=value_prediction,
            response_prediction=response_prediction,
            offer=offer,
        )


orchestrator = OfferOrchestrator()
