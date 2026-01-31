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

"""Load prompts from local files in academic_research/prompts/."""

from __future__ import annotations

from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """Load prompt template by name.

    Expects name in format: agentname/instruction or agentname/description
    Resolves to prompts/agentname/instruction.txt or prompts/agentname/description.txt.
    """
    if "/" not in name:
        raise ValueError(
            f"Prompt name must be '<agent>/instruction' or '<agent>/description', got: {name!r}"
        )
    agent, kind = name.split("/", 1)
    if kind not in ("instruction", "description"):
        raise ValueError(
            f"Prompt kind must be 'instruction' or 'description', got: {kind!r}"
        )
    path = _PROMPTS_DIR / agent / f"{kind}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()
