import { test, expect } from "../fixtures";
import { ChatPage } from "../pages/chat";
import { ResearchPanelPage } from "../pages/research";
import {
  cleanupTestData,
  getResearchTask,
  verifyProgressEvents,
} from "../helpers/research-db";

const RUN_RESEARCH_E2E = process.env.RUN_RESEARCH_E2E === "true";
const describeResearch = RUN_RESEARCH_E2E
  ? test.describe.serial
  : test.describe.skip;

// These tests require a running FastAPI backend, Neon database, and research agents.
describeResearch("@e2e Research end-to-end workflow", () => {
  let chatPage: ChatPage;
  let researchPanel: ResearchPanelPage;
  let producedUserId: string | null = null;
  let activeResearchPrompt = "";

  const backendUrl =
    process.env.RESEARCH_API_URL ?? "http://localhost:8000";
  let backendHealthyChecked = false;
  let backendHealthy = false;

  const ensureBackendReady = async (): Promise<boolean> => {
    if (backendHealthyChecked) {
      return backendHealthy;
    }
    backendHealthyChecked = true;
    try {
      const response = await fetch(`${backendUrl}/api/health`, {
        method: "GET",
        headers: { Accept: "application/json" },
      });
      backendHealthy = response.ok;
    } catch (error) {
      console.warn("Research backend health check failed", error);
      backendHealthy = false;
    }
    return backendHealthy;
  };

  test.beforeEach(async ({ curieContext, researchPrompt }, testInfo) => {
    if (!(await ensureBackendReady())) {
      testInfo.skip(
        `Research backend not reachable at ${backendUrl}. Start FastAPI server before running these tests.`
      );
    }

    await curieContext.page.addInitScript(() => {
      try {
        const payload = JSON.parse(window.name || "{}");
        if (payload && typeof payload.e2eResearchPrompt === "string") {
          (window as any).__E2E_RESEARCH_PROMPT = payload.e2eResearchPrompt;
        }
      } catch {
        // ignore malformed window.name contents
      }
    });

    await curieContext.page.evaluate((prompt: string) => {
      try {
        const existing = window.name ? JSON.parse(window.name) : {};
        window.name = JSON.stringify({
          ...existing,
          e2eResearchPrompt: prompt,
        });
      } catch {
        window.name = JSON.stringify({ e2eResearchPrompt: prompt });
      }
    }, researchPrompt);

    chatPage = new ChatPage(curieContext.page);
    researchPanel = new ResearchPanelPage(curieContext.page);
    producedUserId = null;
    activeResearchPrompt = researchPrompt;

    await chatPage.createNewChat();
    await chatPage.sendUserMessage(
      `Let's investigate the topic: ${researchPrompt}`
    );
  });

  test.afterEach(async ({ curieContext }) => {
    if (producedUserId) {
      await cleanupTestData(producedUserId).catch(() => undefined);
      producedUserId = null;
    }
    await curieContext.page
      .evaluate(() => {
        window.name = "{}";
        delete (window as any).__E2E_RESEARCH_PROMPT;
      })
      .catch(() => undefined);
  });

  test("executes research workflow end-to-end with persistence", async () => {
    await researchPanel.waitForSuggestion();
    await researchPanel.startResearch();
    await researchPanel.waitForStatus("running");

    const events = await researchPanel.getEventSummaries();
    expect(events.length).toBeGreaterThan(0);

    const metadataWhileStreaming = await chatPage.getResearchTaskMetadata();
    expect(metadataWhileStreaming.taskId).toBeTruthy();
    expect(metadataWhileStreaming.status).toBe("running");
    const taskId = metadataWhileStreaming.taskId!;

    await researchPanel.waitForStatus("done");
    const metadataAfterCompletion = await chatPage.getResearchTaskMetadata();
    expect(metadataAfterCompletion.status).toBe("done");

    await expect
      .poll(async () => {
        const record = await getResearchTask(taskId);
        if (record?.user_id) {
          producedUserId = record.user_id;
        }
        return record?.status ?? null;
      }, { timeout: 60_000 })
      .toBe("completed");

    const record = await getResearchTask(taskId);
    expect(record?.report ?? "").not.toHaveLength(0);
    expect((record?.topic ?? "").trim()).toBe(activeResearchPrompt.trim());
    expect(await verifyProgressEvents(taskId)).toBe(true);
    expect(record?.progress?.events?.length ?? 0).toBeGreaterThan(0);
    expect(
      record?.progress?.events?.some((event) => event.type === "done")
    ).toBe(true);

    const researchSummary = await chatPage.getRecentUserMessage();
    expect(researchSummary?.content ?? "").toContain("Research completed");

    await chatPage.sendUserMessage(
      "Based on that research, what should I do next?"
    );
    await chatPage.isGenerationComplete();

    const assistantMessage = await chatPage.getRecentAssistantMessage();
    expect(assistantMessage?.content ?? "").not.toHaveLength(0);
  });
});
