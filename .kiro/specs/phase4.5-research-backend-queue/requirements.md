# Phase 4.5: Research Backend Queue – 需求文档

## 文档信息
- **项目**: AI 研究助手
- **阶段**: Phase 4.5 – Research Backend Queue & Recovery
- **版本**: 1.0
- **创建日期**: 2025-11-02
- **状态**: 待实施

---

## 简介
本阶段旨在将研究流程从“浏览器 ↔ Next.js ↔ FastAPI”长连接解耦，改为“短连接提交 + 后台队列执行 + 状态查询”的模式。核心目标是消除 `UND_ERR_HEADERS_TIMEOUT` 等超时引发的前后端失步问题，使前端可以通过 `taskId` 随时恢复任务进度并展示最终报告。

---

## 范围
1. 研究任务通过 HTTP 短连接提交后立即返回 `taskId`。
2. 后台 worker 串行执行研究步骤，并在数据库中持久化事件、状态与报告。
3. 提供统一的状态查询接口，前端可轮询或订阅，断线后可恢复。
4. 允许未来扩展：任务重试、取消、多 worker、SSE 推送。

不在本阶段范围内：
- 并行执行步骤、任务优先级调度；
- 可视化队列监控后台；
- 完整的分布式队列（后续可引入 Redis/Celery）。

---

## 术语表
- **Task / research task**: 单次研究请求，由 prompt + chatId + model 参数构成。
- **Worker**: 后台执行研究步骤的线程/协程。
- **Queue**: 任务排队结构，可为内存队列或后续升级为 Redis/Celery。
- **Event**: 每个阶段产生的进度记录，包含 `type/message/timestamp` 等字段。
- **Progress Summary**: 针对前端展示的当前步骤、总步骤、已完成步骤汇总。
- **Recovery**: 前端在断网/刷新后，通过 `taskId` 恢复查看任务进度与报告。

---

## 功能需求

### R1 – 任务排队提交
1. WHEN 用户提交研究请求，系统 SHALL 在数据库创建任务记录，状态为 `queued`。
2. System SHALL 生成唯一 `taskId` 并返回给调用方（HTTP 202）。
3. System SHALL 将 `taskId` 推入后台队列等待执行。
4. IF 参数缺失或校验失败，System SHALL 返回 4xx 并不入队。

### R2 – 后台任务执行
1. Worker SHALL 从队列获取任务并将状态更新为 `running`。
2. Worker SHALL 串行执行原有 planner/research/writer/editor 流程。
3. Worker SHALL 在每个阶段写入事件 (`start/plan/progress/done/error/cancelled`)。
4. IF 执行成功，System SHALL 将状态更新为 `completed` 并保存报告。
5. IF 执行异常，System SHALL 捕获异常、写入 `error` 事件，并将状态设为 `failed`。

### R3 – 状态查询与恢复
1. System SHALL 提供 `GET /api/research/tasks/:taskId` 返回任务当前状态、事件、报告。
2. WHEN `taskId` 不存在，System SHALL 返回 404。
3. Response SHALL 包含 `status`, `progress`, `report`, `queueInfo`, `createdAt`, `updatedAt`。
4. Events SHALL 保留历史，供前端重建时间线。
5. 前端刷新或重新发起查询时，System SHALL 不重复执行任务。

### R4 – 容错与可扩展性
1. System SHALL 在事件中记录连接错误、重试等信息。
2. System SHALL 允许未来添加 `cancel` 操作（本阶段可预留 API 占位）。
3. System SHALL 允许将队列替换为 Redis/Celery，而无需改动核心业务流程。

### R5 – 前端体验与可访问性
1. Research 面板（建议提示、进度卡片）SHALL 与聊天主体宽度保持一致（`max-w-3xl` 居中），在超宽屏不会占满整行。
2. “Research This Topic” 常驻按钮 WHEN prompt 为空或仅空白字符 MUST 处于禁用状态，并向用户提供提示；按钮在聊天输入工具栏中 SHALL 始终渲染，与附件、模型切换、发送按钮同一行展示。
3. 无论当前是否存在历史消息，只要用户在输入框键入可用内容，按钮 SHALL 即刻启用；初始空态下按钮保持禁用但可见，避免“凭空消失”的交互落差。
4. 进度空态（events 为空）SHALL 显示准备状态文案与基础动画，避免出现纯空白面板。
5. 队列状态提示 SHALL 使用紧凑样式（行内标签/副标题），展示入队时间与重试次数，并以“已排队 XX 秒/分钟”形式动态刷新；队列事件不再使用整卡占位。
6. 研究触发区域 SHOULD 与输入框或建议卡片同一视觉基线，或在输入框下方与发送按钮并列，保证操作路径直观。
7. Artifact 关闭行为 SHALL 仅隐藏视图，保留 `documentId/title/report` 以便从历史记录再次打开。
8. 研究报告完成后，系统 SHALL 在研究面板中保留可见的“查看完整报告/导出”入口，确保用户在关闭侧边报告视图后仍可随时重新打开；该入口在移动端同样必须可访问。
9. 历史记录视图 SHALL 暴露最近的研究任务，包括状态（queued/running/done/failed）、报告摘要与重新打开报告的操作（例如历史列表或“Recent research” 区块），以便刷新或切换会话后仍可恢复结果。
10. 完成态不得自动隐藏研究面板或销毁报告上下文；系统 SHALL 在刷新或重新加载后，通过 `taskId` 恢复 `status === "done"` 的研究记录并还原查看入口。
11. 排队计时 SHALL 在任务进入 `running/done/error` 状态时停止自增，并以“已排队 XX 秒/分钟（固定值）”形式展示，避免完成后仍持续增长。
12. 完成后的建议研究按钮（智能提示） SHOULD 在一定冷却期内隐藏或改为“查看历史研究”，防止用户误触发重复任务。
13. 移动端在侧栏折叠/展开、屏幕旋转后，研究进度面板 MUST 持续可见（`status !== "idle"` 时强制展示或通过全局状态恢复），并保证折叠/展开不会重置事件时间线。
14. 所有研究相关按钮、进度条与文本 MUST 满足 WCAG AA 对比度并支持键盘导航，以通过 Playwright a11y 测试。

---

## 非功能需求
1. **可用性**：任务提交应在 500ms 内返回；状态查询接口响应时间 < 200ms。
2. **可靠性**：Worker 崩溃时任务状态保持在 `running/failed`，重启后可重新入队。
3. **可维护性**：代码结构应模块化，便于替换队列实现、增加新事件类型。
4. **日志与监控**：需在日志中打印 `taskId + status`，便于排查队列阻塞。

---

## 成功度量
- 研究任务在网络抖动或断线情况下仍可通过 `taskId` 恢复结果。
- 用户端再未见 “Failed to connect to research backend” 错误；超时降到可控范围。
- 新流程对现有成本监控、代理调用准确性无负面影响。
