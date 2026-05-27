import asyncio

from app.models.domain import MemberFeatures, PredictionResult


class PredictionService:
    """Deterministic ML-like scoring service used to keep the project runnable locally.

    In a real deployment this class would call model endpoints or load registered model artifacts.
    """

    async def predict_value_score(self, features: MemberFeatures) -> PredictionResult:
        await asyncio.sleep(0)
        expected_volume = (features.last_3_transactions_avg_points_bought * 0.7) + (features.avg_points_bought * 0.3)
        engagement_weight = max(
            0.1,
            features.pct_buy_transactions + features.pct_gift_transactions - (features.pct_redeem_transactions * 0.5),
        )
        prediction = round(expected_volume * engagement_weight, 4)
        confidence = min(0.95, 0.55 + min(features.transaction_count, 10) * 0.04)
        return PredictionResult(
            model_name="value_score",
            prediction=prediction,
            confidence=round(confidence, 2),
            explanation=(
                "Estimated member value based on recent points activity, " "lifetime history, and transaction mix."
            ),
        )

    async def predict_response(self, features: MemberFeatures) -> PredictionResult:
        await asyncio.sleep(0)
        product_weight = (
            features.pct_buy_transactions * 0.45
            + features.pct_gift_transactions * 0.35
            + features.pct_redeem_transactions * 0.20
        )
        revenue_signal = min(
            1.0,
            (features.avg_revenue_usd * 0.3 + features.last_3_transactions_avg_revenue_usd * 0.7) / 50,
        )
        recency_signal = 1 / (features.days_since_last_transaction + 1)
        raw_prediction = product_weight * 0.55 + revenue_signal * 0.35 + recency_signal * 0.10
        prediction = round(min(0.95, max(0.05, raw_prediction)), 4)
        confidence = min(0.92, 0.50 + min(features.transaction_count, 10) * 0.035)
        return PredictionResult(
            model_name="response",
            prediction=prediction,
            confidence=round(confidence, 2),
            explanation="Probability-like response score from purchase pattern, revenue signal, and recency.",
        )
