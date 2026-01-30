/**
 * Root layout with CopilotKit provider.
 * Connects the app to the AG-UI backend via runtimeUrl and agent name.
 * Reference: https://www.copilotkit.ai/blog/build-a-frontend-for-your-adk-agents-with-ag-ui
 */

import type { Metadata } from "next";
import { CopilotKit } from "@copilotkit/react-core";
import "./globals.css";
import "@copilotkit/react-ui/styles.css";

export const metadata: Metadata = {
  title: "Academic Research Agent — AG-UI + CopilotKit",
  description: "AI-driven academic research agent with CopilotKit frontend",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // suppressHydrationWarning: avoids hydration errors when browser extensions (e.g. Grammarly) inject attributes into html/body before React hydrates
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased" suppressHydrationWarning>
        <CopilotKit
          runtimeUrl="/api/copilotkit"
          agent="academic_research"
        >
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
