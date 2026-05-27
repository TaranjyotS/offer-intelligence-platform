# Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs


## Authentication

Demo mode includes `/api/v1/auth/register`, `/api/v1/auth/login`, and `/api/v1/auth/me`. Offer and member-history endpoints require a Bearer token. In production, replace the in-memory user repository with persistent users or OAuth/OIDC provider-issued JWT validation.
