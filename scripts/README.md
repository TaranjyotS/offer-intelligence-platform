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
