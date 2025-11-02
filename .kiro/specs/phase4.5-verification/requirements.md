# Phase 4.5: 前后端 UI 一致性验证 - 需求规范

## 文档信息

- **项目**: AI DeepResearch Agent
- **阶段**: Phase 4.5 - 验证与测试
- **版本**: 1.0
- **创建日期**: 2025-11-01
- **前置条件**: Phase 4 (45% 完成)

---

## 验证目标 🎯

**核心目标**: 将代码完成度 58% 提升到验证完成度 90%+

### 关键指标

| 指标 | 当前状态 | 目标状态 | 验收标准 |
|------|---------|---------|---------|
| E2E 测试覆盖率 | 15% | ≥80% | 所有核心流程有自动化测试 |
| 组件测试覆盖率 | 20% | ≥90% | 所有研究组件有单元测试 |
| 视觉回归测试 | 0% | 100% | 所有组件状态有基准快照 |
| 可访问性合规 | 未知 | 100% | WCAG 2.1 AA 零缺陷 |
| 性能指标达标率 | 未知 | ≥95% | Core Web Vitals 达标 |
| 总体代码覆盖率 | ~25% | ≥80% | Statement, Branch, Function 覆盖率 |

---

## 功能需求

### REQ-1: E2E 自动化测试 🔴 高优先级

**需求描述**: 建立完整的端到端测试体系，覆盖所有核心用户流程。

**验收标准**:
1. THE System SHALL 使用 Playwright 编写 15+ E2E 测试用例
2. THE System SHALL 使用 webapp-testing skill 辅助测试编写
3. THE System SHALL 覆盖研究完整流程（登录 → 研究 → 报告 → Artifact）
4. THE System SHALL 包含错误处理测试（网络错误、超时、取消）
5. THE System SHALL 包含响应式布局测试（桌面/移动端）
6. THE System SHALL 包含暗色模式测试
7. THE System SHALL 生成 HTML 测试报告（包含截图和视频）
8. THE System SHALL 在 CI/CD 中自动运行

**测试场景** (最少 15 个):
1. 用户登录 → 发送研究请求 → ResearchButton 出现
2. 点击按钮 → SSE 连接建立 → 进度实时更新
3. 研究完成 → Artifact 自动创建 → 报告显示
4. Follow-up 问题 → updateDocument 调用 → Artifact 更新
5. 错误处理 → 网络断开 → Retry 功能
6. Cancel 按钮 → 中断研究 → 状态清理
7. ResearchPanel sticky 定位验证
8. Framer Motion 动画效果测试
9. 响应式布局测试（3 种断点）
10. 暗色模式切换测试
11. 键盘导航测试
12. 数据库持久化验证
13. Progress JSONB 字段验证
14. 并发研究请求测试
15. SSE 重连机制测试

**优先级**: P0 - 阻碍生产部署

---

### REQ-2: 组件单元测试 🔴 高优先级

**需求描述**: 为所有 Phase 3 研究组件编写单元测试和快照测试。

**验收标准**:
1. THE System SHALL 使用 Vitest + @testing-library/react
2. THE System SHALL 覆盖以下组件：
   - ResearchButton (10+ 测试用例)
   - ResearchProgress (15+ 测试用例)
   - ResearchPanel (8+ 测试用例)
   - useResearchProgress Hook (12+ 测试用例)
3. THE System SHALL 包含快照测试（props 组合）
4. THE System SHALL 测试事件处理器
5. THE System SHALL 测试条件渲染逻辑
6. THE System SHALL 测试 Framer Motion 配置
7. THE System SHALL 达到 90%+ 组件覆盖率

**测试内容**:
- Props 验证
- 状态管理
- 事件处理
- 条件渲染
- 样式类名
- ARIA 属性
- 快照一致性

**优先级**: P0 - 阻碍生产部署

---

### REQ-3: 视觉回归测试 🟡 中优先级

**需求描述**: 建立视觉回归测试基准，确保 UI 外观一致性。

**验收标准**:
1. THE System SHALL 使用 Percy 或 Chromatic
2. THE System SHALL 为以下组件创建快照：
   - ResearchButton (4 种状态：idle, hover, disabled, loading)
   - ResearchProgress (4 种进度：0%, 50%, 100%, error)
   - ResearchPanel (5 个动画关键帧)
3. THE System SHALL 测试 4 种视口尺寸（375px, 768px, 1280px, 1920px）
4. THE System SHALL 测试亮/暗色模式
5. THE System SHALL 在 PR 中自动运行
6. THE System SHALL 达到 100% 基准覆盖率

**基准快照数量**: 40+ 张

**优先级**: P1 - 质量保障

---

### REQ-4: 可访问性测试 🟡 中优先级

**需求描述**: 确保所有组件符合 WCAG 2.1 AA 标准。

**验收标准**:
1. THE System SHALL 使用 axe-core + @axe-core/playwright
2. THE System SHALL 测试以下可访问性规则：
   - ARIA 标签完整性
   - 键盘导航支持
   - Focus 管理
   - 颜色对比度 ≥ 4.5:1
   - 屏幕阅读器兼容性
3. THE System SHALL 零可访问性缺陷
4. THE System SHALL 生成可访问性审计报告
5. THE System SHALL 在 CI 中阻止不合规 PR

**测试组件**:
- ResearchButton
- ResearchProgress
- ResearchPanel
- Chat 页面

**优先级**: P1 - 合规要求

---

### REQ-5: 端到端数据验证 🔴 高优先级

**需求描述**: 验证 UI 显示与数据库存储的一致性。

**验收标准**:
1. THE System SHALL 使用 @neondatabase/serverless 查询数据库
2. THE System SHALL 验证 research_tasks 表数据：
   - status 字段正确更新（pending → completed）
   - progress JSONB 包含完整事件历史
   - report 字段存储完整报告
   - userId/chatId 外键关联正确
3. THE System SHALL 验证 UI 显示与 DB 数据一致
4. THE System SHALL 清理测试数据
5. THE System SHALL 达到 100% 数据一致性

**验证点**:
- 研究状态
- 进度百分比
- 事件历史
- 报告内容
- 用户关联

**优先级**: P0 - 数据完整性

---

### REQ-6: 性能测试 🟢 低优先级

**需求描述**: 建立性能基准并持续监控。

**验收标准**:
1. THE System SHALL 使用 Lighthouse CI
2. THE System SHALL 达到以下指标：
   - LCP < 2.5s
   - FID < 100ms
   - CLS < 0.1
   - Time to Interactive < 3s
   - SSE 连接延迟 < 500ms
   - Research 完整流程 < 3min
3. THE System SHALL 在 CI 中运行性能测试
4. THE System SHALL 生成性能分析报告
5. THE System SHALL 达标率 ≥ 95%

**性能预算**:
- 首屏加载: 2.5s
- API 响应: 500ms
- SSE 首字节: 500ms
- 研究完成: 180s

**优先级**: P2 - 优化项

---

## 非功能需求

### NFR-1: 测试执行效率

**要求**:
- 单元测试: < 30 秒
- 集成测试: < 2 分钟
- E2E 测试（核心）: < 5 分钟
- E2E 测试（完整）: < 15 分钟
- 总执行时间: < 40 分钟

### NFR-2: 测试报告质量

**要求**:
- HTML 报告包含截图和视频
- 覆盖率报告高亮未覆盖代码
- Markdown 总结人类可读
- 性能报告包含优化建议
- 所有报告自动归档

### NFR-3: CI/CD 集成

**要求**:
- 所有测试在 GitHub Actions 运行
- PR 必须通过所有测试
- 自动发布测试报告到 GitHub Pages
- 失败测试自动通知
- 测试结果在 PR 中显示

### NFR-4: 可维护性

**要求**:
- 测试代码遵循 DRY 原则
- 使用 Page Object 模式
- 测试数据使用 Fixtures
- Helper 函数可复用
- 文档清晰完整

---

## 验收标准总结

### 阶段 1: 测试基础设施 (Day 1-5)

**验收标准**:
- [x] Playwright 配置完成
- [x] Percy/Chromatic 配置完成
- [x] axe-core 配置完成
- [x] Vitest 配置完成
- [x] 数据库 helper 函数创建
- [x] CI/CD pipeline 配置

### 阶段 2: 编写测试 (Day 6-10)

**验收标准**:
- [x] 15+ E2E 测试用例编写
- [x] 30+ 组件单元测试编写
- [x] 40+ 视觉回归快照创建
- [x] 可访问性测试编写
- [x] 数据验证测试编写
- [x] 性能测试配置

### 阶段 3: 执行和修复 (Day 11-15)

**验收标准**:
- [x] 所有测试通过率 ≥ 95%
- [x] 代码覆盖率 ≥ 80%
- [x] 可访问性零缺陷
- [x] 性能指标达标
- [x] 测试报告生成
- [x] 文档更新完成

---

## 依赖和约束

### 依赖

**技术依赖**:
- Playwright 1.40+
- Vitest 1.0+
- Percy CLI / Chromatic
- axe-core 4.8+
- @neondatabase/serverless
- Lighthouse CI

**数据依赖**:
- Neon 数据库可访问
- 测试用户账号
- 测试数据 fixtures

### 约束

**时间约束**:
- 总时间: 15 个工作日
- 每日工作: 6-8 小时
- 不可延期: 生产部署需要测试完成

**资源约束**:
- Percy 免费层: 5000 snapshots/月
- Neon 免费层: 0.5GB 存储
- GitHub Actions: 2000 分钟/月

---

## 风险和缓解

### 高风险

**R1: 测试编写时间超预期**
- 缓解: 优先 P0 测试，P1/P2 可后续补充
- 缓解: 使用 webapp-testing skill 提速
- 缓解: 复用现有测试模式

**R2: 测试不稳定（flaky tests）**
- 缓解: 使用显式等待而非固定延迟
- 缓解: 正确配置 timeout
- 缓解: 隔离测试数据

**R3: 覆盖率无法达标**
- 缓解: 聚焦核心流程
- 缓解: 接受 80% 作为最低标准
- 缓解: 记录未覆盖部分原因

### 中风险

**R4: Percy/Chromatic 免费额度用尽**
- 缓解: 仅对关键组件创建快照
- 缓解: 考虑自托管方案
- 缓解: 按需升级付费计划

**R5: CI 执行时间过长**
- 缓解: 并行化测试执行
- 缓解: 分级测试（快速 vs 完整）
- 缓解: 使用 Playwright sharding

---

## 成功标准

**Phase 4.5 完成的定义**:

1. ✅ 所有 P0 需求完成并验证
2. ✅ E2E 测试覆盖率 ≥ 80%
3. ✅ 组件测试覆盖率 ≥ 90%
4. ✅ 视觉回归基准建立（100%）
5. ✅ 可访问性零缺陷
6. ✅ 性能指标达标率 ≥ 95%
7. ✅ 所有测试报告生成
8. ✅ 文档完整更新
9. ✅ CI/CD pipeline 正常运行
10. ✅ 准备好进行生产部署

**质量门槛**:
- 测试通过率: ≥ 95%
- 代码覆盖率: ≥ 80%
- 可访问性缺陷: 0
- 性能指标达标率: ≥ 95%
- Flaky 测试率: < 5%

---

**文档版本**: 1.0
**创建日期**: 2025-11-01
**状态**: 待执行
**批准人**: AI DeepResearch Team
