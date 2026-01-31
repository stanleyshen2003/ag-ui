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

"""Academic_Research: Research advice, related literature finding, research area proposals, web knowledge access."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from .util.prompts import load_prompt
from .sub_agents.literature_synthesizer import literature_synthesizer_agent
from .sub_agents.paper_critic import paper_critic_agent
from .sub_agents.research_idea import research_idea_agent
from .sub_agents.trend_survey import trend_survey_agent
from .sub_agents.paper_search import paper_search_agent

MODEL = "gemini-2.5-flash"


class CoordinatorAgent(LlmAgent):
    """Root coordinator agent defined in this module so ADK Runner infers app name from academic_research.agent, avoiding 'App name mismatch' warning."""

    __module__ = "academic_research.agent"


coordinator = CoordinatorAgent(
    name="coordinator",
    model=MODEL,
    description=load_prompt("coordinator/description"),
    instruction=load_prompt("coordinator/instruction"),
    tools=[
        AgentTool(agent=paper_search_agent),
        AgentTool(agent=trend_survey_agent),
    ],
    sub_agents=[
        literature_synthesizer_agent,
        paper_critic_agent,
        research_idea_agent,
    ],
)

root_agent = coordinator
