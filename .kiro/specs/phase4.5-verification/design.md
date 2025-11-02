# Phase 4.5: 前后端 UI 一致性验证 - 测试架构设计

## 文档信息

- **项目**: AI DeepResearch Agent
- **阶段**: Phase 4.5 - 验证与测试
- **版本**: 1.0
- **创建日期**: 2025-11-01
- **架构师**: AI DeepResearch Team

---

## 测试架构概览 🏗️

### 测试金字塔

```
                    E2E Tests                    ← 15 tests (Slow, High Value)
                 ─────────────────
              Integration Tests                  ← 20 tests (Medium Speed)
           ─────────────────────────
         Component Unit Tests                    ← 30+ tests (Fast)
      ─────────────────────────────────
    Visual Regression + Accessibility            ← Continuous (Percy + axe)
  ───────────────────────────────────────
```

**设计原则**:
1. **自动化优先**: 最大化自动化测试覆盖
2. **快速反馈**: 快速测试频繁运行，慢速测试定期运行
3. **分层隔离**: 每层测试独立运行，互不依赖
4. **真实环境**: E2E 测试使用真实数据库和 API

---

## 技术栈架构 🛠️

### 核心测试框架

```yaml
前端测试:
  E2E 测试:
    框架: Playwright 1.40+
    辅助: webapp-testing skill (MCP)
    浏览器: Chromium, Firefox, WebKit
    运行器: @playwright/test

  组件测试:
    框架: Vitest 1.0+
    库: @testing-library/react
    渲染: jsdom environment
    快照: vitest snapshots

  视觉回归:
    工具: Percy (推荐) / Chromatic
    集成: @percy/playwright
    存储: Percy Dashboard / Git LFS

  可访问性:
    核心: axe-core 4.8+
    集成: @axe-core/playwright
    标准: WCAG 2.1 AA

后端验证:
  数据库查询:
    驱动: @neondatabase/serverless
    ORM: Drizzle (用于类型)
    连接: Neon Serverless Driver

  API 测试:
    工具: Playwright (API testing)
    验证: Response schemas
    Mock: MSW (如需要)

性能测试:
  工具: Lighthouse CI
  指标: Core Web Vitals
  报告: HTML + JSON

覆盖率:
  工具: @vitest/coverage-v8, c8
  报告: HTML, LCOV, JSON
  CI 集成: Codecov / Coveralls
```

---

## 测试环境架构 🌍

### 环境分层

```
┌─────────────────────────────────────────────────┐
│ 本地开发环境 (Local Development)                  │
├─────────────────────────────────────────────────┤
│ - Frontend: localhost:3000 (Vercel Dev)        │
│ - Backend: localhost:8000 (Python uvicorn)     │
│ - Database: Neon Dev Database (shared)         │
│ - 用途: 快速测试开发，单元测试                     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ CI 环境 (GitHub Actions)                        │
├─────────────────────────────────────────────────┤
│ - Frontend: GitHub Actions Runner              │
│ - Backend: GitHub Actions Runner               │
│ - Database: Neon Dev Database (isolated)       │
│ - 用途: PR 验证，完整测试套件                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Staging 环境 (Vercel Preview)                   │
├─────────────────────────────────────────────────┤
│ - Frontend: preview-xxx.vercel.app             │
│ - Backend: staging.onrender.com (可选)         │
│ - Database: Neon Staging Database              │
│ - 用途: 生产前验证，手动测试                       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 生产环境 (Production)                            │
├─────────────────────────────────────────────────┤
│ - Frontend: your-app.vercel.app                │
│ - Backend: backend.onrender.com               │
│ - Database: Neon Production Database          │
│ - 用途: 生产监控，冒烟测试                         │
└─────────────────────────────────────────────────┘
```

---

## 测试数据管理 📊

### 数据策略

**测试用户**:
```typescript
const TEST_USERS = {
  basic: {
    email: 'test-basic@example.com',
    password: 'Test1234!',
    role: 'user',
  },
  admin: {
    email: 'test-admin@example.com',
    password: 'Admin1234!',
    role: 'admin',
  },
};
```

**Fixtures**:
```typescript
// tests/fixtures/research-events.ts
export const mockResearchEvents = [
  { type: 'start', message: 'Starting research', timestamp: '2025-11-01T10:00:00Z' },
  { type: 'plan', message: 'Planning steps', timestamp: '2025-11-01T10:00:05Z' },
  // ...
];

// tests/fixtures/research-reports.ts
export const mockReport = `
# AI in Healthcare

## Introduction
Artificial Intelligence (AI) is transforming healthcare...
`;
```

**数据清理策略**:
```typescript
// tests/helpers/cleanup.ts
export async function cleanupTestData(userId: string) {
  await db.delete(researchTasks).where(eq(researchTasks.userId, userId));
  await db.delete(chats).where(eq(chats.userId, userId));
  // 保留用户记录用于复用
}
```

---

## E2E 测试架构 🎭

### Page Object 模式

```typescript
// tests/pages/ChatPage.ts
export class ChatPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/');
  }

  async login(email: string, password: string) {
    await this.page.fill('[name="email"]', email);
    await this.page.fill('[name="password"]', password);
    await this.page.click('button[type="submit"]');
  }

  async sendMessage(message: string) {
    await this.page.fill('[data-testid="chat-input"]', message);
    await this.page.click('[data-testid="send-button"]');
  }

  async waitForResearchButton() {
    return this.page.waitForSelector('[data-testid="research-button"]');
  }

  async startResearch() {
    await this.page.click('[data-testid="research-button"]');
  }

  async waitForResearchComplete() {
    await this.page.waitForSelector('text=/Research completed/i', { timeout: 180000 });
  }

  async getArtifactContent() {
    return this.page.locator('[data-testid="artifact-content"]').textContent();
  }
}
```

### 测试组织结构

```
tests/
├── e2e/
│   ├── pages/                      # Page Objects
│   │   ├── ChatPage.ts
│   │   ├── ResearchPage.ts
│   │   └── ArtifactPage.ts
│   ├── fixtures/                   # 测试数据
│   │   ├── users.ts
│   │   ├── research-events.ts
│   │   └── reports.ts
│   ├── helpers/                    # 辅助函数
│   │   ├── db.ts
│   │   ├── auth.ts
│   │   └── cleanup.ts
│   └── specs/                      # 测试用例
│       ├── auth.spec.ts
│       ├── research-workflow.spec.ts
│       ├── research-components.spec.ts
│       ├── research-data.spec.ts
│       ├── research-errors.spec.ts
│       ├── research-a11y.spec.ts
│       └── research-visual.spec.ts
├── components/                     # 组件测试
│   ├── research-button.test.tsx
│   ├── research-progress.test.tsx
│   └── research-panel.test.tsx
├── lib/                           # 工具函数测试
│   └── research-utils.test.ts
└── setup.ts                       # 测试配置
```

---

## 组件测试架构 🧩

### 测试工具配置

```typescript
// tests/setup.ts
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// 自动清理
afterEach(() => {
  cleanup();
});

// Mock Framer Motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock fetch-event-source
vi.mock('@microsoft/fetch-event-source', () => ({
  fetchEventSource: vi.fn(),
}));
```

### 测试模式

**快照测试**:
```typescript
it('should match snapshot', () => {
  const { container } = render(<ResearchButton onClick={() => {}} disabled={false} />);
  expect(container).toMatchSnapshot();
});
```

**交互测试**:
```typescript
it('should handle click', async () => {
  const handleClick = vi.fn();
  render(<ResearchButton onClick={handleClick} />);

  await userEvent.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalled();
});
```

**状态测试**:
```typescript
it('should update progress', () => {
  const { rerender } = render(<ResearchProgress events={[]} status="idle" />);

  rerender(<ResearchProgress events={mockEvents} status="researching" />);
  expect(screen.getByText('Planning steps')).toBeInTheDocument();
});
```

---

## 视觉回归测试架构 📸

### Percy 集成

**工作流**:
```
1. 开发者提交 PR
   ↓
2. GitHub Actions 触发
   ↓
3. 运行 Playwright 测试
   ↓
4. Percy 捕获快照
   ↓
5. Percy 对比基准快照
   ↓
6. 差异显示在 PR 中
   ↓
7. 开发者批准/拒绝变更
```

**快照策略**:
```typescript
// 组件状态快照
await percySnapshot(page, 'ResearchButton - Idle');
await percySnapshot(page, 'ResearchButton - Hover');
await percySnapshot(page, 'ResearchButton - Disabled');
await percySnapshot(page, 'ResearchButton - Loading');

// 响应式快照
await percySnapshot(page, 'ResearchPanel - Desktop', {
  widths: [1920, 1280],
});
await percySnapshot(page, 'ResearchPanel - Mobile', {
  widths: [375],
});
```

---

## 可访问性测试架构 ♿

### axe-core 集成

**自动化检查**:
```typescript
import AxeBuilder from '@axe-core/playwright';

test('should have no accessibility violations', async ({ page }) => {
  await page.goto('/');

  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

**自定义规则**:
```typescript
const accessibilityScanResults = await new AxeBuilder({ page })
  .include('[data-testid="research-panel"]')
  .exclude('[data-testid="third-party-widget"]')
  .disableRules(['color-contrast'])  // 如果有特殊原因
  .analyze();
```

---

## 性能测试架构 ⚡

### Lighthouse CI 集成

**配置**:
```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3,
      settings: {
        preset: 'desktop',
      },
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

**自定义指标**:
```typescript
// 测量 SSE 连接延迟
test('SSE connection latency', async ({ page }) => {
  await page.evaluate(() => {
    performance.mark('sse-start');
  });

  await page.click('[data-testid="research-button"]');
  await page.waitForSelector('text=/Starting research/i');

  const latency = await page.evaluate(() => {
    performance.mark('sse-end');
    performance.measure('sse-latency', 'sse-start', 'sse-end');
    const measure = performance.getEntriesByName('sse-latency')[0];
    return measure.duration;
  });

  expect(latency).toBeLessThan(500);
});
```

---

## CI/CD 架构 ⚙️

### GitHub Actions 工作流

```yaml
name: Tests

on:
  pull_request:
  push:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
      - run: pnpm install
      - run: pnpm run test:unit
      - run: pnpm run test:coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
      - run: pnpm install
      - run: npx playwright install --with-deps
      - run: pnpm run test:e2e
        env:
          POSTGRES_URL: ${{ secrets.POSTGRES_URL_TEST }}
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: test-results/

  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - run: pnpm install
      - run: npx playwright install --with-deps
      - run: pnpm run percy:exec
        env:
          PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}

  accessibility-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - run: pnpm install
      - run: pnpm run test:a11y

  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - run: pnpm install
      - run: pnpm run build
      - run: lhci autorun
```

### 测试分级策略

**快速测试** (每次 commit):
- 单元测试 (~30秒)
- 核心 E2E 测试 (~3分钟)

**完整测试** (每次 PR):
- 所有单元测试
- 完整 E2E 套件
- 视觉回归测试
- 可访问性测试
- 性能测试

**定期测试** (每日):
- 端到端数据验证
- 性能基准测试
- 安全扫描

---

## 报告架构 📊

### 多格式报告

```
test-results/
├── playwright-report/          # HTML 交互式报告
│   ├── index.html
│   ├── trace-*.zip            # 测试 trace 文件
│   └── screenshots/
├── coverage/                   # 覆盖率报告
│   ├── index.html
│   └── lcov.info
├── lighthouse/                 # 性能报告
│   └── report.html
└── accessibility/              # 可访问性报告
    └── violations.json
```

### 报告聚合

```typescript
// scripts/generate-test-report.ts
import { generateMarkdownReport } from './reporters/markdown';
import { generateHTMLSummary } from './reporters/html';

async function main() {
  const playwrightResults = await readJSON('test-results/results.json');
  const coverageResults = await readJSON('coverage/coverage-summary.json');
  const lighthouseResults = await readJSON('lighthouse/report.json');

  // 生成 Markdown 总结
  await generateMarkdownReport({
    playwright: playwrightResults,
    coverage: coverageResults,
    lighthouse: lighthouseResults,
    outputPath: '.kiro/specs/phase4.5-verification/VERIFICATION_REPORT.md',
  });

  // 生成 HTML Dashboard
  await generateHTMLSummary({
    playwright: playwrightResults,
    coverage: coverageResults,
    lighthouse: lighthouseResults,
    outputPath: 'test-results/dashboard.html',
  });
}
```

---

## 测试隔离和并行化 🚀

### 测试隔离策略

**数据隔离**:
```typescript
test.beforeEach(async ({ page }) => {
  // 为每个测试创建独立用户
  const testUser = await createTestUser();
  await login(page, testUser.email, testUser.password);
});

test.afterEach(async ({ page }) => {
  // 清理测试数据
  await cleanupTestData(currentUserId);
});
```

**并行化配置**:
```typescript
// playwright.config.ts
export default defineConfig({
  workers: process.env.CI ? 2 : 4,  // CI 环境限制并发
  fullyParallel: true,
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // 并行运行多个浏览器
  ],
});
```

---

## 错误处理和重试 🔄

### Flaky 测试处理

**自动重试**:
```typescript
// playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  expect: {
    timeout: 10000,  // 断言超时
  },
  use: {
    actionTimeout: 15000,  // 操作超时
    navigationTimeout: 30000,  // 导航超时
  },
});
```

**显式等待**:
```typescript
// 推荐：显式等待
await page.waitForSelector('[data-testid="research-progress"]');

// 避免：固定延迟
await page.waitForTimeout(3000);  // ❌ Bad practice
```

---

## 质量门槛 ✅

### 自动化质量检查

```yaml
# 测试必须通过才能合并 PR
required_checks:
  - unit-tests
  - e2e-tests-core
  - accessibility-tests

# 覆盖率门槛
coverage_thresholds:
  statements: 80
  branches: 80
  functions: 80
  lines: 80

# 性能门槛
performance_budgets:
  lcp: 2500ms
  fid: 100ms
  cls: 0.1

# 可访问性门槛
accessibility:
  violations: 0
  incomplete: 0
```

---

## 成本优化 💰

### 免费层优化

**Percy**:
- 免费层: 5000 snapshots/月
- 优化: 仅对关键组件创建快照
- 策略: PR 运行，main 分支跳过

**GitHub Actions**:
- 免费层: 2000 分钟/月
- 优化: 并行化测试，减少总时间
- 策略: 快速测试优先，定期运行完整测试

**Neon**:
- 免费层: 0.5GB 存储
- 优化: 定期清理测试数据
- 策略: 使用独立测试数据库

---

## 安全性考虑 🔒

### 测试数据安全

**敏感数据处理**:
```typescript
// ❌ 不要在代码中硬编码
const API_KEY = 'sk-xxx';

// ✅ 使用环境变量
const API_KEY = process.env.TEST_API_KEY;

// ✅ 使用 GitHub Secrets
env:
  POSTGRES_URL: ${{ secrets.POSTGRES_URL_TEST }}
```

**测试隔离**:
- 使用独立的测试数据库
- 测试用户有限权限
- 定期轮换测试凭据

---

**文档版本**: 1.0
**创建日期**: 2025-11-01
**架构师**: AI DeepResearch Team
**状态**: 待实施
