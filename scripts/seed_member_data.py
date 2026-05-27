#!/usr/bin/env python3
"""Seed the running API with realistic member transaction examples."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx


TRANSACTIONS: list[dict[str, Any]] = [
    {"member_id": "A0F18FAA", "transaction_type": "GIFT", "points_bought": 500, "revenue_usd": 25.50},
    {"member_id": "A0F18FAA", "transaction_type": "BUY", "points_bought": 2500, "revenue_usd": 105.75},
    {"member_id": "B7C42E91", "transaction_type": "REDEEM", "points_bought": 300, "revenue_usd": 12.00},
    {"member_id": "C9D32A10", "transaction_type": "BUY", "points_bought": 7500, "revenue_usd": 310.00},
    {"member_id": "D1E55B73", "transaction_type": "GIFT", "points_bought": 1200, "revenue_usd": 60.00},
]


def add_timestamps(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    now = datetime.now(tz=UTC)
    enriched = []
    for index, row in enumerate(rows):
        enriched.append({**row, "transaction_utc_ts": (now - timedelta(days=index)).isoformat()})
    return enriched


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed member transactions through the public API.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--username", default="admin", help="Demo auth username")
    parser.add_argument("--password", default="demo123", help="Demo auth password")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    rows = add_timestamps(TRANSACTIONS)

    try:
        with httpx.Client(timeout=10.0) as client:
            client.get(f"{base_url}/api/v1/health").raise_for_status()
            token_response = client.post(f"{base_url}/api/v1/auth/login", json={"username": args.username, "password": args.password})
            token_response.raise_for_status()
            headers = {"Authorization": f"Bearer {token_response.json()['access_token']}"}
            for row in rows:
                response = client.post(f"{base_url}/api/v1/offers", json=row, headers=headers)
                response.raise_for_status()
                offer = response.json()["offer"]
                print(f"Seeded {row['member_id']} -> {offer['offer_code']}")
            print(f"Seed complete. Posted {len(rows)} transactions.")
            return 0
    except httpx.HTTPError as exc:
        print(f"Seed failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
