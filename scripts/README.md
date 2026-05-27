# Scripts

Operational helpers for local development and portfolio demos.

| Script | Purpose |
|---|---|
| `start-dev.sh` | Starts backend and frontend with Docker Compose. |
| `smoke_test.py` | Verifies health and one end-to-end offer request. |
| `seed_member_data.py` | Posts sample member transactions through the API. |
| `generate_load.py` | Sends lightweight concurrent traffic for demo/testing. |

Run examples from the repository root:

```bash
python scripts/smoke_test.py --username admin --password demo123
python scripts/seed_member_data.py --username admin --password demo123
python scripts/generate_load.py --username admin --password demo123 --requests 100 --concurrency 20
./scripts/start-dev.sh
```

## Generate Deployment JWT Secret

For local development, the API can generate a temporary JWT secret automatically.
For production, use a stable secret so existing tokens remain valid after restarts.

```bash
python scripts/generate_jwt_secret.py
```

Render Blueprint deployments can generate this automatically with:

```yaml
- key: JWT_SECRET
  generateValue: true
```
