import { defineConfig } from "@percy/cli";

export default defineConfig({
  version: 2,
  discovery: {
    allowedHostnames: ["localhost", "127.0.0.1"],
    launchOptions: {
      headless: true,
    },
    networkIdleTimeout: 300,
    requestHeaders: {
      "x-test-suite": "percy-visual-regression",
    },
  },
  snapshot: {
    widths: [375, 768, 1280, 1920],
    minHeight: 720,
    percyCSS: `
      /* Freeze animated elements to avoid diff noise */
      [data-animate], [data-testid="loading-spinner"] {
        animation: none !important;
        transition: none !important;
      }
    `,
  },
  upload: {
    concurrency: 3,
  },
});
