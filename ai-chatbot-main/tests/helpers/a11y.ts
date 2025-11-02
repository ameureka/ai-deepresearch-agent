import AxeBuilder, {
  type AxeResults,
  type RunOptions,
} from "@axe-core/playwright";
import type { Page } from "@playwright/test";

export interface AccessibilityScanOptions {
  include?: string[];
  exclude?: string[];
  tags?: string[];
  runOptions?: RunOptions;
}

export async function runAccessibilityScan(
  page: Page,
  options: AccessibilityScanOptions = {}
): Promise<AxeResults> {
  const builder = new AxeBuilder({ page })
    .withTags(options.tags ?? ["wcag2a", "wcag2aa", "wcag21aa"]);

  if (options.include) {
    for (const selector of options.include) {
      builder.include(selector);
    }
  }

  if (options.exclude) {
    for (const selector of options.exclude) {
      builder.exclude(selector);
    }
  }

  return builder.analyze(options.runOptions);
}
