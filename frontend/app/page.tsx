"use client";

/**
 * Main page with CopilotChat for the Academic Research agent.
 */

import { CopilotChat } from "@copilotkit/react-ui";

const INITIAL_MESSAGE = `👋 Hi! You're chatting with the **Academic Research** agent.

This agent can help you:
- **Explore academic literature** — e.g. "Analyze the Attention is All You Need paper"
- **Find related research** — e.g. "What papers are related to transformer architectures?"
- **Get research advice** — e.g. "Suggest research directions in NLP"
- **Search the web** for up-to-date academic knowledge

Ask anything research-related and the agent will use its tools to help.`;

export default function Home() {
  return (
    <main className="flex h-screen flex-col items-center">
      <div className="chat-center flex w-2/3 max-w-full flex-1 flex-col overflow-hidden">
        <CopilotChat
          className="chat-fullscreen h-full w-full"
        labels={{
          title: "Academic Research Assistant",
          initial: INITIAL_MESSAGE,
          placeholder: "Ask about papers, research directions, or related work…",
        }}
        />
      </div>
    </main>
  );
}
