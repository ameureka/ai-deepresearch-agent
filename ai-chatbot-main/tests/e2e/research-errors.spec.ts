import { test, expect } from "@playwright/test";
import { ResearchPanelPage } from "../pages/research";

test.describe("@e2e Research error handling", () => {
  test("@e2e displays error state and retry button", async ({ page }) => {
    await page.goto("/research-preview?scenario=error");
    const researchPanel = new ResearchPanelPage(page);

    await researchPanel.waitForStatus("error");
    const events = await researchPanel.getEventSummaries();

    expect(events.some((event) => event.toLowerCase().includes("error"))).toBe(
      true
    );
    await expect(
      page.getByRole("button", { name: "Retry", exact: true })
    ).toBeVisible();
  });

  test("@e2e can cancel an in-progress research task", async ({ page }) => {
    await page.goto("/research-preview?scenario=active");
    const researchPanel = new ResearchPanelPage(page);

    await researchPanel.waitForStatus("running");
    await researchPanel.cancel();
    await expect(
      page.getByRole("button", { name: "Cancel", exact: true })
    ).toBeVisible();
  });
});
