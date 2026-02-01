# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
AG-UI server: exposes the Academic Research ADK agent via the AG-UI protocol
so that HTML/React (e.g. CopilotKit) and other AG-UI clients can connect.

Run: uv run python main.py
Then open the HTML chat at http://localhost:8080 (serve web/ separately)
or use any AG-UI client pointing at http://localhost:8000/
"""

import os

import dotenv
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

# Load .env from backend directory so GOOGLE_API_KEY etc. are available.
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from academic_research.agent import root_agent as academic_root_agent

# Wrap the ADK agent with AG-UI middleware (sessions, identity, event protocol).
ag_agent = ADKAgent(
    adk_agent=academic_root_agent,
    app_name="academic_research",
    user_id="default",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

app = FastAPI(title="Academic Research AG-UI")

# Allow HTML frontend (and CopilotKit) to call this API from another origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Expose the AG-UI / ADK-compatible chat API at "/".
# AG-UI clients (e.g. web/index.html or CopilotKit) call this endpoint.
add_adk_fastapi_endpoint(app, ag_agent, path="/")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
