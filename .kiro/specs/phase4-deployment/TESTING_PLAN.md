# AI DeepResearch Agent - 自动化测试计划

## 文档信息

- **项目**: AI DeepResearch Agent
- **版本**: 1.0
- **创建日期**: 2025-11-01
- **状态**: Phase 4.5 验证阶段
- **测试策略**: 自动化优先 + 多维度质量保障

---

## 测试目标 🎯

### 核心目标

1. **提升测试覆盖率**: 从当前 ~25% 提升到 ≥80%
2. **建立自动化测试体系**: E2E + 组件 + 视觉 + 可访问性
3. **保障前后端一致性**: UI 显示与数据库存储一致
4. **确保生产可靠性**: 所有关键路径通过自动化验证

### 测试覆盖率目标

| 测试类型         | 目标覆盖率 | 当前覆盖率 | 缺口    | 优先级 |
|--------------|-------|-------|-------|-----|
| E2E 测试       | 80%   | 15%   | -65%  | 🔴 高 |
| 组件单元测试       | 90%   | 20%   | -70%  | 🔴 高 |
| API 集成测试     | 70%   | 40%   | -30%  | 🟡 中 |
| 视觉回归测试       | 100%  | 0%    | -100% | 🟡 中 |
| 可访问性测试       | 100%  | 0%    | -100% | 🟢 低 |
| 性能测试         | ≥95%  | 0%    | N/A   | 🟢 低 |
| **总体代码覆盖率** | **80%** | **~25%** | **-55%** | **🔴 紧急** |

---

## 测试金字塔架构 🏗️

```
           E2E Tests (Playwright)           ← 15 个核心流程测试
        ─────────────────────────
       Integration Tests (API)              ← 20 个 API 集成测试
    ─────────────────────────────────
   Component Tests (Vitest + Snapshots)     ← 30+ 组件单元测试
 ───────────────────────────────────────
Visual Regression (Percy) + A11y (axe-core) ← 持续运行
```

### 测试层级说明

#### 1. E2E 测试（End-to-End）
- **工具**: Playwright + webapp-testing skill
- **范围**: 完整用户流程，从登录到研究报告生成
- **数量**: 15 个核心测试场景
- **运行时机**: 每次 PR + 部署前

#### 2. 集成测试（Integration）
- **工具**: Playwright + Neon serverless driver
- **范围**: 前后端 API 通信 + 数据库验证
- **数量**: 20 个 API 端点测试
- **运行时机**: 每次 commit

#### 3. 组件单元测试（Component Unit）
- **工具**: Vitest + @testing-library/react
- **范围**: React 组件逻辑和渲染
- **数量**: 30+ 组件测试
- **运行时机**: 开发时实时运行

#### 4. 视觉回归测试（Visual Regression）
- **工具**: Percy/Chromatic
- **范围**: UI 外观一致性
- **数量**: 所有核心组件的关键状态
- **运行时机**: 每次 PR

#### 5. 可访问性测试（Accessibility）
- **工具**: axe-core + @axe-core/playwright
- **范围**: WCAG 2.1 AA 合规性
- **数量**: 所有公开页面和组件
- **运行时机**: 每次 PR

---

## 技术栈配置 🛠️

### 安装依赖

```bash
cd ai-chatbot-main

# Playwright E2E 测试
pnpm add -D @playwright/test
pnpm add -D @microsoft/fetch-event-source  # SSE 支持

# 视觉回归测试 (Percy 推荐)
pnpm add -D @percy/cli @percy/playwright

# 可访问性测试
pnpm add -D @axe-core/playwright axe-core

# 组件测试
pnpm add -D vitest @testing-library/react @testing-library/jest-dom
pnpm add -D @testing-library/user-event

# 数据库验证
pnpm add -D @neondatabase/serverless

# 性能测试
pnpm add -D @lhci/cli

# 代码覆盖率
pnpm add -D @vitest/coverage-v8 c8
```

### 配置文件

#### `playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'test-results/playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'pnpm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

#### `vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['components/**', 'lib/**', 'hooks/**'],
      exclude: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}', 'tests/**'],
      all: true,
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80,
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
});
```

#### `percy.config.yml`

```yaml
version: 2
static:
  cleanUrls: true
snapshot:
  widths: [375, 768, 1280, 1920]
  minHeight: 1024
  percyCSS: |
    /* Hide dynamic content */
    [data-percy-hide] { display: none !important; }
```

#### `lighthouserc.js`

```javascript
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000'],
      numberOfRuns: 3,
      settings: {
        preset: 'desktop',
        onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
      },
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

---

## Playwright E2E 测试套件 🧪

### 测试场景设计（15 个核心场景）

基于 UI_DESIGN_REPORT.md 和真实用户流程设计。

#### 测试文件结构

```
tests/e2e/
├── auth.spec.ts                    # 认证测试
├── research-workflow.spec.ts       # 研究完整流程 ⭐ 新增
├── research-components.spec.ts     # 组件交互 ⭐ 新增
├── research-data.spec.ts           # 数据验证 ⭐ 新增
├── research-errors.spec.ts         # 错误处理
├── research-a11y.spec.ts           # 可访问性 ⭐ 新增
├── research-visual.spec.ts         # 视觉回归 ⭐ 新增
└── artifacts.spec.ts               # Artifact 集成
```

### 核心测试用例

#### 1. `research-workflow.spec.ts` - 完整研究流程 ⭐

```typescript
import { test, expect } from '@playwright/test';
import { dbHelper } from '../helpers/db';

test.describe('Research Workflow - 完整流程', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('/');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');
  });

  test('用户触发研究 → ResearchButton 出现 → 点击开始研究', async ({ page }) => {
    // 1. 发送研究请求
    await page.fill('[data-testid="chat-input"]', 'Can you research AI applications in healthcare?');
    await page.click('[data-testid="send-button"]');

    // 2. 等待 AI 回复包含研究关键词
    await expect(page.locator('text=/research|investigate/i')).toBeVisible({ timeout: 10000 });

    // 3. 验证 ResearchButton 出现在输入框上方（sticky 定位）
    const researchPanel = page.locator('[data-testid="research-panel"]');
    await expect(researchPanel).toBeVisible();

    const researchButton = researchPanel.locator('[data-testid="research-button"]');
    await expect(researchButton).toBeVisible();
    await expect(researchButton).toHaveText(/Start Research/i);

    // 4. 验证 sticky 定位（bottom-[72px] = 72px * 0.25rem = 18rem）
    const panelBox = await researchPanel.boundingBox();
    expect(panelBox).toBeTruthy();
    expect(panelBox!.y).toBeGreaterThan(0);  // 在视口内
  });

  test('点击 ResearchButton → SSE 连接 → 进度实时更新', async ({ page }) => {
    // ... (前置步骤同上)

    // 点击 Start Research 按钮
    await page.click('[data-testid="research-button"]');

    // 验证切换到 ResearchProgress 组件
    await expect(page.locator('[data-testid="research-progress"]')).toBeVisible({ timeout: 2000 });

    // 验证 START 事件
    await expect(page.locator('text=/Starting research/i')).toBeVisible();

    // 验证 PLAN 事件
    await expect(page.locator('text=/Planning research/i')).toBeVisible({ timeout: 10000 });

    // 验证进度条显示
    const progressBar = page.locator('[data-testid="progress-bar"]');
    await expect(progressBar).toBeVisible();

    // 验证进度百分比更新（至少达到 50%）
    await expect(async () => {
      const progressText = await page.locator('[data-testid="progress-percentage"]').textContent();
      const percentage = parseInt(progressText || '0');
      expect(percentage).toBeGreaterThanOrEqual(50);
    }).toPass({ timeout: 30000 });
  });

  test('研究完成 → Artifact 自动创建 → 报告显示', async ({ page }) => {
    // ... (前置步骤同上)

    // 等待研究完成（DONE 事件）
    await expect(page.locator('text=/Research completed/i')).toBeVisible({ timeout: 180000 }); // 3分钟超时

    // 验证进度条达到 100%
    await expect(page.locator('text=/100%/i')).toBeVisible();

    // 验证 Artifact 自动打开
    const artifactPanel = page.locator('[data-testid="artifact-panel"]');
    await expect(artifactPanel).toBeVisible({ timeout: 5000 });

    // 验证报告内容显示（Markdown 渲染）
    const artifactContent = page.locator('[data-testid="artifact-content"]');
    await expect(artifactContent).toContainText(/healthcare/i);

    // 验证 Artifact 类型为 "text"
    await expect(artifactPanel.locator('[data-type="text"]')).toBeVisible();

    // 验证 ResearchPanel 关闭
    await expect(page.locator('[data-testid="research-panel"]')).not.toBeVisible({ timeout: 3000 });
  });

  test('端到端数据验证 → 数据库存储正确', async ({ page }) => {
    // 触发研究并获取 taskId
    await page.click('[data-testid="research-button"]');

    // 从 DOM 中提取 taskId（假设前端显示在某个元素中）
    const taskId = await page.getAttribute('[data-testid="research-task-id"]', 'data-task-id');
    expect(taskId).toBeTruthy();

    // 等待研究完成
    await expect(page.locator('text=/Research completed/i')).toBeVisible({ timeout: 180000 });

    // 查询数据库验证
    const dbTask = await dbHelper.getResearchTask(taskId!);

    // 验证字段
    expect(dbTask).toBeTruthy();
    expect(dbTask.status).toBe('completed');
    expect(dbTask.report).toContain('healthcare');
    expect(dbTask.progress).toHaveProperty('events');
    expect(dbTask.progress.events.length).toBeGreaterThan(0);
    expect(dbTask.progress.completedSteps).toBe(dbTask.progress.totalSteps);
  });

  test('Follow-up 问题 → updateDocument 调用 → Artifact 更新', async ({ page }) => {
    // ... (完成首次研究)

    // 发送 follow-up 问题
    await page.fill('[data-testid="chat-input"]', 'Can you add more details about AI diagnostics?');
    await page.click('[data-testid="send-button"]');

    // 等待 AI 处理
    await page.waitForTimeout(2000);

    // 验证 Artifact 内容更新
    const artifactContent = page.locator('[data-testid="artifact-content"]');
    await expect(artifactContent).toContainText(/diagnostics/i, { timeout: 30000 });

    // 验证版本历史增加
    const versionCount = await page.locator('[data-testid="version-badge"]').textContent();
    expect(parseInt(versionCount || '1')).toBeGreaterThan(1);
  });
});
```

#### 2. `research-components.spec.ts` - 组件交互测试 ⭐

```typescript
test.describe('ResearchPanel 组件测试', () => {
  test('sticky 定位验证 - 始终在输入框上方', async ({ page }) => {
    const researchPanel = page.locator('[data-testid="research-panel"]');
    const chatInput = page.locator('[data-testid="chat-input"]');

    // 获取位置
    const panelBox = await researchPanel.boundingBox();
    const inputBox = await chatInput.boundingBox();

    // 验证 panel 在 input 上方
    expect(panelBox!.y + panelBox!.height).toBeLessThan(inputBox!.y);

    // 滚动页面，验证 sticky 行为
    await page.evaluate(() => window.scrollTo(0, 500));
    const panelBoxAfterScroll = await researchPanel.boundingBox();

    // sticky 定位应保持相对视口位置不变
    expect(panelBoxAfterScroll!.y).toBe(panelBox!.y);
  });

  test('Framer Motion 动画 - 滑入滑出效果', async ({ page }) => {
    const researchPanel = page.locator('[data-testid="research-panel"]');

    // 触发显示
    await page.click('[data-testid="research-button"]');

    // 验证动画属性（opacity: 0 → 1, y: 20 → 0）
    await expect(researchPanel).toHaveCSS('opacity', '1');

    // 关闭后验证淡出
    await page.click('[data-testid="close-research"]');
    await expect(researchPanel).not.toBeVisible();
  });

  test('响应式布局 - 移动端 vs 桌面端', async ({ page, viewport }) => {
    // 桌面端测试
    await page.setViewportSize({ width: 1280, height: 720 });
    const desktopPanel = page.locator('[data-testid="research-panel"]');
    const desktopWidth = (await desktopPanel.boundingBox())!.width;

    // 移动端测试
    await page.setViewportSize({ width: 375, height: 667 });
    const mobilePanel = page.locator('[data-testid="research-panel"]');
    const mobileWidth = (await mobilePanel.boundingBox())!.width;

    // 验证响应式宽度
    expect(mobileWidth).toBeLessThan(desktopWidth);
    expect(mobileWidth).toBeGreaterThan(300);  // 最小宽度
  });

  test('最大高度和滚动 - max-h-[400px]', async ({ page }) => {
    const researchProgress = page.locator('[data-testid="research-progress"]');

    // 触发长列表事件
    // ... (模拟多个进度事件)

    const progressBox = await researchProgress.boundingBox();

    // 验证最大高度约束（400px = 100rem）
    expect(progressBox!.height).toBeLessThanOrEqual(400);

    // 验证滚动条出现
    const isScrollable = await researchProgress.evaluate((el) => {
      return el.scrollHeight > el.clientHeight;
    });
    expect(isScrollable).toBe(true);
  });
});
```

#### 3. `research-errors.spec.ts` - 错误处理测试

```typescript
test.describe('错误处理和重试', () => {
  test('网络断开 → 错误提示 → Retry 按钮', async ({ page, context }) => {
    // 模拟网络离线
    await context.setOffline(true);

    // 尝试开始研究
    await page.click('[data-testid="research-button"]');

    // 验证错误提示
    await expect(page.locator('text=/Network error|Connection failed/i')).toBeVisible();

    // 验证 Retry 按钮出现
    const retryButton = page.locator('[data-testid="retry-button"]');
    await expect(retryButton).toBeVisible();

    // 恢复网络
    await context.setOffline(false);

    // 点击 Retry
    await retryButton.click();

    // 验证研究重新开始
    await expect(page.locator('text=/Starting research/i')).toBeVisible();
  });

  test('SSE 超时 → 超时错误 → 状态恢复', async ({ page }) => {
    // 触发研究
    await page.click('[data-testid="research-button"]');

    // 模拟长时间无响应（通过拦截网络请求）
    await page.route('**/api/research/stream', (route) => {
      // 延迟 6 分钟（超过 5 分钟 maxDuration）
      setTimeout(() => route.abort(), 360000);
    });

    // 验证超时错误
    await expect(page.locator('text=/Timeout|Request timed out/i')).toBeVisible({ timeout: 360000 });

    // 验证状态恢复为 idle
    await expect(page.locator('[data-testid="research-button"]')).toBeVisible();
  });

  test('Cancel 按钮 → 中断研究 → 清理状态', async ({ page }) => {
    // 开始研究
    await page.click('[data-testid="research-button"]');

    // 等待进入进行中状态
    await expect(page.locator('text=/Planning research/i')).toBeVisible();

    // 点击 Cancel
    await page.click('[data-testid="cancel-button"]');

    // 验证研究中断
    await expect(page.locator('[data-testid="research-panel"]')).not.toBeVisible();

    // 验证状态清理
    await expect(page.locator('[data-testid="research-button"]')).toBeVisible();
  });
});
```

#### 4. `research-a11y.spec.ts` - 可访问性测试 ⭐

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('可访问性测试 (WCAG 2.1 AA)', () => {
  test('ResearchButton 可访问性', async ({ page }) => {
    await page.goto('/');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('[data-testid="research-button"]')
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);

    // 验证 ARIA 标签
    const button = page.locator('[data-testid="research-button"]');
    await expect(button).toHaveAttribute('aria-label', /Start research/i);
    await expect(button).toHaveAttribute('role', 'button');

    // 验证键盘支持
    await button.focus();
    await expect(button).toBeFocused();
    await page.keyboard.press('Enter');
    // 验证触发研究
  });

  test('ResearchProgress 可访问性', async ({ page }) => {
    // 触发研究显示 progress
    // ...

    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('[data-testid="research-progress"]')
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);

    // 验证进度条 role
    const progressBar = page.locator('[data-testid="progress-bar"]');
    await expect(progressBar).toHaveAttribute('role', 'progressbar');
    await expect(progressBar).toHaveAttribute('aria-valuenow');
    await expect(progressBar).toHaveAttribute('aria-valuemin', '0');
    await expect(progressBar).toHaveAttribute('aria-valuemax', '100');

    // 验证状态公告（live region）
    const liveRegion = page.locator('[aria-live="polite"]');
    await expect(liveRegion).toBeVisible();
  });

  test('颜色对比度测试', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa', 'wcag21aa'])
      .analyze();

    // 确保无对比度违规
    const contrastViolations = accessibilityScanResults.violations.filter(
      (v) => v.id === 'color-contrast'
    );
    expect(contrastViolations).toEqual([]);
  });

  test('键盘导航测试', async ({ page }) => {
    await page.goto('/');

    // Tab 导航到 ResearchButton
    await page.keyboard.press('Tab');
    // ... (继续 Tab 直到聚焦到 ResearchButton)

    const button = page.locator('[data-testid="research-button"]');
    await expect(button).toBeFocused();

    // Enter 激活
    await page.keyboard.press('Enter');
    await expect(page.locator('[data-testid="research-progress"]')).toBeVisible();

    // Escape 关闭
    await page.keyboard.press('Escape');
    await expect(page.locator('[data-testid="research-panel"]')).not.toBeVisible();
  });
});
```

#### 5. `research-visual.spec.ts` - 视觉回归测试 ⭐

```typescript
import { test } from '@playwright/test';
import percySnapshot from '@percy/playwright';

test.describe('视觉回归测试 (Percy)', () => {
  test('ResearchButton - 4 种状态快照', async ({ page }) => {
    await page.goto('/');

    // 1. Idle 状态
    await percySnapshot(page, 'ResearchButton - Idle');

    // 2. Hover 状态
    await page.hover('[data-testid="research-button"]');
    await percySnapshot(page, 'ResearchButton - Hover');

    // 3. Disabled 状态（通过 props 控制）
    await page.evaluate(() => {
      document.querySelector('[data-testid="research-button"]')?.setAttribute('disabled', 'true');
    });
    await percySnapshot(page, 'ResearchButton - Disabled');

    // 4. Loading 状态
    await page.click('[data-testid="research-button"]');
    await page.waitForSelector('text=/Starting.../i');
    await percySnapshot(page, 'ResearchButton - Loading');
  });

  test('ResearchProgress - 进度状态快照', async ({ page }) => {
    // 触发研究
    await page.click('[data-testid="research-button"]');

    // 0% 快照
    await percySnapshot(page, 'ResearchProgress - 0%');

    // 50% 快照（等待进度更新）
    await page.waitForSelector('text=/50%/');
    await percySnapshot(page, 'ResearchProgress - 50%');

    // 100% 完成快照
    await page.waitForSelector('text=/100%/', { timeout: 180000 });
    await percySnapshot(page, 'ResearchProgress - 100%');

    // Error 状态快照（通过模拟错误）
    // ...
    await percySnapshot(page, 'ResearchProgress - Error');
  });

  test('ResearchPanel - 展开收起动画快照', async ({ page }) => {
    // 收起状态
    await percySnapshot(page, 'ResearchPanel - Collapsed');

    // 展开动画中间帧
    await page.click('[data-testid="research-button"]');
    await page.waitForTimeout(150);  // 动画一半
    await percySnapshot(page, 'ResearchPanel - Expanding');

    // 完全展开
    await page.waitForTimeout(150);
    await percySnapshot(page, 'ResearchPanel - Expanded');
  });

  test('响应式布局快照 - 桌面 vs 移动端', async ({ page }) => {
    // 桌面端
    await page.setViewportSize({ width: 1920, height: 1080 });
    await percySnapshot(page, 'ResearchPanel - Desktop', {
      widths: [1920, 1280],
    });

    // 平板
    await page.setViewportSize({ width: 768, height: 1024 });
    await percySnapshot(page, 'ResearchPanel - Tablet', {
      widths: [768],
    });

    // 移动端
    await page.setViewportSize({ width: 375, height: 667 });
    await percySnapshot(page, 'ResearchPanel - Mobile', {
      widths: [375],
    });
  });

  test('暗色模式快照', async ({ page }) => {
    // 切换到暗色模式
    await page.evaluate(() => {
      document.documentElement.classList.add('dark');
    });

    await page.click('[data-testid="research-button"]');
    await percySnapshot(page, 'ResearchPanel - Dark Mode');
  });
});
```

---

## 组件单元测试 (Vitest) 🧪

### 测试文件结构

```
tests/components/
├── research-button.test.tsx        ⭐ 新增
├── research-progress.test.tsx      ⭐ 新增
├── research-panel.test.tsx         ⭐ 新增
└── setup.ts                        # 测试配置
```

### 核心测试用例

#### 1. `research-button.test.tsx` ⭐

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResearchButton } from '@/components/research-button';

describe('ResearchButton 组件', () => {
  it('应该渲染正确的文本', () => {
    render(<ResearchButton onClick={() => {}} disabled={false} />);
    expect(screen.getByText(/Start Research/i)).toBeInTheDocument();
  });

  it('disabled 状态应该禁用按钮', () => {
    render(<ResearchButton onClick={() => {}} disabled={true} />);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('点击应该触发 onClick 回调', () => {
    const handleClick = vi.fn();
    render(<ResearchButton onClick={handleClick} disabled={false} />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('应该有正确的 ARIA 属性', () => {
    render(<ResearchButton onClick={() => {}} disabled={false} />);
    const button = screen.getByRole('button');

    expect(button).toHaveAttribute('aria-label');
    expect(button).toHaveAttribute('type', 'button');
  });

  it('Framer Motion 动画配置快照', () => {
    const { container } = render(<ResearchButton onClick={() => {}} disabled={false} />);
    expect(container.firstChild).toMatchSnapshot();
  });

  // 10 种 props 组合快照
  it.each([
    { disabled: false, loading: false },
    { disabled: true, loading: false },
    { disabled: false, loading: true },
    { disabled: true, loading: true },
  ])('快照测试 - props: %o', (props) => {
    const { container } = render(<ResearchButton onClick={() => {}} {...props} />);
    expect(container).toMatchSnapshot();
  });
});
```

#### 2. `research-progress.test.tsx` ⭐

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResearchProgress } from '@/components/research-progress';

describe('ResearchProgress 组件', () => {
  const mockEvents = [
    { type: 'start', message: 'Starting research', timestamp: '2025-11-01T10:00:00Z' },
    { type: 'plan', message: 'Planning steps', timestamp: '2025-11-01T10:00:05Z' },
    { type: 'progress', message: 'Searching sources', timestamp: '2025-11-01T10:00:10Z' },
  ];

  it('应该渲染所有事件', () => {
    render(
      <ResearchProgress
        events={mockEvents}
        status="researching"
        onCancel={() => {}}
        onRetry={() => {}}
      />
    );

    expect(screen.getByText('Starting research')).toBeInTheDocument();
    expect(screen.getByText('Planning steps')).toBeInTheDocument();
    expect(screen.getByText('Searching sources')).toBeInTheDocument();
  });

  it('应该计算正确的进度百分比', () => {
    const eventsWithProgress = [
      ...mockEvents,
      { type: 'done', message: 'Completed', timestamp: '2025-11-01T10:01:00Z' },
    ];

    render(
      <ResearchProgress
        events={eventsWithProgress}
        status="completed"
        onCancel={() => {}}
        onRetry={() => {}}
      />
    );

    // 4 events, 100% progress
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('error 状态应该显示 Retry 按钮', () => {
    render(
      <ResearchProgress
        events={mockEvents}
        status="error"
        onCancel={() => {}}
        onRetry={() => {}}
      />
    );

    expect(screen.getByText(/Retry/i)).toBeInTheDocument();
  });

  it('researching 状态应该显示 Cancel 按钮', () => {
    render(
      <ResearchProgress
        events={mockEvents}
        status="researching"
        onCancel={() => {}}
        onRetry={() => {}}
      />
    );

    expect(screen.getByText(/Cancel/i)).toBeInTheDocument();
  });

  it('点击 Cancel 应该触发回调', () => {
    const handleCancel = vi.fn();
    render(
      <ResearchProgress
        events={mockEvents}
        status="researching"
        onCancel={handleCancel}
        onRetry={() => {}}
      />
    );

    fireEvent.click(screen.getByText(/Cancel/i));
    expect(handleCancel).toHaveBeenCalledTimes(1);
  });

  // 15 种状态快照
  it.each([
    { events: [], status: 'idle' },
    { events: mockEvents, status: 'researching' },
    { events: mockEvents, status: 'completed' },
    { events: mockEvents, status: 'error' },
  ])('快照测试 - %o', ({ events, status }) => {
    const { container } = render(
      <ResearchProgress
        events={events}
        status={status as any}
        onCancel={() => {}}
        onRetry={() => {}}
      />
    );
    expect(container).toMatchSnapshot();
  });
});
```

#### 3. `research-panel.test.tsx` ⭐

```typescript
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { ResearchPanel } from '@/components/research-panel';

describe('ResearchPanel 组件', () => {
  it('isActive=false 应该显示 ResearchButton', () => {
    const { getByTestId } = render(
      <ResearchPanel
        isActive={false}
        onStartResearch={() => {}}
        events={[]}
        status="idle"
      />
    );

    expect(getByTestId('research-button')).toBeInTheDocument();
  });

  it('isActive=true 应该显示 ResearchProgress', () => {
    const { getByTestId } = render(
      <ResearchPanel
        isActive={true}
        onStartResearch={() => {}}
        events={[]}
        status="researching"
      />
    );

    expect(getByTestId('research-progress')).toBeInTheDocument();
  });

  it('应该有 sticky 定位 class', () => {
    const { container } = render(
      <ResearchPanel
        isActive={false}
        onStartResearch={() => {}}
        events={[]}
        status="idle"
      />
    );

    const panel = container.querySelector('[data-testid="research-panel"]');
    expect(panel).toHaveClass('sticky');
    expect(panel).toHaveClass('bottom-[72px]');
  });

  it('应该有最大高度 class', () => {
    const { container } = render(
      <ResearchPanel
        isActive={true}
        onStartResearch={() => {}}
        events={[]}
        status="researching"
      />
    );

    const panel = container.querySelector('[data-testid="research-panel"]');
    expect(panel).toHaveClass('max-h-[400px]');
    expect(panel).toHaveClass('overflow-y-auto');
  });

  it('AnimatePresence 配置快照', () => {
    const { container } = render(
      <ResearchPanel
        isActive={true}
        onStartResearch={() => {}}
        events={[]}
        status="researching"
      />
    );
    expect(container).toMatchSnapshot();
  });

  // 8 种场景快照
  it.each([
    { isActive: false, status: 'idle' },
    { isActive: true, status: 'researching' },
    { isActive: true, status: 'completed' },
    { isActive: true, status: 'error' },
  ])('快照测试 - %o', ({ isActive, status }) => {
    const { container } = render(
      <ResearchPanel
        isActive={isActive}
        onStartResearch={() => {}}
        events={[]}
        status={status as any}
      />
    );
    expect(container).toMatchSnapshot();
  });
});
```

---

## 端到端数据验证 🗄️

### 数据库查询辅助函数

#### `tests/helpers/db.ts`

```typescript
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.POSTGRES_URL!);

export const dbHelper = {
  async getResearchTask(taskId: string) {
    const [task] = await sql`
      SELECT * FROM research_tasks WHERE task_id = ${taskId}
    `;
    return task;
  },

  async getUserResearchTasks(userId: string) {
    return await sql`
      SELECT * FROM research_tasks WHERE user_id = ${userId} ORDER BY created_at DESC
    `;
  },

  async cleanupTestData(userId: string) {
    await sql`DELETE FROM research_tasks WHERE user_id = ${userId}`;
  },

  async verifyTaskProgress(taskId: string, expectedStatus: string) {
    const task = await this.getResearchTask(taskId);
    return task && task.status === expectedStatus;
  },

  async verifyProgressEvents(taskId: string) {
    const task = await this.getResearchTask(taskId);
    return task?.progress?.events || [];
  },
};
```

### 数据一致性测试用例

```typescript
test.describe('数据一致性验证', () => {
  test('UI 显示与数据库存储一致', async ({ page }) => {
    const testUserId = 'test-user-123';

    // 1. 触发研究
    await page.click('[data-testid="research-button"]');
    const taskId = await page.getAttribute('[data-testid="research-task-id"]', 'data-task-id');

    // 2. 等待研究完成
    await expect(page.locator('text=/Research completed/i')).toBeVisible({ timeout: 180000 });

    // 3. 从 UI 读取显示的进度
    const uiProgress = await page.locator('[data-testid="progress-percentage"]').textContent();
    const uiStatus = await page.locator('[data-testid="research-status"]').textContent();

    // 4. 从数据库查询
    const dbTask = await dbHelper.getResearchTask(taskId!);

    // 5. 验证一致性
    expect(dbTask.status).toBe(uiStatus?.toLowerCase());
    expect(uiProgress).toContain('100%');
    expect(dbTask.progress.completedSteps).toBe(dbTask.progress.totalSteps);

    // 6. 验证报告内容
    const uiReport = await page.locator('[data-testid="artifact-content"]').textContent();
    expect(dbTask.report).toContain(uiReport?.substring(0, 50));  // 验证前50字符匹配

    // 7. 清理测试数据
    await dbHelper.cleanupTestData(testUserId);
  });

  test('progress JSONB 字段包含完整事件历史', async ({ page }) => {
    const taskId = '...';

    // 等待研究完成
    await expect(page.locator('text=/Research completed/i')).toBeVisible({ timeout: 180000 });

    // 查询数据库
    const events = await dbHelper.verifyProgressEvents(taskId);

    // 验证事件完整性
    expect(events.length).toBeGreaterThan(0);
    expect(events[0].type).toBe('start');
    expect(events[events.length - 1].type).toBe('done');

    // 验证每个事件包含必需字段
    events.forEach((event: any) => {
      expect(event).toHaveProperty('type');
      expect(event).toHaveProperty('message');
      expect(event).toHaveProperty('timestamp');
    });
  });
});
```

---

## 性能测试 ⚡

### Lighthouse CI 配置

运行命令：

```bash
# 启动本地服务
pnpm run dev &

# 运行 Lighthouse CI
lhci autorun

# 查看报告
open .lighthouseci/
```

### 自定义性能指标

```typescript
// tests/performance/sse-latency.test.ts
test('SSE 连接延迟 < 500ms', async ({ page }) => {
  const startTime = Date.now();

  await page.click('[data-testid="research-button"]');

  // 等待第一个 SSE 事件
  await page.waitForSelector('text=/Starting research/i');

  const latency = Date.now() - startTime;
  expect(latency).toBeLessThan(500);
});

test('Research 完整流程 < 3 分钟', async ({ page }) => {
  const startTime = Date.now();

  await page.click('[data-testid="research-button"]');
  await page.waitForSelector('text=/Research completed/i', { timeout: 180000 });

  const duration = Date.now() - startTime;
  expect(duration).toBeLessThan(180000);  // 3 分钟
});
```

---

## 测试报告生成 📊

### 报告类型

1. **HTML 测试报告** (Playwright)
   - 路径: `test-results/playwright-report/index.html`
   - 包含截图、视频、trace 文件
   - 交互式查看每个测试步骤

2. **覆盖率报告** (Vitest)
   - 路径: `coverage/index.html`
   - 显示代码行、函数、分支覆盖率
   - 高亮未覆盖代码

3. **性能报告** (Lighthouse)
   - 路径: `.lighthouseci/report.html`
   - Core Web Vitals 指标
   - 性能优化建议

4. **Markdown 验证总结**
   - 路径: `.kiro/specs/phase4.5-verification/VERIFICATION_REPORT.md`
   - 人类可读的测试总结
   - 已知问题和改进建议

### 报告生成命令

```bash
# 运行所有测试并生成报告
pnpm run test:all

# 查看 HTML 报告
pnpm run test:report
```

---

## CI/CD 集成 ⚙️

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install

      - name: Run unit tests
        run: pnpm run test:unit

      - name: Run E2E tests
        run: pnpm run test:e2e
        env:
          POSTGRES_URL: ${{ secrets.POSTGRES_URL }}

      - name: Run Percy visual tests
        run: pnpm run percy:exec
        env:
          PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/

      - name: Publish test report
        uses: peaceiris/actions-gh-pages@v3
        if: always()
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./test-results/playwright-report
```

---

## 测试执行时间表 ⏱️

| 测试类型 | 预估时间 | 运行频率 |
|---------|---------|---------|
| 组件单元测试 | 30 秒 | 每次保存 |
| API 集成测试 | 2 分钟 | 每次 commit |
| E2E 测试（核心流程） | 5 分钟 | 每次 commit |
| E2E 测试（完整套件） | 15 分钟 | 每次 PR |
| 视觉回归测试 | 10 分钟 | 每次 PR |
| 可访问性测试 | 3 分钟 | 每次 PR |
| 性能测试 | 5 分钟 | 每次 PR + 部署前 |
| **总计（完整测试）** | **~40 分钟** | **部署前** |

---

## 下一步行动 🎯

### 立即执行（本周）

1. ✅ 创建 TESTING_PLAN.md（本文档）
2. 🔄 配置测试工具栈（Playwright + Percy + axe-core + Vitest）
3. 🔄 编写 15 个 E2E 测试用例（使用 webapp-testing skill）
4. 🔄 编写 30+ 组件单元测试

### 下周执行

5. 🔄 建立视觉回归测试基准
6. 🔄 配置可访问性测试
7. 🔄 配置性能测试
8. 🔄 执行完整测试并修复问题

### 最终验收

9. 🔄 生成测试报告（HTML + Markdown + 性能分析）
10. 🔄 达到目标覆盖率（≥80%）
11. 🔄 通过所有质量门槛
12. 🔄 准备生产部署

---

**文档版本**: 1.0
**创建时间**: 2025-11-01
**负责人**: AI DeepResearch Team
**状态**: 待执行
