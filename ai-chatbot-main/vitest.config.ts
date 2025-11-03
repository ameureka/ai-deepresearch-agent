import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    // Test environment
    environment: "jsdom",

    // Setup files
    setupFiles: ["./tests/setup.ts"],

    // Global test APIs
    globals: true,

    // Coverage configuration
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html", "lcov"],
      reportsDirectory: "./coverage",
      exclude: [
        "node_modules/",
        "tests/",
        "*.config.*",
        "**/*.d.ts",
        "**/*.test.{ts,tsx}",
        "**/*.spec.{ts,tsx}",
        ".next/",
        "dist/",
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },

    // Test file patterns
    include: [
      "components/**/*.{test,spec}.{ts,tsx}",
      "lib/**/*.{test,spec}.{ts,tsx}",
      "hooks/**/*.{test,spec}.{ts,tsx}",
    ],

    // Exclude test utilities and mocks
    exclude: [
      "**/node_modules/**",
      "**/dist/**",
      "**/.next/**",
      "**/tests/**",
      "lib/ai/models.test.ts", // This is a mock file, not a test
    ],

    // Reporters
    reporters: ["verbose", "html", "json"],
    outputFile: {
      html: "./test-results/vitest-report/index.html",
      json: "./test-results/vitest-results.json",
    },

    // Timeouts
    testTimeout: 10000,
    hookTimeout: 10000,
  },

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
    },
  },
});
