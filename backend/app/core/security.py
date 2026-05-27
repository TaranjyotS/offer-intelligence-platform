from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.services.user_store import user_store

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    username: str
    auth_provider: str = "demo-jwt"
    role: str = "Operator"


def _b64url_encode(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("utf-8")


def _b64url_decode(payload: str) -> bytes:
    padding = "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode(payload + padding)


def create_access_token(username: str) -> str:
    settings = get_settings()
    issued_at = int(time.time())
    expires_at = issued_at + settings.jwt_access_token_minutes * 60
    header = {"alg": "HS256", "typ": "JWT"}
    payload: dict[str, Any] = {
        "sub": username,
        "iat": issued_at,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    signing_input = f"{_b64url_encode(json.dumps(header, separators=(',', ':')).encode())}.{_b64url_encode(json.dumps(payload, separators=(',', ':')).encode())}"
    signature = hmac.new(settings.jwt_secret.get_secret_value().encode() if settings.jwt_secret else b"", signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(settings.jwt_secret.get_secret_value().encode() if settings.jwt_secret else b"", signing_input.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_encode(expected_signature), signature_b64):
            raise ValueError("Invalid token signature")
        header = json.loads(_b64url_decode(header_b64))
        payload = json.loads(_b64url_decode(payload_b64))
        if header.get("alg") != "HS256":
            raise ValueError("Unsupported token algorithm")
        now = int(time.time())
        if int(payload.get("exp", 0)) < now:
            raise ValueError("Token expired")
        if payload.get("iss") != settings.jwt_issuer:
            raise ValueError("Invalid token issuer")
        if payload.get("aud") != settings.jwt_audience:
            raise ValueError("Invalid token audience")
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    claims = decode_access_token(credentials.credentials)
    username = str(claims["sub"])
    stored_user = user_store.get_user(username)
    return AuthenticatedUser(username=username, role=stored_user.role if stored_user else "Operator")
