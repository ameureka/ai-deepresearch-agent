import { notFound } from "next/navigation";
import { ResearchPanelPreview } from "@/components/research-panel-preview";

const SCENARIOS = new Set(["idle", "active", "error", "done"]);

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

  const scenario = SCENARIOS.has(scenarioParam) ? scenarioParam : "idle";
  const theme = themeParam === "dark" ? "dark" : "light";

  return <ResearchPanelPreview scenario={scenario} theme={theme} />;
}

function normalizeParam(
  value: string | string[] | undefined
): string | undefined {
  if (!value) return undefined;
  return Array.isArray(value) ? value[0] : value;
}
