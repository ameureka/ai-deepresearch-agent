"use client";

import { useEffect, useMemo } from "react";
import { ResearchPanel } from "@/components/research-panel";
import type {
  ResearchEvent,
  ResearchStatus,
} from "@/hooks/use-research-progress";

type Scenario = "idle" | "active" | "error" | "done";
type Theme = "light" | "dark";

interface ScenarioState {
  prompt: string;
  isActive: boolean;
  status: ResearchStatus;
  events: ResearchEvent[];
  error: Error | null;
}

const BASE_EVENTS: ResearchEvent[] = [
  {
    type: "start",
    data: { message: "Research request received", agent: "Planner Agent" },
    timestamp: Date.now() - 40000,
  },
  {
    type: "plan",
    data: {
      outline: [
        "Gather background knowledge",
        "Compare recent breakthroughs",
        "Summarize actionable insights",
      ],
      agent: "Planner Agent",
    },
    timestamp: Date.now() - 32000,
  },
  {
    type: "progress",
    data: {
      source: "ArXiv",
      title: "Advances in Quantum Error Correction (2025)",
    },
    timestamp: Date.now() - 24000,
  },
  {
    type: "progress",
    data: {
      source: "Tavily",
      title: "Industry adoption of superconducting qubits",
    },
    timestamp: Date.now() - 16000,
  },
];

function buildScenarioState(scenario: Scenario): ScenarioState {
  switch (scenario) {
    case "active":
      return {
        prompt: "Latest breakthroughs in quantum computing hardware",
        isActive: true,
        status: "running",
        events: BASE_EVENTS,
        error: null,
      };
    case "error":
      return {
        prompt: "Impact of quantum processors on cryptography",
        isActive: true,
        status: "error",
        events: [...BASE_EVENTS, { type: "error", data: { message: "Upstream API timeout" } }],
        error: new Error("Streaming interrupted: upstream API timeout"),
      };
    case "done":
      return {
        prompt: "Quantum computing adoption roadmap for enterprises",
        isActive: true,
        status: "done",
        events: [
          ...BASE_EVENTS,
          {
            type: "done",
            data: {
              report: "Research summary with recommendations delivered to chat.",
            },
          },
        ],
        error: null,
      };
    case "idle":
    default:
      return {
        prompt: "Should we explore quantum computing for our product roadmap?",
        isActive: false,
        status: "idle",
        events: [],
        error: null,
      };
  }
}

export function ResearchPanelPreview({
  scenario = "idle",
  theme = "light",
}: {
  scenario?: Scenario;
  theme?: Theme;
}) {
  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  const state = useMemo(() => buildScenarioState(scenario), [scenario]);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="mx-auto max-w-xl">
        <ResearchPanel
          prompt={state.prompt}
          isActive={state.isActive}
          events={state.events}
          status={state.status}
          error={state.error ?? undefined}
          onStart={async () => void 0}
          onCancel={() => void 0}
          onRetry={() => void 0}
        />
      </div>
    </div>
  );
}
