from collections import defaultdict
from copy import deepcopy
from threading import RLock

from app.models.domain import MemberTransaction


class MemberDataStore:
    """Thread-safe in-memory store. Swap this with Postgres/Redis in production."""

    def __init__(self) -> None:
        self._data: dict[str, list[MemberTransaction]] = defaultdict(list)
        self._lock = RLock()

    def list_transactions(self, member_id: str) -> list[MemberTransaction]:
        with self._lock:
            return deepcopy(self._data.get(member_id, []))

    def add_transaction(self, transaction: MemberTransaction) -> MemberTransaction:
        with self._lock:
            self._data[transaction.member_id].append(transaction)
        return transaction

    def seed(self, transactions: list[MemberTransaction]) -> None:
        with self._lock:
            for transaction in transactions:
                self._data[transaction.member_id].append(transaction)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


member_store = MemberDataStore()
