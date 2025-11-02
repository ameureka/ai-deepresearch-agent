# Phase 4.5: Research Backend Queue – 执行计划

## 概览
- **负责人**: TBD
- **预计周期**: 1.5 – 2 周
- **依赖**: Phase 3 前端框架、Phase 2 API 标准化
- **成功标准**: 前端可通过 `taskId` 稳定恢复任务进度；不再出现 “Failed to connect to research backend”。

---

## 里程碑
1. **M1 – 后端排队基础完成**（后端提交接口 + worker + 状态查询 API）
2. **M2 – 前端轮询恢复上线**（Hook/UI 改造、历史面板、报告展示）
3. **M3 – 验证与文档**（测试用例、手动验证、开发指南更新）

---

## 任务拆分

### 阶段 A：后端基础（M1）
1. **抽象执行函数**
   - 将 `research_stream` 中的执行逻辑抽取为 `run_research_task(task_id)`。
   - 确保对 `planner_agent/executor_agent_step` 的调用不依赖 HTTP 上下文。
2. **构建队列与 worker**
   - 在 FastAPI `startup` 中初始化 `queue.Queue()`/`asyncio.Queue()`。
   - 启动 `ResearchWorker` 后台线程：循环 `get()` taskId → `run_research_task`.
   - 每个任务创建独立 SQLAlchemy session；处理异常。
3. **扩展数据模型**
   - 更新 `research_tasks` schema（status enum、progress JSON、queue_info 等）。
   - 在 Drizzle + SQLAlchemy 里提供 `create/update/get` 帮助方法。
4. **实现 API**
   - `POST /api/research/tasks`：验证参数、创建任务、写 `queued` 事件、入队。
   - `GET /api/research/tasks/:taskId`：返回最新状态与事件。
   - （可选）预留 `PATCH /tasks/:id { action: "cancel" }`，暂不实现逻辑。
5. **日志与监控**
   - 在 `backend.log` 中打印 `taskId + status` 变更。
   - 记录队列长度/worker 异常（可用 `logger.warning`）。

### 阶段 B：前端改造（M2）
1. **Hook 重构**
   - `useResearchProgress`：提交任务改为 `POST /api/research/tasks`。
   - 保存 `taskId`，定时轮询 `GET /api/research/tasks/:id`（2–3s）。
   - 根据响应更新 `events/status/report`，断线后可继续轮询。
2. **UI 更新**
   - `ResearchProgress` 展示排队/执行/完成/失败状态，支持查看 `connection_error` 等新事件。
   - `ResearchPanel` 与聊天主体对齐（`max-w-3xl`、居中），并在无事件时显示准备态骨架。
   - `ResearchPanel` 新增历史入口（列出近期任务 & 报告弹窗）。
   - `Retry` 按钮重新提交，获取新的 `taskId`。
   - 常驻 “Research This Topic” 按钮在无有效 prompt 时禁用，并给出提示。
   - 常驻按钮位置调整为与输入框同一视觉基线（或与发送按钮并列），保证操作路径顺畅。
   - 队列状态 UI 收紧为行内提示（展示入队时间、重试次数），并改为“已等待 XX 秒/分钟”的动态显示。
   - 研究完成态在面板上保留“View full report / Copy / Export” 按钮，点击后重新打开报告侧栏或触发下载，移动端需提供等效入口。
   - 移除 “完成 2 秒后自动隐藏面板” 逻辑，改为在用户手动关闭前保持面板存在；刷新或重新加载时根据 `taskId` 恢复完成状态与 CTA。
   - 侧栏/历史页增加 “Recent Research” 区块，展示最新任务列表（主题、状态、更新时间），操作按钮可通过 `taskId` 重新打开报告侧栏。
   - 队列计时在状态转换后冻结：`Queued` → 其他状态时停止自增，优先使用 `queueInfo.startedAt/completedAt` 计算静态时长。
   - 自动推荐按钮执行冷却策略：任务完成后隐藏/替换智能提示，避免重复触发研究。
3. **报告展示**
   - 若 `status === "completed"`，自动打开 `ResearchReportViewer`。
   - 支持用户刷新后从历史任务重新查看报告。
   - Artifact 关闭仅隐藏视图，保留 `documentId/title/report`，确保历史列表可重新打开。
4. **错误提示**
   - 当 `status === "failed"`，展示最后一条错误事件信息。
   - 如果任务仍在后台执行但轮询失败，提示用户稍候再查看历史。
5. **可访问性**
   - 调整按钮、进度条颜色对比度，补足 ARIA 属性与键盘焦点。
   - 更新 Playwright a11y 脚本（`e2e/research-a11y.test.ts`）并确保通过。
6. **移动端体验**
   - 确保在移动布局下（折叠侧栏、旋转屏幕）`status !== "idle"` 时进度面板仍可见，必要时展示“研究进行中”浮层或入口。

### 阶段 C：验证与文档（M3）
1. **自动化测试**
   - 后端：`run_research_task` 正常/异常路径单测；`POST` + `GET` API 集成测试。
   - 前端：`useResearchProgress` 单元测试（mock fetch）；Playwright 场景测试（提交→轮询→展示报告）。
2. **手动验证**
   - 模拟 DeepSeek 超时/网络断线，确认前端能通过 `taskId` 恢复结果。
   - 测试多个任务并发提交，观察队列行为。
3. **文档更新**
   - README / 开发指南加入新 API & 队列说明。
   - 在 `.kiro/specs` 记录实施过程（Phase 4.5 实施报告）。
   - 补充 UI 改造说明（宽度、按钮禁用逻辑、队列提示、Artifact 行为）。

---

## 风险 & 缓解
| 风险 | 缓解策略 |
|------|----------|
| Worker 崩溃导致任务卡住 | 在日志中记录 `taskId` 进度，支持手动重入队列；后续考虑持久化队列 |
| 队列积压 | 监控队列长度；必要时增加 worker 或降级排队提示 |
| 前端轮询压力 | 控制轮询频率；未来升级为 SSE PubSub |
| 数据库事件过多 | 可对 `events` 做分页或限制长度 |

---

## 交付物
- 更新后的 FastAPI 代码（队列 + API + Worker）。
- 前端 Hook/UI 改造，支持 `taskId` 恢复。
- 自动化测试用例 & 手动验证记录。
- 更新后的开发文档 / Readme。
