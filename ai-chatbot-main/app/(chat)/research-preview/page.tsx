import { notFound } from "next/navigation";
import {
  ResearchPanelPreview,
  type Scenario,
  type Theme,
} from "@/components/research-panel-preview";

const SCENARIO_VALUES = ["idle", "active", "error", "done"] as const;

const isScenario = (value: string | undefined): value is Scenario =>
  typeof value === "string" &&
  (SCENARIO_VALUES as readonly string[]).includes(value);

interface PageProps {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}

export default async function ResearchPreviewPage({ searchParams }: PageProps) {
  if (
    process.env.NODE_ENV === "production" &&
    process.env.NEXT_PUBLIC_ENABLE_RESEARCH_PREVIEW !== "true"
  ) {
    notFound();
  }

  const params = await searchParams;
  const scenarioParam = normalizeParam(params?.scenario);
  const themeParam = normalizeParam(params?.theme);

  const scenario: Scenario = isScenario(scenarioParam)
    ? scenarioParam
    : "idle";
  const theme: Theme = themeParam === "dark" ? "dark" : "light";

  return <ResearchPanelPreview scenario={scenario} theme={theme} />;
}

function normalizeParam(
  value: string | string[] | undefined
): string | undefined {
  if (!value) return undefined;
  return Array.isArray(value) ? value[0] : value;
}
