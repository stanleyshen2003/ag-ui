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

Discovers prompts by scanning for {agent_name}/prompts/{prompt_name}.txt and
registers each as agent_name/prompt_name. Self-contained, no project imports.

Usage:
    python scripts/register_prompts.py [--commit-message MESSAGE]
    uv run python scripts/register_prompts.py

Environment:
    MLFLOW_TRACKING_URI: MLflow tracking server URI (default: ./mlruns for local)
    COMMIT_MESSAGE: Override commit message (used by CI; avoids shell quoting issues)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _backend_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _discover_prompts(root: Path) -> list[tuple[str, Path]]:
    """Find prompts/{agent}/{instruction,description}.txt, return (registry_name, path).

    Registry name format: projectname.agentname.instruction or projectname.agentname.description
    """
    results: list[tuple[str, Path]] = []
    root = root.resolve()
    project_name = "academic_research"

    for prompts_dir in root.rglob("prompts"):
        if not prompts_dir.is_dir():
            continue
        # agent_dir = parent of prompts/ (e.g. academic_research)
        agent_dir = prompts_dir.parent
        try:
            agent_rel = agent_dir.relative_to(root)
        except ValueError:
            continue
        if str(agent_rel).replace("\\", "/") != project_name:
            continue

        for agent_folder in prompts_dir.iterdir():
            if not agent_folder.is_dir():
                continue
            agent_name = agent_folder.name
            for kind in ("instruction", "description"):
                path = agent_folder / f"{kind}.txt"
                if path.is_file():
                    registry_name = f"{project_name}.{agent_name}.{kind}"
                    results.append((registry_name, path))

    return sorted(results, key=lambda x: x[0])


def get_git_commit_info(backend_dir: Path) -> str:
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


def register_prompts(root: Path, commit_message: str | None = None) -> None:
    """Discover and register all prompts to MLflow."""
    import mlflow

    if commit_message is None:
        commit_message = get_git_commit_info(root)

    prompts = _discover_prompts(root)
    if not prompts:
        print("No prompts found (expected {agent_name}/prompts/*.txt)")
        return

    for registry_name, prompt_path in prompts:
        template = prompt_path.read_text(encoding="utf-8").strip()
        prompt = mlflow.genai.register_prompt(
            name=registry_name,
            template=template,
            commit_message=commit_message,
            tags={
                "source": "file",
                "path": str(prompt_path.relative_to(root)).replace("\\", "/"),
            },
        )
        print(f"Registered '{registry_name}' -> version {prompt.version}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Register prompts to MLflow")
    parser.add_argument(
        "--commit-message",
        "-m",
        help="Commit message for the prompt version",
    )
    parser.add_argument(
        "--root",
        "-r",
        type=Path,
        default=None,
        help="Root directory to scan (default: parent of scripts/)",
    )
    args = parser.parse_args()

    root = args.root or _backend_dir()

    # COMMIT_MESSAGE env takes precedence (avoids shell quoting in CI)
    commit_message = os.environ.get("COMMIT_MESSAGE") or args.commit_message

    # Ensure MLflow tracking URI is set (default to local if not set)
    if not os.environ.get("MLFLOW_TRACKING_URI"):
        default_uri = (root / "mlruns").as_uri()
        os.environ["MLFLOW_TRACKING_URI"] = default_uri
        print(f"Using default MLFLOW_TRACKING_URI: {default_uri}")

    try:
        register_prompts(root, commit_message=commit_message)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
