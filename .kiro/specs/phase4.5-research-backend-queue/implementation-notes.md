# Phase 4.5 Implementation Notes

## 2025-11-02 — Backend Queue Foundation

### 已完成内容
- 新增 `ResearchTask` SQLAlchemy 模型（映射 Drizzle `research_tasks` 表）。
- 引入全局队列 `research_task_queue` 与后台线程 `ResearchWorker`，在应用启动/关闭时自动拉起或释放。
- 抽取 `run_research_task`，串行执行 planner/researcher/writer 流程，并将进度/事件写入 `research_tasks.progress`。
- 新增 `POST /api/research/tasks`：接受 `taskId/prompt/model`，重置任务状态为 `queued` 并入队。
- 新增 `GET /api/research/tasks/{taskId}`：返回最新 `status/progress/report`，供前端轮询。
- 事件结构统一包含 `type/message/timestamp`，支持 `queued/start/plan/progress/done/error`。
- 记录详细日志，便于追踪任务流转。

### 待处理 / 后续步骤
- 前端 Hook/UI 切换到新 API（轮询或 SSE）并联动进度展示。
- 实现 Retry/历史面板等交互。
- 自动化测试 & 手动验证队列行为、错误恢复。

---

## 2025-11-02 — 队列元数据与前端状态同步

- 扩展 `research_tasks` 表：新增 `queue_info / started_at / completed_at / failed_at` 列，并将 `status` 默认值更新为 `queued`；补充迁移脚本将旧状态 (`pending`, `planning`, `researching`, `writing`, `streaming`) 归一到新枚举。
- FastAPI：
  - `enqueue_research_task` 复位队列元数据，记录入队时间与重试次数。
  - `run_research_task` 在运行/完成/失败时写入 `queue_info` 及时间戳，并通过 `/api/research/tasks/{id}` 暴露 `queueInfo / startedAt / completedAt / failedAt` 字段。
  - 响应序列化时提供队列信息，前端可解析。
- Next.js：
  - `POST /api/research/tasks` 在排队失败时补写 `queueInfo.failedAt`。
  - `GET /api/research/tasks/[taskId]` 透传新的时间戳与队列信息。
  - `useResearchProgress` 改为状态机 `idle → queued → running → done/error`，并缓存 `queueInfo`；兼容旧状态 `pending/planning/researching/writing`。
  - `ResearchProgress`/`ResearchPanel`/`Chat` UI 同步：新增排队提示、重试计数、取消逻辑重置 `showResearchUI`。
- 测试：
  - 更新组件快照与 Playwright 辅助类，统一使用 `running` 状态。
  - 新增队列信息渲染单测，确保 `Enqueued at/Retry attempt` 文案存在。

后续仍需：补充端到端回归（长耗时/失败场景）与文档说明。

---

## 2025-11-03 — UI 抛光与可访问性补强

- Research 建议面板改为居中布局（`mx-auto w-full max-w-3xl px-4`），保证与聊天消息、输入框宽度一致。
- `ResearchPanel` 在 events 为空时添加占位骨架与文案（例如“正在准备研究…”），避免出现纯白空态。
- 常驻 “Research This Topic” 按钮与 `ResearchButton` 组件增加空 prompt 防御：`disabled` 状态 + 交互提示。
- 进度视图中将队列提示收紧为行内提示（Badge + timestamp），并利用 `queueInfo.retryCount/enqueuedAt` 展示具体信息。
- Artifact 关闭行为改为仅隐藏 `isVisible`，保留文档上下文，支持从历史列表再次打开。
- 调整按钮/进度条配色满足 WCAG AA，对焦点态、ARIA 标签做补充；同步更新 Playwright a11y 用例及快照。

---

## 2025-11-04 — 报告回溯能力与历史入口规划

- 用户反馈：完成后关闭报告侧栏无法再次打开，历史记录也缺少对应入口。
- 设计追加：
  - `ResearchProgress` 完成态保留 CTA（View full report / Copy / Export），移动端保持可达性。
  - 移除自动隐藏研究面板的定时逻辑，基于 `taskId` 恢复完成状态并允许刷新后继续查看。
  - 侧栏或专用“Recent Research” 模块列出最近任务，含状态、更新时间与打开报告的操作。
- 实施 TODO：
  - 更新 `useResearchProgress` 使 `status === "done"` 时始终保留 `report` 于 state，并在初始轮询时恢复 CTA。
  - 扩展 `ResearchProgress`，在完成状态渲染操作按钮并连接到 `ResearchReportViewer`。
  - 引入历史列表 UI（侧栏或面板内 tabs），消费 `/api/research/tasks/:taskId` 数据并支持再次打开报告。
  - 增加单元/端到端用例覆盖：关闭侧栏后重新打开、刷新页面后仍可访问报告、历史入口跳转正确。
  - 处理排队计时：状态转为 `running/done` 时停止自增，展示静态时长。
  - 对自动推荐按钮添加冷却或替换逻辑，避免完成后立即再次提示。
