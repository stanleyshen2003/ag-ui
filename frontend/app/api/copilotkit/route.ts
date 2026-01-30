/**
 * CopilotKit API route: bridges the frontend to the AG-UI ADK backend.
 * Uses HttpAgent to connect to the FastAPI AG-UI server (e.g. http://localhost:8000/).
 * Reference: https://www.copilotkit.ai/blog/build-a-frontend-for-your-adk-agents-with-ag-ui
 */

import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

// Backend AG-UI server URL (default: backend running on port 8000)
const AG_UI_URL =
  process.env.NEXT_PUBLIC_AG_UI_URL ?? "http://localhost:8000/";

const serviceAdapter = new ExperimentalEmptyAdapter();

// Type assertion: CopilotKit bundles its own @ag-ui/client; at runtime the AG-UI protocol is compatible.
const runtime = new CopilotRuntime({
  agents: {
    academic_research: new HttpAgent({
      url: AG_UI_URL.replace(/\/?$/, "/"),
    }) as any,
  },
});

export async function POST(req: NextRequest) {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });
  return handleRequest(req);
}
