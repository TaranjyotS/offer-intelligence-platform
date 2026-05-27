#!/usr/bin/env python3
"""Generate lightweight concurrent traffic against the offer endpoint."""

from __future__ import annotations

import argparse
import asyncio
import random
import statistics
import time
from typing import Any

import httpx


TRANSACTION_TYPES = ["GIFT", "BUY", "REDEEM"]


def payload(index: int) -> dict[str, Any]:
    return {
        "member_id": f"LOAD-{index % 25:03d}",
        "transaction_type": random.choice(TRANSACTION_TYPES),
        "points_bought": random.choice([100, 250, 500, 1000, 2500, 5000]),
        "revenue_usd": round(random.uniform(5, 250), 2),
    }


async def send_one(client: httpx.AsyncClient, base_url: str, index: int) -> float:
    start = time.perf_counter()
    response = await client.post(f"{base_url}/api/v1/offers", json=payload(index))
    response.raise_for_status()
    return (time.perf_counter() - start) * 1000


async def run(base_url: str, requests: int, concurrency: int, username: str, password: str) -> int:
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    async with httpx.AsyncClient(timeout=15.0, limits=limits) as client:
        await client.get(f"{base_url}/api/v1/health")
        token_response = await client.post(f"{base_url}/api/v1/auth/login", json={"username": username, "password": password})
        token_response.raise_for_status()
        client.headers.update({"Authorization": f"Bearer {token_response.json()['access_token']}"})
        semaphore = asyncio.Semaphore(concurrency)

        async def guarded(index: int) -> float:
            async with semaphore:
                return await send_one(client, base_url, index)

        start = time.perf_counter()
        latencies = await asyncio.gather(*(guarded(i) for i in range(requests)))
        elapsed = time.perf_counter() - start

    print("Load test complete")
    print(f"Requests: {requests}")
    print(f"Concurrency: {concurrency}")
    print(f"Throughput: {requests / elapsed:.2f} req/s")
    print(f"Avg latency: {statistics.mean(latencies):.2f} ms")
    print(f"P95 latency: {statistics.quantiles(latencies, n=20)[18]:.2f} ms")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate sample load for the API.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--requests", type=int, default=50, help="Total requests")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    parser.add_argument("--username", default="admin", help="Demo auth username")
    parser.add_argument("--password", default="demo123", help="Demo auth password")
    args = parser.parse_args()
    return asyncio.run(run(args.base_url.rstrip("/"), args.requests, args.concurrency, args.username, args.password))


if __name__ == "__main__":
    raise SystemExit(main())
