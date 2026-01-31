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

"""Paper search agent for finding research papers using search tools."""

from google.adk import Agent

from academic_research.util.prompts import load_prompt

from . import tools as paper_search_tools

MODEL = "gemini-2.5-flash"


class PaperSearchAgent(Agent):
    """Subclass so ADK infers app name from our module, not google.adk.agents."""
    __module__ = "academic_research.sub_agents.paper_search.agent"


paper_search_agent = PaperSearchAgent(
    model=MODEL,
    name="paper_search_agent",
    description=load_prompt("paper_search/description"),
    instruction=load_prompt("paper_search/instruction"),
    output_key="recent_citing_papers",
    tools=[paper_search_tools.semanticscholar_search_bulk],
)
