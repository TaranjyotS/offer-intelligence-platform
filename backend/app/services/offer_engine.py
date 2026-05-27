from app.models.domain import OfferDecision, PredictionResult


class OfferEngine:
    def assign(self, value_score: PredictionResult, response: PredictionResult) -> OfferDecision:
        expected_value = value_score.prediction * response.prediction

        if expected_value >= 300:
            return OfferDecision(
                offer_code="PREMIUM_50_DISCOUNT",
                offer_label="50% Discount",
                priority="high",
                reason="High predicted value and strong response likelihood.",
            )
        if expected_value >= 125:
            return OfferDecision(
                offer_code="BONUS_35_POINTS",
                offer_label="35% Bonus Points",
                priority="medium",
                reason="Moderate predicted value; bonus points can improve engagement.",
            )
        return OfferDecision(
            offer_code="BONUS_10_POINTS",
            offer_label="10% Bonus Points",
            priority="low",
            reason="Lower predicted value; use a lightweight incentive.",
        )
