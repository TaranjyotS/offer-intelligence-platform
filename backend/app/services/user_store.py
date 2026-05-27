from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from app.core.config import get_settings


@dataclass(frozen=True)
class StoredUser:
    username: str
    password_hash: str
    salt: str
    role: str = "Operator"


class UserAlreadyExistsError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass


class UserStore:
    """Small in-memory user store for portfolio/demo usage.

    The interface intentionally mirrors a repository so production deployments can
    replace this class with PostgreSQL plus OAuth/OIDC identity provider records.
    """

    def __init__(self) -> None:
        self._users: dict[str, StoredUser] = {}
        self._bootstrap_demo_users()

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120_000,
        ).hex()

    def _bootstrap_demo_users(self) -> None:
        settings = get_settings()
        for username in {settings.demo_username, "tara", "demo"}:
            self.create_user(
                username=username,
                password=settings.demo_password.get_secret_value(),
                role="Administrator",
                allow_existing=True,
            )

    def create_user(
        self,
        username: str,
        password: str,
        role: str = "Operator",
        allow_existing: bool = False,
    ) -> StoredUser:
        normalized_username = username.strip().lower()
        if normalized_username in self._users:
            if allow_existing:
                return self._users[normalized_username]
            raise UserAlreadyExistsError("An account with this username already exists.")

        salt = secrets.token_hex(16)
        user = StoredUser(
            username=normalized_username,
            password_hash=self._hash_password(password, salt),
            salt=salt,
            role=role,
        )
        self._users[normalized_username] = user
        return user

    def authenticate(self, username: str, password: str) -> StoredUser:
        normalized_username = username.strip().lower()
        user = self._users.get(normalized_username)
        if user is None:
            raise InvalidCredentialsError("Invalid username or password.")
        candidate_hash = self._hash_password(password, user.salt)
        if not hmac.compare_digest(candidate_hash, user.password_hash):
            raise InvalidCredentialsError("Invalid username or password.")
        return user

    def get_user(self, username: str) -> StoredUser | None:
        return self._users.get(username.strip().lower())


user_store = UserStore()
