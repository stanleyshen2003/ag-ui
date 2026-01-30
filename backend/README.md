# Academic Research — Backend

AG-UI server and ADK agent backend. Exposes the Academic Research agent via the AG-UI protocol.

## Quick start

From this directory (`backend/`):

```bash
# Install dependencies (creates .venv/ and installs deps here)
uv sync

# Set GOOGLE_API_KEY in .env (copy from .env.example if needed)

# Run AG-UI server (port 8000)
uv run python main.py
```

For full setup, tests, and deployment, see the [root README](../README.md).

## Project layout

- `main.py` — AG-UI FastAPI server
- `academic_research/` — ADK agent code
- `web/` — Static HTML chat UI (optional; use `frontend/` for CopilotKit UI)
- `eval/`, `tests/` — Evaluation and tests
