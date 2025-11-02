import { test, expect } from "@playwright/test";
import { percySnapshot } from "@percy/playwright";

const VISUAL_SCENARIOS = [
  { name: "Idle", query: "scenario=idle" },
  { name: "Active", query: "scenario=active" },
  { name: "Error", query: "scenario=error" },
  { name: "Done", query: "scenario=done" },
];

const isPercyEnabled =
  !!process.env.PERCY_TOKEN ||
  process.env.PERCY_ENABLE === "1" ||
  process.env.PERCY_ON === "true";

test.describe("@visual Research Panel snapshots", () => {
  for (const scenario of VISUAL_SCENARIOS) {
    test(`@visual ResearchPanel - ${scenario.name}`, async ({ page }) => {
      await page.goto(`/research-preview?${scenario.query}`);
      await page.getByTestId("research-panel").waitFor();

      // Basic assertion to ensure the panel renders
      await expect(page.getByTestId("research-panel")).toBeVisible();

      if (isPercyEnabled) {
        await percySnapshot(page, `ResearchPanel - ${scenario.name}`, {
          widths: [375, 768, 1280],
        });
      }
    });
  }

  test("@visual ResearchPanel - Active (Dark)", async ({ page }) => {
    await page.goto("/research-preview?scenario=active&theme=dark");
    await page.getByTestId("research-panel").waitFor();
    await expect(page.getByTestId("research-panel")).toBeVisible();

    if (isPercyEnabled) {
      await percySnapshot(page, "ResearchPanel - Active (Dark)", {
        widths: [375, 1280],
      });
    }
  });
});
