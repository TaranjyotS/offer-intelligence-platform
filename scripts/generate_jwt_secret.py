#!/usr/bin/env python3
"""Generate a cryptographically strong JWT secret for deployment.

Usage:
    python scripts/generate_jwt_secret.py

Copy the printed JWT_SECRET value into your production environment if you are
not using Render Blueprint `generateValue: true`.
"""

from __future__ import annotations

import secrets


def main() -> None:
    secret = secrets.token_urlsafe(64)
    print(f"JWT_SECRET={secret}")


if __name__ == "__main__":
    main()
