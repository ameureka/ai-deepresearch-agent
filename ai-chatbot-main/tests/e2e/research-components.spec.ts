import { test, expect, devices } from "@playwright/test";

test.describe("@ui Research panel layout", () => {
  test("@ui panel is sticky above composer", async ({ page }) => {
    await page.goto("/research-preview?scenario=idle");
    const panel = page.getByTestId("research-panel");
    await panel.waitFor();

    const stickyInfo = await panel.evaluate((node) => {
      const style = window.getComputedStyle(node);
      return {
        position: style.position,
        bottom: style.bottom,
      };
    });

    expect(stickyInfo.position).toBe("sticky");
    expect(stickyInfo.bottom).toBe("72px");
  });

  test("@ui progress container respects max height and scroll", async ({
    page,
  }) => {
    await page.goto("/research-preview?scenario=active");
    const progress = page.getByTestId("research-progress");
    await progress.waitFor();

    const layoutInfo = await progress.evaluate((node) => {
      const style = window.getComputedStyle(node.parentElement!);
      return {
        maxHeight: style.maxHeight,
        overflowY: style.overflowY,
      };
    });

    expect(layoutInfo.maxHeight).toBe("400px");
    expect(layoutInfo.overflowY).toBe("auto");
  });

  test("@ui responsive widths (mobile)", async ({ browser }) => {
    const context = await browser.newContext(devices["iPhone 12"]);
    const page = await context.newPage();
    await page.goto("/research-preview?scenario=idle");

    const panelWidth = await page
      .getByTestId("research-panel")
      .evaluate((node) => node.getBoundingClientRect().width);

    expect(panelWidth).toBeLessThanOrEqual(390);
    await context.close();
  });

  test("@ui responsive widths (desktop)", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto("/research-preview?scenario=active");

    const panelWidth = await page
      .getByTestId("research-panel")
      .evaluate((node) => node.getBoundingClientRect().width);

    expect(panelWidth).toBeLessThanOrEqual(1280);
    expect(panelWidth).toBeGreaterThan(600);
  });

  test("@ui state switches between button and progress", async ({ page }) => {
    await page.goto("/research-preview?scenario=idle");
    await expect(page.getByTestId("research-button")).toBeVisible();
    await expect(page.getByTestId("research-progress")).toHaveCount(0);

    await page.goto("/research-preview?scenario=active");
    await expect(page.getByTestId("research-progress")).toBeVisible();
  });
});
