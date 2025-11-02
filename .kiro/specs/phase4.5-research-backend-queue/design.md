# Phase 4.5: Research Backend Queue – 设计文档

## 1. 总体架构

```
Client -> Next.js API (/api/research/tasks) -> FastAPI Queue API
                                         \-> Task Status API (/api/research/tasks/:id)

FastAPI App
 ├─ Task Submission Endpoint (short-lived)
 ├─ Task Status Endpoint
 ├─ Queue Manager (queue.Queue / asyncio.Queue)
 └─ ResearchWorker Thread
      └─ run_research_task(task_id) – 调用 planner / executor / writer / editor
             ↳ persist_event(task_id, type, message, meta)
             ↳ update_task_status(task_id, status, report)
```

- 任务提交与执行解耦：HTTP 请求仅负责落库 + 入队；真正的研究流程在 `ResearchWorker` 中串行执行。
- 状态查询接口直接读取数据库，无需依赖活动连接；前端可轮询或通过后续的 SSE 订阅。

## 2. 关键组件

### 2.1 数据模型扩展
在 `research_tasks` 表新增/调整字段：

| 字段 | 类型 | 描述 |
|------|------|------|
| `status` | enum | `"queued" | "running" | "completed" | "failed" | "cancelled"` |
| `progress` | jsonb | `{ currentStep?, totalSteps?, completedSteps?, events: [...]} ` |
| `report` | text | 最终 Markdown 报告 |
| `queue_info` | jsonb (optional) | `{ enqueuedAt, startedAt, finishedAt, workerId, retryCount }` |
| `created_at` / `updated_at` / `completed_at` | timestamp | 记录关键时间点 |

事件结构示例：
```json
{
  "type": "progress",
  "message": "Research agent: searching Tavily…",
  "timestamp": "2025-11-02T03:23:31Z",
  "step": 2,
  "total": 7
}
```

### 2.2 队列与 Worker

- **Queue 实现**：首版使用 `queue.Queue()` 或 `asyncio.Queue()`；后续可替换为 Redis/Celery。
- **ResearchWorker**：
  - 在 FastAPI `startup` 时启动后台线程。
  - `while True` 从队列 `get()` taskId → 调用 `run_research_task`.
  - 每完成一个阶段写入事件、更新 `progress` & `status`。
  - 捕获异常并写 `error` 事件、`status="failed"`。
  - 可选择写 `queue_info.startedAt/finishedAt`。
- **线程安全**：Worker 内部为每个任务创建新的 SQLAlchemy session；使用 `SessionLocal()` 的 context manager。

### 2.3 API 流程

1. **POST /api/research/tasks**
   - 验证 body `{ prompt, chatId, model? }`。
   - 创建任务记录：`status="queued"`, 写入初始事件 `queued`.
   - 将 `taskId` 放入队列。
   - 返回 `202 { taskId, status: "queued" }`.

2. **GET /api/research/tasks/:taskId**
   - 查询 `research_tasks`。
   - 若存在：返回 `{ taskId, status, progress, report, createdAt, updatedAt }`.
   - 若不存在：返回 404。
   - 可扩展：支持 `?since=<timestamp>` 只返回增量事件。

3. **PATCH /api/research/tasks/:taskId` (可选)**
   - JSON `{ action: "cancel" }`.
   - 标记 `cancel_requested=true`，Worker 在下一循环检查后中止任务并写 `cancelled` 事件。

4. **SSE `/api/research/tasks/:taskId/stream` (未来扩展)**
   - 监听数据库/Redis PubSub，推送增量事件；当前阶段先使用轮询，接口预留。

### 2.4 核心逻辑调整

#### run_research_task(task_id)
1. 从数据库读取任务（获取 prompt/chatId/model）。
2. 将状态更新为 `running`，写 `start` 事件。
3. 调用 `planner_agent`，写 `plan` 事件。
4. 遍历步骤调用 `executor_agent_step`，写 `progress` 事件、更新 `completedSteps`。
5. 完成时写 `done` 事件，保存报告，状态更新为 `completed`。
6. 捕获异常时写 `error` 事件，并设置 `status=failed`。

#### persist_event(task_id, event)
1. 读取当前 `progress` JSON。
2. `events.append(event)`；更新 `currentStep/totalSteps/completedSteps`。
3. 保存回 `research_tasks`.

#### update_status(task_id, status, report?)
1. 更新 `status`、`report`、`updated_at`、`completed_at/failed_at` 等字段。

### 2.5 前端交互

1. `Start Research` → `POST /api/research/tasks`，记录 `taskId`。
2. `useResearchProgress` 使用 `setInterval` 轮询 `GET /api/research/tasks/:taskId`（2–3s）。
3. 根据 `status/events/report` 更新 UI。
   - `queued`: 显示“排队中…”
   - `running`: 根据事件绘制时间线
   - `completed`: 展示报告，允许下载/分享
   - `failed`: 提示错误，可点击 Retry（重新提交任务）
4. “View History” 按钮列出近期 taskId，供用户回看报告。
5. Research 建议面板与进度卡片沿用聊天主体的布局容器（`max-w-3xl` + `mx-auto`），大屏幕上不再铺满整行。
6. “Research This Topic” 常驻按钮在 prompt 为空时禁用，同时与输入框保持同一视觉基线（或与发送按钮并列），并给出空输入提示。
7. 进度空态显示占位文案（例如“正在准备研究…”）、骨架条和入队时间，直到收到首个事件；队列时间改用“已排队 XX 秒/分钟”动态刷新。
8. 队列状态使用紧凑型行内提示（Badge + 副标题），在事件时间线上展示 `queueInfo.enqueuedAt` 与 `retryCount`，避免大量留白。
9. Artifact 关闭按钮仅设置 `isVisible=false`，保持 `documentId/title/report` 等上下文，下次从历史记录点击即可恢复。
10. 研究完成后，`ResearchProgress` 顶部需保留“查看完整报告/复制/导出”操作区，调用 `setIsResearchReportOpen(true)` 或触发下载，确保关闭侧边栏后仍可回到完整内容；移动端同样需展示该入口。
11. 报告侧边栏关闭或页面刷新后，应用应根据 `taskId` 检测 `status === "done"` 的任务并自动恢复 CTA/可选自动打开报告；禁止在完成 2 秒后自动隐藏研究面板。
12. 队列计时：在 `status` 从 `queued` 过渡到其他状态时停止 `setInterval` 并冻结排队时长，可使用 `queueInfo.startedAt` / `finishedAt` 计算固定值；完成后在 UI 中显示静态文案，如“Queued for 1m 54s”。
13. 历史视图新增“最近研究”模块（或在侧栏卡片）展示近期任务：主题、状态、更新时间及“View report” 操作，点击后通过 `GET /api/research/tasks/:taskId` 拉取并打开报告侧栏。
14. 完成后 通过 `shouldShowResearchButton` 的逻辑加冷却：在任务状态为 `done` 的一段时间内不再展示自动推荐按钮，或改为提示“查看历史研究”，避免重复启动。
15. Progress/按钮组件遵循 WCAG AA：确保颜色对比度 > 4.5:1，并提供键盘焦点、ARIA 标签。

### 2.6 扩展与替换策略

- 队列实现可替换为 Redis（`redis-py` + pub/sub）或 Celery，需抽象 `enqueue_task`、`fetch_next_task`。
- 若使用 SSE：Worker 在写事件时发布到 Redis Channel，SSE endpoint 订阅 channel 推送。
- 多 worker：在队列表层限制并发数，每个 worker 独立进程；需防止共享资源冲突。

## 3. 数据流

1. **Submit**: Client → Next.js → FastAPI (POST) → DB insert → Queue enqueue → return taskId.
2. **Execute**: Worker (dequeue) → run_research_task → DB update events/status/report。
3. **Poll**: Client → Next.js → FastAPI (GET) → DB read → return JSON → 更新 UI。
4. **Retry**: 重复步骤 1，生成新 taskId。

## 4. 失败场景处理

| 场景 | 行为 |
|------|------|
| Worker 执行中崩溃 | 任务状态保持在 `running`，系统日志记录错误；队列可在重启后手动重入 |
| 队列 backlog 积压 | 任务长期停留在 `queued`，前端展示排队提示；需监控队列长度 |
| 数据库写失败 | 捕获异常并写入日志，同时保持任务在 `failed` 状态 |
| 前端断线 | 用户仍可通过 `GET /tasks/:id` 恢复进度；报告不会丢失 |

## 5. 安全与鉴权

- 所有 API 维持现有 Auth 机制：必须是登录用户才能提交任务。
- `taskId` 仅允许对应用户访问（`userId` 校验）。
- 队列内部不暴露额外信息，避免泄露用户数据。

## 6. 部署考量

- 初期使用单进程 FastAPI + 后台线程即可；若部署到多实例，需改用共享队列（Redis/Celery）。
- 确保 `Task Submission` 与 `Worker` 运行在同一容器/进程中，否则应通过消息队列同步。

## 7. 验收标准

- 任务提交 < 500ms 返回 `taskId`。
- 在 DeepSeek 长耗时或网络断线情况下，前端仍可通过 `taskId` 获取最终报告。
- 日志中能追踪 `taskId` 的状态变更：`queued -> running -> completed/failed`。
- 改造后旧功能（日志、成本追踪、报告生成）保持可用。
