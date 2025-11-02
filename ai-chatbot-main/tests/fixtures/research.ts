import type { ResearchEvent } from "@/hooks/use-research-progress";

export const mockResearchPrompt =
  "Investigate the latest breakthroughs in quantum computing hardware.";

export const mockResearchEvents: ResearchEvent[] = [
  {
    type: "start",
    data: { message: "Research request received", agent: "Planner Agent" },
  },
  {
    type: "plan",
    data: {
      outline: [
        "Summarize current hardware landscape",
        "Highlight 2024-2025 breakthroughs",
        "Compare superconducting vs trapped ion approaches",
      ],
    },
  },
  {
    type: "progress",
    data: {
      source: "ArXiv",
      title:
        "Topological qubits reach error rates below 10^-6 (arXiv:2501.01234)",
    },
  },
  {
    type: "progress",
    data: {
      source: "Tavily",
      title:
        "Major cloud vendors roll out hybrid quantum-classical orchestration",
    },
  },
  {
    type: "done",
    data: {
      report:
        "Quantum hardware adoption is accelerating in 2025, driven by error-corrected superconducting qubits and improved trapped ion coherence. Enterprises should evaluate hybrid architectures.",
    },
  },
];

export const mockResearchReport =
  mockResearchEvents[mockResearchEvents.length - 1].data.report ??
  "Research summary unavailable.";
