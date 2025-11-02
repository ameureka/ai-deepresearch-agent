import { test, expect } from "@playwright/test";
import { runAccessibilityScan } from "../helpers/a11y";

test.describe("@a11y Research Panel accessibility", () => {
  test("@a11y ResearchButton and ResearchProgress meet WCAG AA", async ({
    page,
  }) => {
    await page.goto("/research-preview?scenario=active");
    await page.getByTestId("research-panel").waitFor();

    const results = await runAccessibilityScan(page, {
      include: ["[data-testid='research-panel']"],
    });

    expect(results.violations).toEqual([]);
  });

  test("@a11y ResearchButton focus and keyboard support", async ({ page }) => {
    await page.goto("/research-preview?scenario=idle");

    const researchButton = page.getByTestId("research-button");
    await researchButton.focus();
    await expect(researchButton).toBeFocused();

    await researchButton.press("Enter");
    await expect(researchButton).toBeDisabled();
  });
});
