import { test, expect } from "../fixtures";
import { ChatPage } from "../pages/chat";
import { ResearchPanelPage } from "../pages/research";
import {
  cleanupTestData,
  getResearchTask,
  verifyProgressEvents,
  verifyTaskProgress,
} from "../helpers/research-db";

const RUN_RESEARCH_E2E = process.env.RUN_RESEARCH_E2E === "true";
const describeData = RUN_RESEARCH_E2E
  ? test.describe.serial
  : test.describe.skip;

describeData("@db Research task data validation", () => {
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
      `Trigger research mode for: ${researchPrompt}`
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

  test("persists research progress and report to Neon", async () => {
    await researchPanel.waitForSuggestion();
    await researchPanel.startResearch();
    await researchPanel.waitForStatus("running");

    const metadata = await chatPage.getResearchTaskMetadata();
    expect(metadata.taskId).toBeTruthy();
    expect(metadata.status).toBe("running");
    const taskId = metadata.taskId!;

    await researchPanel.waitForStatus("done");
    const metadataDone = await chatPage.getResearchTaskMetadata();
    expect(metadataDone.status).toBe("done");

    await expect
      .poll(async () => {
        const record = await getResearchTask(taskId);
        if (record?.user_id) {
          producedUserId = record.user_id;
        }
        return record?.status ?? null;
      }, { timeout: 60_000 })
      .toBe("completed");

    expect(await verifyTaskProgress(taskId, "completed")).toBe(true);
    expect(await verifyProgressEvents(taskId)).toBe(true);

    const record = await getResearchTask(taskId);
    expect(record?.report ?? "").not.toHaveLength(0);
    expect((record?.topic ?? "").trim()).toBe(activeResearchPrompt.trim());
    expect(
      record?.progress?.events?.some((event) => event.type === "done")
    ).toBe(true);
  });
});
