module.exports = {
  ci: {
    collect: {
      startServerCommand:
        "NEXT_PUBLIC_ENABLE_RESEARCH_PREVIEW=true pnpm dev --port 3000",
      url: [
        "http://localhost:3000/",
        "http://localhost:3000/research-preview?scenario=active",
      ],
      numberOfRuns: 3,
      settings: {
        preset: "desktop",
        throttling: {
          rttMs: 40,
          throughputKbps: 10240,
          cpuSlowdownMultiplier: 1,
        },
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
    assert: {
      assertions: {
        "categories:performance": ["error", { minScore: 0.95 }],
        "categories:accessibility": ["warn", { minScore: 0.95 }],
        "categories:best-practices": ["warn", { minScore: 0.9 }],
        "categories:seo": ["warn", { minScore: 0.9 }],
        "largest-contentful-paint": ["error", { maxNumericValue: 2500 }],
        "first-input-delay": ["warn", { maxNumericValue: 100 }],
        "cumulative-layout-shift": ["error", { maxNumericValue: 0.1 }],
      },
    },
  },
};
