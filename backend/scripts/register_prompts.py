#!/usr/bin/env python3
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

"""Register all prompts to MLflow Prompt Registry.

Run this script to create new prompt versions in MLflow. Each run creates
a new version for each prompt, enabling version history and tracking.

Usage:
    python scripts/register_prompts.py [--commit-message MESSAGE]
    uv run python scripts/register_prompts.py

Environment:
    MLFLOW_TRACKING_URI: MLflow tracking server URI (default: ./mlruns for local)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))


def get_git_commit_info() -> str:
    """Get current git commit hash and message for traceability."""
    try:
        rev = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=backend_dir,
        ).stdout.strip()
        msg = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            capture_output=True,
            text=True,
            check=True,
            cwd=backend_dir.parent,
        ).stdout.strip()
        return f"git:{rev[:8]} - {msg[:50]}"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "manual registration"


def register_prompts(commit_message: str | None = None) -> None:
    """Register all prompts from the prompts directory to MLflow."""
    import mlflow

    from academic_research.prompts import PROMPT_REGISTRY

    if commit_message is None:
        commit_message = get_git_commit_info()

    prompts_dir = backend_dir / "prompts"

    for prompt_name, filename in PROMPT_REGISTRY.items():
        prompt_path = prompts_dir / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        template = prompt_path.read_text(encoding="utf-8").strip()

        prompt = mlflow.genai.register_prompt(
            name=prompt_name,
            template=template,
            commit_message=commit_message,
            tags={
                "project": "academic-research",
                "source": "prompts",
            },
        )
        print(f"Registered '{prompt_name}' -> version {prompt.version}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Register prompts to MLflow")
    parser.add_argument(
        "--commit-message",
        "-m",
        help="Commit message for the prompt version",
    )
    args = parser.parse_args()

    # Ensure MLflow tracking URI is set (default to local if not set)
    if not os.environ.get("MLFLOW_TRACKING_URI"):
        default_uri = (backend_dir / "mlruns").as_uri()
        os.environ["MLFLOW_TRACKING_URI"] = default_uri
        print(f"Using default MLFLOW_TRACKING_URI: {default_uri}")

    try:
        register_prompts(commit_message=args.commit_message)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
