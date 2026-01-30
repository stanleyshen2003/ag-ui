# Academic Research — Frontend

Next.js + CopilotKit UI for the Academic Research agent. Connects to the AG-UI backend (default: `http://localhost:8000`).

## Quick start

From this directory (`frontend/`):

```bash
# Install dependencies
npm install --legacy-peer-deps

# Run dev server (ensure backend is running: cd ../backend && uv run python main.py)
npm run dev
```

Open **http://localhost:3000**. Set `NEXT_PUBLIC_AG_UI_URL` in `.env.local` if the backend runs elsewhere.

For full setup, see the [root README](../README.md).
