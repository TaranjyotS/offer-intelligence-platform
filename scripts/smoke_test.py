#!/usr/bin/env python3
"""Run a quick end-to-end smoke test against the Offer Intelligence API."""

from __future__ import annotations

import argparse
import sys
from typing import Any

import httpx


def build_payload(member_id: str) -> dict[str, Any]:
    return {
        "member_id": member_id,
        "transaction_type": "GIFT",
        "points_bought": 500,
        "revenue_usd": 25.5,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test the Offer Intelligence API.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--member-id", default="SMOKE-001", help="Member ID to test")
    parser.add_argument("--username", default="admin", help="Demo auth username")
    parser.add_argument("--password", default="demo123", help="Demo auth password")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    try:
        with httpx.Client(timeout=10.0) as client:
            health = client.get(f"{base_url}/api/v1/health")
            health.raise_for_status()

            token_response = client.post(f"{base_url}/api/v1/auth/login", json={"username": args.username, "password": args.password})
            token_response.raise_for_status()
            headers = {"Authorization": f"Bearer {token_response.json()['access_token']}"}

            response = client.post(f"{base_url}/api/v1/offers", json=build_payload(args.member_id), headers=headers)
            response.raise_for_status()
            body = response.json()

            required_keys = {"request_id", "features", "value_prediction", "response_prediction", "offer"}
            missing = required_keys.difference(body)
            if missing:
                print(f"Smoke test failed. Missing keys: {sorted(missing)}")
                return 1

            offer = body["offer"]
            print("Smoke test passed")
            print(f"Service: {health.json().get('service')}")
            print(f"Member: {args.member_id}")
            print(f"Offer: {offer.get('offer_name')} ({offer.get('offer_code')})")
            print(f"Decision reason: {offer.get('reason')}")
            return 0
    except httpx.HTTPError as exc:
        print(f"Smoke test failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
