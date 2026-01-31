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

"""Research idea agent for finding new research lines."""

from google.adk import Agent

from academic_research.util.prompts import load_prompt
from academic_research.util.tools import fetch_url

MODEL = "gemini-2.5-flash"


class ResearchIdeaAgent(Agent):
    """Subclass so ADK infers app name from our module, not google.adk.agents."""
    __module__ = "academic_research.sub_agents.research_idea.agent"


research_idea_agent = ResearchIdeaAgent(
    model=MODEL,
    name="research_idea_agent",
    description=load_prompt("research_idea/description"),
    instruction=load_prompt("research_idea/instruction"),
    tools=[fetch_url],
)
