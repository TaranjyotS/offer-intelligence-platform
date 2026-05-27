from datetime import datetime, timezone

from app.models.domain import MemberFeatures, MemberTransaction, TransactionType


def _avg(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def compute_member_features(history: list[MemberTransaction], current: MemberTransaction) -> MemberFeatures:
    transactions = sorted([*history, current], key=lambda tx: tx.transaction_utc_ts)
    count = len(transactions)
    last_3 = transactions[-3:]

    type_counts = {tx_type: 0 for tx_type in TransactionType}
    for tx in transactions:
        type_counts[tx.transaction_type] += 1

    previous_last = max(history, key=lambda tx: tx.transaction_utc_ts, default=None)
    if previous_last:
        days_since = max(0, (current.transaction_utc_ts - previous_last.transaction_utc_ts).days)
    else:
        days_since = max(0, (datetime.now(timezone.utc) - current.transaction_utc_ts).days)

    return MemberFeatures(
        avg_points_bought=_avg([tx.points_bought for tx in transactions]),
        avg_revenue_usd=_avg([tx.revenue_usd for tx in transactions]),
        last_3_transactions_avg_points_bought=_avg([tx.points_bought for tx in last_3]),
        last_3_transactions_avg_revenue_usd=_avg([tx.revenue_usd for tx in last_3]),
        pct_buy_transactions=round(type_counts[TransactionType.BUY] / count, 4),
        pct_gift_transactions=round(type_counts[TransactionType.GIFT] / count, 4),
        pct_redeem_transactions=round(type_counts[TransactionType.REDEEM] / count, 4),
        days_since_last_transaction=days_since,
        transaction_count=count,
    )
