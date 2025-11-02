import { expect, type Page } from "@playwright/test";

export class ResearchPanelPage {
  constructor(private readonly page: Page) {}

  get panel() {
    return this.page.getByTestId("research-panel");
  }

  get progress() {
    return this.page.getByTestId("research-progress");
  }

  get startButton() {
    return this.page.getByTestId("research-button");
  }

  async waitForSuggestion() {
    await this.panel.waitFor({ state: "visible" });
    await expect(this.startButton).toBeVisible();
  }

  async startResearch() {
    await this.waitForSuggestion();
    await this.startButton.click();
  }

  async waitForStatus(status: "queued" | "running" | "done" | "error") {
    await this.page.waitForFunction((expected) => {
      const panel = document.querySelector("[data-testid='research-panel']");
      return panel?.getAttribute("data-status") === expected;
    }, status);
  }

  async cancel() {
    await this.page.getByRole("button", { name: "Cancel" }).click();
  }

  async retry() {
    await this.page.getByRole("button", { name: "Retry" }).click();
  }

  async getEventSummaries(): Promise<string[]> {
    const text = await this.progress.innerText();
    return text
      .split("\n")
      .map((entry) => entry.trim())
      .filter(Boolean);
  }
}
