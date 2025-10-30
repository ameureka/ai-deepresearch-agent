# Phase 2: API 接口标准化 - 需求文档

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 2 - API 接口标准化
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **状态**: 待实施
- **依赖**: Phase 1 (DeepSeek 集成) 必须完成

---

## 简介

本文档定义了 Phase 2（API 接口标准化）的功能需求。该阶段的目标是为 Next.js 前端设计最小可用的标准化 API 接口，支持实时进度推送，采用 MVP 原则快速上线。

---

## 术语表

- **System**: FastAPI 研究助手后端系统
- **SSE**: Server-Sent Events，服务器推送事件
- **API Response**: 统一的 API 响应格式
- **Event Stream**: SSE 事件流
- **Research Task**: 研究任务
- **Progress Event**: 进度事件
- **Health Check**: 健康检查接口
- **Model List**: 可用模型列表接口
- **Global Error Handler**: 全局错误处理器
- **CORS**: 跨域资源共享

---

## 需求

### Requirement 1: 统一响应格式

**用户故事**: 作为前端开发者，我希望所有 API 接口返回统一的响应格式，以便简化前端处理逻辑

#### 验收标准

1. THE System SHALL 定义统一的 ApiResponse 模型
2. THE ApiResponse SHALL 包含 success 字段（布尔类型）
3. THE ApiResponse SHALL 包含 data 字段（可选，任意类型）
4. THE ApiResponse SHALL 包含 error 字段（可选，字符串类型）
5. WHEN API 调用成功时，THE System SHALL 返回 success=true 和 data
6. WHEN API 调用失败时，THE System SHALL 返回 success=false 和 error

### Requirement 2: 全局错误处理

**用户故事**: 作为系统管理员，我希望系统能够统一处理所有错误，以便提供一致的错误响应

#### 验收标准

1. THE System SHALL 实现全局异常处理器
2. WHEN 发生未捕获的异常时，THE System SHALL 返回 500 状态码和错误信息
3. WHEN 发生 HTTP 异常时，THE System SHALL 返回对应的状态码和错误信息
4. THE System SHALL 记录所有错误到日志
5. THE System SHALL 不在错误响应中暴露敏感信息（如堆栈跟踪）

### Requirement 3: 健康检查接口

**用户故事**: 作为运维人员，我希望有一个健康检查接口，以便监控服务状态

#### 验收标准

1. THE System SHALL 提供 GET /api/health 接口
2. WHEN 服务正常运行时，THE System SHALL 返回 200 状态码
3. THE System SHALL 返回 {"success": true, "data": {"status": "ok"}}
4. THE System SHALL 在 100 毫秒内响应健康检查请求
5. THE System SHALL 不需要认证即可访问健康检查接口

### Requirement 4: 模型列表接口

**用户故事**: 作为前端开发者，我希望能够获取可用的模型列表，以便在 UI 中展示

#### 验收标准

1. THE System SHALL 提供 GET /api/models 接口
2. THE System SHALL 返回所有可用模型的列表
3. THE System SHALL 为每个模型提供 id 和 name 字段
4. THE System SHALL 包含至少 DeepSeek 和 OpenAI 模型
5. THE System SHALL 返回 200 状态码和统一响应格式

### Requirement 5: SSE 流式研究接口

**用户故事**: 作为前端开发者，我希望能够通过 SSE 接收实时研究进度，以便向用户展示进度

#### 验收标准

1. THE System SHALL 提供 POST /api/research/stream 接口
2. THE System SHALL 接受 JSON 请求体，包含 prompt 字段
3. THE System SHALL 返回 text/event-stream 媒体类型
4. THE System SHALL 通过 SSE 推送进度事件
5. THE System SHALL 在研究完成或失败后关闭连接

### Requirement 6: SSE 事件格式

**用户故事**: 作为前端开发者，我希望 SSE 事件有标准化的格式，以便解析和处理

#### 验收标准

1. THE System SHALL 使用标准 SSE 格式: "event: {type}\ndata: {json}\n\n"
2. THE System SHALL 支持以下事件类型: start, plan, progress, done, error
3. WHEN 研究开始时，THE System SHALL 发送 start 事件
4. WHEN 规划完成时，THE System SHALL 发送 plan 事件，包含步骤列表
5. WHEN 执行步骤时，THE System SHALL 发送 progress 事件，包含当前步骤和总步骤数
6. WHEN 研究完成时，THE System SHALL 发送 done 事件，包含最终报告
7. WHEN 发生错误时，THE System SHALL 发送 error 事件，包含错误信息

### Requirement 7: SSE 连接管理

**用户故事**: 作为前端开发者，我希望 SSE 连接能够正确管理，以便避免资源泄漏

#### 验收标准

1. THE System SHALL 在客户端断开连接时清理资源
2. THE System SHALL 设置适当的 HTTP 头禁用缓冲
3. THE System SHALL 设置 Cache-Control: no-cache, no-transform
4. THE System SHALL 设置 Connection: keep-alive
5. THE System SHALL 设置 X-Accel-Buffering: no（禁用 Nginx 缓冲）

### Requirement 8: 错误事件处理

**用户故事**: 作为前端开发者，我希望在研究过程中发生错误时能够收到通知

#### 验收标准

1. WHEN 研究过程中发生异常时，THE System SHALL 发送 error 事件
2. THE error 事件 SHALL 包含 message 字段描述错误
3. THE System SHALL 在发送 error 事件后关闭 SSE 连接
4. THE System SHALL 记录错误到日志
5. THE System SHALL 不在 error 事件中暴露敏感信息

### Requirement 9: CORS 配置

**用户故事**: 作为前端开发者，我希望 API 支持跨域请求，以便前端可以调用

#### 验收标准

1. THE System SHALL 配置 CORS 中间件
2. THE System SHALL 允许来自 localhost:3000 的请求（开发环境）
3. THE System SHALL 允许来自配置的生产域名的请求
4. THE System SHALL 允许所有 HTTP 方法
5. THE System SHALL 允许所有 HTTP 头
6. THE System SHALL 支持凭证（credentials）

### Requirement 10: 请求验证

**用户故事**: 作为系统管理员，我希望系统能够验证请求参数，以便拒绝无效请求

#### 验收标准

1. WHEN /api/research/stream 接收到请求时，THE System SHALL 验证 prompt 字段存在
2. WHEN prompt 字段缺失时，THE System SHALL 返回 400 状态码
3. WHEN prompt 字段为空时，THE System SHALL 返回 400 状态码
4. THE System SHALL 返回清晰的验证错误信息
5. THE System SHALL 使用 Pydantic 模型验证请求

### Requirement 11: 性能要求

**用户故事**: 作为用户，我希望 API 响应快速，以便获得良好的体验

#### 验收标准

1. THE System SHALL 在 100 毫秒内响应健康检查请求
2. THE System SHALL 在 2 秒内发送 SSE 首个事件
3. THE System SHALL 在 5 分钟内完成完整研究任务
4. THE System SHALL 支持至少 5 个并发 SSE 连接
5. THE System SHALL 不因 SSE 连接导致内存泄漏

### Requirement 12: 日志记录

**用户故事**: 作为系统管理员，我希望系统记录关键操作日志，以便调试和监控

#### 验收标准

1. THE System SHALL 记录所有 API 请求（方法、路径、状态码）
2. THE System SHALL 记录 SSE 连接建立和关闭
3. THE System SHALL 记录研究任务的开始和完成
4. THE System SHALL 记录所有错误和异常
5. THE System SHALL 使用结构化日志格式（时间戳、级别、消息）

### Requirement 13: 响应时间监控

**用户故事**: 作为系统管理员，我希望能够监控 API 响应时间，以便识别性能问题

#### 验收标准

1. THE System SHALL 记录每个 API 请求的响应时间
2. THE System SHALL 在日志中输出响应时间
3. WHEN 响应时间超过 5 秒时，THE System SHALL 记录警告日志
4. THE System SHALL 提供响应时间统计（可选）
5. THE System SHALL 不因监控影响性能超过 5%

### Requirement 14: 简化设计原则

**用户故事**: 作为开发者，我希望 API 设计简单，以便快速实现和维护

#### 验收标准

1. THE System SHALL 不实现复杂的错误码体系（使用 HTTP 状态码）
2. THE System SHALL 不实现版本化路由（/api/v1/）
3. THE System SHALL 不实现认证授权（延后到后续阶段）
4. THE System SHALL 不实现速率限制（延后到后续阶段）
5. THE System SHALL 不实现 traceId 追踪（延后到后续阶段）
6. THE System SHALL 不实现心跳机制（浏览器自动处理）
7. THE System SHALL 不实现缓存策略（研究任务不重复）

### Requirement 15: 部署验证

**用户故事**: 作为运维人员，我希望能够验证 API 在生产环境正常工作

#### 验收标准

1. THE System SHALL 在 Render 部署成功
2. THE System SHALL 通过健康检查验证
3. THE System SHALL 通过 SSE 连接测试
4. THE System SHALL 配置防休眠机制（cron-job.org）
5. THE System SHALL 在生产环境响应时间满足要求

---

## 非功能需求

### NFR 1: 可维护性

- 代码应遵循 PEP 8 Python 编码规范
- 所有公共函数应包含 docstring 文档
- API 接口应有清晰的注释
- 应提供简单的 API 文档

### NFR 2: 可测试性

- 所有核心功能应有单元测试
- 应提供手动测试脚本
- 应在生产环境验证功能
- 测试覆盖核心流程即可（不要求高覆盖率）

### NFR 3: 兼容性

- 应与 Phase 1 的代码兼容
- 应支持 FastAPI 最新版本
- 应支持标准 SSE 协议
- 应与 Next.js EventSource API 兼容

### NFR 4: 性能

- 健康检查响应时间 < 100ms
- SSE 首个事件 < 2s
- 完整研究任务 < 5 分钟
- 支持 5 个并发连接

---

## 依赖关系

### 外部依赖

- FastAPI
- Pydantic
- Phase 1 的所有代理（planner_agent, research_agent, writer_agent, editor_agent）

### 内部依赖

- Phase 1 (DeepSeek 集成) 必须完成

---

## 验收标准总结

Phase 2 完成的标准：

1. ✅ 所有 15 个需求的验收标准都已满足
2. ✅ 统一响应格式工作正常
3. ✅ SSE 流式响应正常
4. ✅ 事件格式符合规范
5. ✅ 健康检查和模型列表可用
6. ✅ 全局错误处理完善
7. ✅ 生产环境部署成功
8. ✅ 手动测试通过
9. ✅ 简单文档完整

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待实施
