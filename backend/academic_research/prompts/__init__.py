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

"""Prompt management with MLflow Prompt Registry support.

Loads prompts from MLflow when MLFLOW_TRACKING_URI is configured,
otherwise falls back to local prompt files in backend/prompts/.
"""

from __future__ import annotations

import os
from pathlib import Path

# Registry: prompt_name -> filename in prompts/
PROMPT_REGISTRY = {
    "academic_coordinator": "academic_coordinator.txt",
    "academic_newresearch": "academic_newresearch.txt",
    "academic_websearch": "academic_websearch.txt",
}

_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


def _load_from_mlflow(name: str) -> str | None:
    """Load prompt template from MLflow registry. Returns None if unavailable."""
    try:
        import mlflow

        prompt = mlflow.genai.load_prompt(f"prompts:/{name}@latest")
        return prompt.template
    except Exception:
        return None


def _load_from_local(name: str) -> str:
    """Load prompt template from local file."""
    filename = PROMPT_REGISTRY.get(name)
    if not filename:
        raise ValueError(f"Unknown prompt: {name}")
    path = _PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def get_prompt(name: str) -> str:
    """Get prompt template by name.

    Tries MLflow registry first when MLFLOW_TRACKING_URI is set.
    Falls back to local prompts/ directory.
    """
    if os.environ.get("MLFLOW_TRACKING_URI"):
        template = _load_from_mlflow(name)
        if template is not None:
            return template
    return _load_from_local(name)
