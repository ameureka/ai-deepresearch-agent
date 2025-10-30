# Phase 2: API 接口标准化 - 任务清单

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 2 - API 接口标准化
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **预计时间**: 3 天（24 小时）
- **状态**: 待执行
- **依赖**: Phase 1 (DeepSeek 集成) 必须完成

---

## 任务概览

本阶段包含 **30 个任务**，分为 **5 个主要模块**：

1. **统一响应与错误处理** (6 个任务，3 小时)
2. **基础接口实现** (4 个任务，2 小时)
3. **SSE 流式接口** (8 个任务，10 小时)
4. **测试与验证** (8 个任务，6 小时)
5. **部署与文档** (4 个任务，3 小时)

**标记说明**:
- `[ ]` 未完成
- `[x]` 已完成
- `*` 可选任务（文档编写）

---

## 实施任务

### 模块 1: 统一响应与错误处理（3 小时）

#### - [ ] 1.1 创建统一响应模型
- 创建文件 `models.py`（如果不存在）
- 定义 `ApiResponse` Pydantic 模型
- 包含字段: success (bool), data (Optional[Any]), error (Optional[str])
- 添加类型提示和 docstring
- _需求: Requirement 1_
- _预计时间: 30 分钟_

#### - [ ] 1.2 实现全局异常处理器
- 在 `main.py` 中添加 `@app.exception_handler(Exception)`
- 捕获所有未处理的异常
- 返回 500 状态码和 ApiResponse 格式
- 记录错误到日志
- 不暴露敏感信息（堆栈跟踪）
- _需求: Requirement 2_
- _预计时间: 30 分钟_

#### - [ ] 1.3 实现 HTTP 异常处理器
- 在 `main.py` 中添加 `@app.exception_handler(HTTPException)`
- 返回对应的 HTTP 状态码
- 返回 ApiResponse 格式
- 记录错误到日志
- _需求: Requirement 2_
- _预计时间: 20 分钟_

#### - [ ] 1.4 配置 CORS 中间件
- 在 `main.py` 中添加 CORSMiddleware
- 配置 allow_origins（localhost:3000, Vercel 域名）
- 配置 allow_credentials=True
- 配置 allow_methods=["*"]
- 配置 allow_headers=["*"]
- 从环境变量读取 ALLOWED_ORIGINS
- _需求: Requirement 9_
- _预计时间: 30 分钟_

#### - [ ] 1.5 配置日志系统
- 配置 logging.basicConfig
- 设置日志级别为 INFO
- 设置日志格式（时间戳、级别、消息）
- 创建 logger 实例
- _需求: Requirement 12_
- _预计时间: 20 分钟_

#### - [ ] 1.6 测试错误处理
- 创建测试脚本 `tests/test_error_handling.py`
- 测试全局异常处理
- 测试 HTTP 异常处理
- 测试 CORS 配置
- 验证日志记录
- _需求: Requirement 2, 9, 12_
- _预计时间: 30 分钟_

---

### 模块 2: 基础接口实现（2 小时）

#### - [ ] 2.1 实现健康检查接口
- 在 `main.py` 中添加 `@app.get("/api/health")`
- 返回 ApiResponse(success=True, data={"status": "ok"})
- 确保响应时间 < 100ms
- 不需要认证
- _需求: Requirement 3_
- _预计时间: 15 分钟_

#### - [ ] 2.2 实现模型列表接口
- 在 `main.py` 中添加 `@app.get("/api/models")`
- 返回可用模型列表
- 包含 DeepSeek 和 OpenAI 模型
- 每个模型包含 id 和 name 字段
- 返回 ApiResponse 格式
- _需求: Requirement 4_
- _预计时间: 20 分钟_

#### - [ ] 2.3 测试基础接口
- 使用 curl 测试健康检查接口
- 使用 curl 测试模型列表接口
- 验证响应格式
- 验证响应时间
- _需求: Requirement 3, 4_
- _预计时间: 15 分钟_

#### - [ ] 2.4 添加请求日志
- 在所有接口中添加请求日志
- 记录: 方法、路径、状态码、响应时间
- 使用 logger.info()
- _需求: Requirement 12, 13_
- _预计时间: 30 分钟_

---

### 模块 3: SSE 流式接口（10 小时）

#### - [ ] 3.1 创建研究请求模型
- 在 `models.py` 中定义 `ResearchRequest` 模型
- 包含 prompt 字段（必需，字符串类型）
- 添加验证规则（非空）
- 添加 docstring
- _需求: Requirement 10_
- _预计时间: 15 分钟_

#### - [ ] 3.2 实现 SSE 事件格式化函数
- 创建 `sse_event(event: str, data: dict) -> str` 函数
- 返回标准 SSE 格式: "event: {type}\ndata: {json}\n\n"
- 使用 json.dumps() 序列化 data
- 添加类型提示和 docstring
- _需求: Requirement 6_
- _预计时间: 20 分钟_

#### - [ ] 3.3 实现事件生成器框架
- 创建 `event_generator()` async generator 函数
- 添加 try-except 错误处理
- 在 except 中发送 error 事件
- 添加日志记录
- _需求: Requirement 5, 8_
- _预计时间: 30 分钟_

#### - [ ] 3.4 实现 start 事件
- 在 event_generator 开始时发送 start 事件
- 包含 prompt 字段
- 记录日志: "Research started"
- _需求: Requirement 6_
- _预计时间: 15 分钟_

#### - [ ] 3.5 集成 planner_agent 并发送 plan 事件
- 调用 planner_agent(request.prompt)
- 获取步骤列表
- 发送 plan 事件，包含 steps 字段
- 记录日志: "Planning completed"
- _需求: Requirement 6_
- _预计时间: 30 分钟_

#### - [ ] 3.6 实现步骤执行循环
- 遍历 steps 列表
- 对每个步骤调用 executor_agent_step()
- 维护 history 列表
- 记录每个步骤的执行
- _需求: Requirement 5_
- _预计时间: 45 分钟_

#### - [ ] 3.7 实现 progress 事件
- 在每个步骤执行前发送 progress 事件
- 包含字段: step (当前步骤), total (总步骤数), message (步骤描述)
- 记录日志: "Step {i}/{total}"
- _需求: Requirement 6_
- _预计时间: 30 分钟_

#### - [ ] 3.8 实现 done 事件
- 在所有步骤完成后发送 done 事件
- 包含 report 字段（最终报告）
- 从 history 中提取最终输出
- 记录日志: "Research completed"
- _需求: Requirement 6_
- _预计时间: 20 分钟_

#### - [ ] 3.9 实现 SSE 路由处理器
- 创建 `@app.post("/api/research/stream")` 路由
- 接受 ResearchRequest 参数
- 调用 event_generator()
- 返回 StreamingResponse
- 设置 media_type="text/event-stream"
- _需求: Requirement 5_
- _预计时间: 30 分钟_

#### - [ ] 3.10 配置 SSE 响应头
- 设置 Cache-Control: no-cache, no-transform
- 设置 Connection: keep-alive
- 设置 X-Accel-Buffering: no
- 验证头部正确设置
- _需求: Requirement 7_
- _预计时间: 20 分钟_

#### - [ ] 3.11 测试 SSE 连接
- 使用 curl -N 测试 SSE 接口
- 验证接收到所有事件类型（start, plan, progress, done）
- 验证事件格式正确
- 验证事件顺序正确
- _需求: Requirement 5, 6_
- _预计时间: 1 小时_

#### - [ ] 3.12 测试 SSE 错误处理
- 模拟研究过程中的异常
- 验证发送 error 事件
- 验证连接正确关闭
- 验证错误日志记录
- _需求: Requirement 8_
- _预计时间: 45 分钟_

---

### 模块 4: 测试与验证（6 小时）

#### - [ ] 4.1 创建手动测试脚本
- 创建 `scripts/test_api.sh`
- 包含所有接口的 curl 测试命令
- 添加预期响应注释
- 添加执行说明
- _需求: All Requirements_
- _预计时间: 30 分钟_

#### - [ ] 4.2 执行完整流程测试
- 启动 FastAPI 服务
- 测试健康检查
- 测试模型列表
- 测试完整研究流程（start → plan → progress → done）
- 记录测试结果
- _需求: Requirement 3, 4, 5, 6_
- _预计时间: 1 小时_

#### - [ ] 4.3 测试请求验证
- 测试缺少 prompt 字段的请求
- 测试空 prompt 的请求
- 验证返回 400 状态码
- 验证错误信息清晰
- _需求: Requirement 10_
- _预计时间: 30 分钟_

#### - [ ] 4.4 测试并发连接
- 同时发起 5 个 SSE 连接
- 验证所有连接正常工作
- 验证无资源泄漏
- 验证性能满足要求
- _需求: Requirement 11_
- _预计时间: 1 小时_

#### - [ ] 4.5 测试性能指标
- 测试健康检查响应时间 < 100ms
- 测试 SSE 首个事件 < 2s
- 测试完整研究任务 < 5 分钟
- 记录性能数据
- _需求: Requirement 11, 13_
- _预计时间: 1 小时_

#### - [ ] 4.6 测试 CORS 配置
- 从不同域名发起请求
- 验证 CORS 头部正确
- 验证允许的域名可以访问
- 验证不允许的域名被拒绝
- _需求: Requirement 9_
- _预计时间: 30 分钟_

#### - [ ] 4.7 测试错误场景
- 测试 API 调用失败
- 测试网络超时
- 测试无效输入
- 验证错误处理正确
- 验证错误日志记录
- _需求: Requirement 2, 8, 11_
- _预计时间: 1 小时_

#### - [ ] 4.8 生成测试报告
- 汇总所有测试结果
- 创建 `reports/phase2_test_report.md`
- 包含: 功能测试、性能测试、错误测试
- 标记通过/失败的测试
- _需求: All Requirements_
- _预计时间: 30 分钟_

---

### 模块 5: 部署与文档（3 小时）

#### - [ ] 5.1 更新 Dockerfile
- 确保 Dockerfile 包含所有依赖
- 测试 Docker 构建
- 测试 Docker 运行
- 验证端口暴露正确
- _需求: Requirement 15_
- _预计时间: 30 分钟_

#### - [ ] 5.2 部署到 Render
- 连接 GitHub 仓库
- 配置环境变量
- 触发部署
- 监控部署日志
- 验证部署成功
- _需求: Requirement 15_
- _预计时间: 1 小时_

#### - [ ] 5.3 配置防休眠
- 注册 cron-job.org
- 配置定时任务（每 10 分钟）
- URL: /api/health
- 测试防休眠工作
- _需求: Requirement 15_
- _预计时间: 20 分钟_

#### - [ ] 5.4 生产环境验证
- 测试生产环境健康检查
- 测试生产环境 SSE 连接
- 测试完整研究流程
- 验证性能满足要求
- 验证防休眠工作
- _需求: Requirement 15_
- _预计时间: 1 小时_

#### - [ ]* 5.5 创建 API 文档
- 创建 `docs/api.md`
- 文档化所有接口
- 包含请求/响应示例
- 包含 SSE 事件格式
- 包含错误码说明
- _需求: NFR 1_
- _预计时间: 1 小时_

#### - [ ]* 5.6 更新 README
- 添加 Phase 2 完成说明
- 添加 API 接口使用指南
- 添加部署说明
- 添加故障排查指南
- _需求: NFR 1_
- _预计时间: 45 分钟_

---

## 验收标准

### 功能验收

- [ ] 所有 15 个需求的验收标准都已满足
- [ ] 统一响应格式工作正常
- [ ] SSE 流式响应正常
- [ ] 事件格式符合规范（start, plan, progress, done, error）
- [ ] 健康检查和模型列表可用
- [ ] 全局错误处理完善
- [ ] CORS 配置正确

### 性能验收

- [ ] 健康检查响应时间 < 100ms
- [ ] SSE 首个事件 < 2s
- [ ] 完整研究任务 < 5 分钟
- [ ] 支持 5 个并发连接
- [ ] 无内存泄漏

### 部署验收

- [ ] Render 部署成功
- [ ] 生产环境健康检查通过
- [ ] 生产环境 SSE 连接正常
- [ ] 防休眠配置生效
- [ ] 监控和日志正常

### 文档验收

- [ ] API 文档完整（可选）
- [ ] README 更新（可选）
- [ ] 测试报告生成

---

## 时间估算

| 模块 | 任务数 | 预计时间 |
|------|--------|----------|
| 统一响应与错误处理 | 6 | 3 小时 |
| 基础接口实现 | 4 | 2 小时 |
| SSE 流式接口 | 12 | 10 小时 |
| 测试与验证 | 8 | 6 小时 |
| 部署与文档 | 6 | 3 小时 |
| **总计** | **36** | **24 小时** |

**实际工作日**: 3 天（每天 8 小时）

---

## 依赖关系

```
Phase 1 完成
    ↓
统一响应与错误处理 (1.1-1.6)
    ↓
基础接口实现 (2.1-2.4)
    ↓
SSE 流式接口 (3.1-3.12)
    ↓
测试与验证 (4.1-4.8)
    ↓
部署与文档 (5.1-5.6)
```

---

## 风险和缓解

### 高风险

1. **SSE 在生产环境不工作**
   - 缓解: 配置正确的响应头（X-Accel-Buffering: no）
   - 缓解: 在部署前测试 SSE 连接

2. **CORS 配置错误**
   - 缓解: 详细的 CORS 配置清单
   - 缓解: 测试不同域名的访问

### 中风险

3. **性能不满足要求**
   - 缓解: 使用异步处理
   - 缓解: 优化代理执行逻辑

4. **Render 休眠问题**
   - 缓解: 配置防休眠（cron-job.org）
   - 缓解: 考虑升级到付费层

---

## 下一步行动

### 立即开始（Day 1 上午）

1. ✅ 创建统一响应模型 (任务 1.1)
2. ✅ 实现全局错误处理 (任务 1.2-1.3)
3. ✅ 配置 CORS (任务 1.4)
4. ✅ 配置日志 (任务 1.5)

### Day 1 下午

5. ✅ 实现基础接口 (任务 2.1-2.4)
6. ✅ 开始 SSE 接口 (任务 3.1-3.4)

### Day 2

7. ✅ 完成 SSE 接口 (任务 3.5-3.12)
8. ✅ 开始测试 (任务 4.1-4.4)

### Day 3

9. ✅ 完成测试 (任务 4.5-4.8)
10. ✅ 部署和文档 (任务 5.1-5.6)

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待执行
