# 阶段 2 综合分析报告：API 接口标准化（MVP 版本）

## 📋 文档信息

- **阶段**: 阶段 2 - API 接口标准化
- **预计时间**: 3 天（MVP 快速上线）
- **创建日期**: 2025-10-30
- **最后更新**: 2025-10-30
- **状态**: ✅ 评估完成 - MVP 方案确定
- **依赖**: 阶段 1 (DeepSeek 集成) 必须完成

---

## 🎯 执行摘要

### 核心目标

**为 Next.js 前端设计最小可用的标准化 API 接口，支持实时进度推送**

### MVP 原则

**"能跑就行，快速上线，后续迭代"**

- ✅ 只做核心功能
- ✅ 3 天完成
- ✅ 避免过度设计
- ✅ 后续根据需求迭代

### 关键发现

基于对 ai-chatbot 代码库的深入分析和 MVP 原则评估：

1. **ai-chatbot 使用 AI SDK 的流式响应** ✅
   - 使用 `streamText` 和 `createUIMessageStream`
   - 通过 SSE (Server-Sent Events) 推送数据
   - 支持工具调用和实时更新

2. **当前 FastAPI 系统需要最小化改造** ⚠️
   - 添加统一响应格式（简化版）
   - 实现基础 SSE 流式接口
   - 添加健康检查和模型列表
   - **不需要**：复杂的错误码、版本化、监控等

3. **采用简化的桥接方案** 🟢
   - 统一响应封装（简化版）
   - SSE 基础实现（无心跳机制）
   - 全局错误处理
   - **延后**：鉴权、速率限制、缓存等

### 可行性评估

- **技术可行性**: ⭐⭐⭐⭐⭐ (5/5) - MVP 方案简单可行
- **时间可行性**: ⭐⭐⭐⭐⭐ (5/5) - 3 天完全够用
- **风险等级**: 🟢 低风险 - 简化后复杂度大幅降低

---

## 🔍 深度技术分析

### 1. ai-chatbot 的流式架构分析

#### 1.1 核心流程

```typescript
// app/(chat)/api/chat/route.ts
export async function POST(request: Request) {
  // 1. 创建 UI 消息流
  const stream = createUIMessageStream({
    execute: ({ writer: dataStream }) => {
      // 2. 调用 streamText
      const result = streamText({
        model: myProvider.languageModel(selectedChatModel),
        messages: convertToModelMessages(uiMessages),
        tools: {
          getWeather,
          createDocument: createDocument({ session, dataStream }),
          updateDocument: updateDocument({ session, dataStream }),
        },
        onFinish: async ({ usage }) => {
          // 3. 完成后写入使用统计
          dataStream.write({ type: "data-usage", data: usage });
        },
      });
      
      // 4. 合并流
      dataStream.merge(result.toUIMessageStream());
    },
  });
  
  // 5. 返回 SSE 流
  return new Response(stream.pipeThrough(new JsonToSseTransformStream()));
}
```

#### 1.2 数据流类型

ai-chatbot 支持多种数据类型：

```typescript
// 消息流数据类型
type DataPart = 
  | { type: "data-kind", data: ArtifactKind }      // 文档类型
  | { type: "data-id", data: string }              // 文档 ID
  | { type: "data-title", data: string }           // 文档标题
  | { type: "data-clear", data: null }             // 清空
  | { type: "data-finish", data: null }            // 完成
  | { type: "data-usage", data: AppUsage }         // 使用统计
  | { type: "text-delta", textDelta: string }      // 文本增量
  | { type: "tool-call", toolCall: ToolCall }      // 工具调用
  | { type: "tool-result", toolResult: ToolResult } // 工具结果
```



#### 1.3 工具调用机制

```typescript
// lib/ai/tools/create-document.ts
export const createDocument = ({ session, dataStream }: CreateDocumentProps) =>
  tool({
    description: "Create a document for writing activities",
    inputSchema: z.object({
      title: z.string(),
      kind: z.enum(artifactKinds),
    }),
    execute: async ({ title, kind }) => {
      const id = generateUUID();
      
      // 1. 写入文档元数据
      dataStream.write({ type: "data-kind", data: kind, transient: true });
      dataStream.write({ type: "data-id", data: id, transient: true });
      dataStream.write({ type: "data-title", data: title, transient: true });
      
      // 2. 生成文档内容
      await documentHandler.onCreateDocument({
        id, title, dataStream, session
      });
      
      // 3. 标记完成
      dataStream.write({ type: "data-finish", data: null, transient: true });
      
      return { id, title, kind, content: "Document created" };
    },
  });
```

**关键发现**:
- ✅ 工具可以直接写入数据流
- ✅ 支持实时进度更新
- ✅ 前端可以立即看到变化
- ⚠️ 这与我们的 FastAPI 架构不同

### 2. 当前 FastAPI 系统分析

#### 2.1 现有接口

```python
# main.py
@app.post("/generate_report")
async def generate_report(request: ResearchRequest):
    """生成研究报告（同步）"""
    # 1. 生成规划
    steps = planner_agent(request.prompt)
    
    # 2. 执行步骤
    history = []
    for step in steps:
        _, agent, output = executor_agent_step(step, history, request.prompt)
        history.append((step, agent, output))
    
    # 3. 返回结果
    return {"report": final_output, "steps": steps}
```

**问题**:
- ❌ 完全同步，前端需要等待
- ❌ 没有进度反馈
- ❌ 没有任务管理
- ❌ 不支持流式响应

#### 2.2 架构差异对比

| 特性 | ai-chatbot (Next.js) | 研究助手 (FastAPI) |
|------|---------------------|-------------------|
| 响应方式 | 流式 (SSE) | 同步 (JSON) |
| 进度更新 | 实时推送 | 无 |
| 工具调用 | AI SDK 自动处理 | 手动实现 |
| 数据流 | `dataStream.write()` | 无 |
| 任务管理 | 内置 (resumable-stream) | 无 |
| 前端集成 | `useChat` hook | 手动 fetch |

---

## 📊 MVP vs 完整方案对比

### 功能取舍分析

| 功能 | 完整方案 | MVP 方案 | 理由 |
|------|---------|---------|------|
| 统一响应封装 | ✅ 复杂模型（code/meta/traceId） | ✅ 简化模型（success/data/error） | 够用就行 |
| SSE 流式 | ✅ 心跳+重连+超时 | ✅ 基础实现 | 浏览器自带重连 |
| 错误码体系 | ✅ AUTH_*/INPUT_*/MODEL_* | ❌ HTTP 状态码 | 过度设计 |
| 版本化路由 | ✅ /api/v1/... | ❌ /api/... | 只有一个版本 |
| 鉴权系统 | ✅ JWT/OAuth | 🟡 简单 API Key（可选） | 看是否公开 |
| 速率限制 | ✅ 详细策略 | ❌ 不需要 | 用户少 |
| traceId | ✅ 请求追踪 | ❌ 不需要 | 过度设计 |
| 结构化日志 | ✅ ELK/Datadog | ❌ print() | MVP 够用 |
| Prometheus | ✅ 指标监控 | ❌ 平台自带 | 过度设计 |
| OpenAPI 文档 | ✅ 自动生成 | ❌ README | FastAPI /docs 够用 |
| 契约测试 | ✅ pytest+locust | ❌ 手动测试 | MVP 够用 |
| SSE 心跳 | ✅ 15-30s | ❌ 不需要 | 浏览器自动处理 |
| 缓存策略 | ✅ Redis | ❌ 不需要 | 研究任务不重复 |

### 时间节省

- **完整方案**: 5-6 天
- **MVP 方案**: **3 天**
- **节省**: 2-3 天

---

## ⚠️ 风险评估（MVP 版本）

### 🟢 低风险（已简化）

#### 1. 架构兼容性

**原风险**: FastAPI 同步架构与 Next.js 流式架构不兼容  
**MVP 方案**: 直接实现 SSE 流式接口  
**概率**: 10%（已大幅降低）  
**影响**: 最小  
**缓解措施**:

**MVP 简化方案**（推荐）:
```python
from fastapi.responses import StreamingResponse
import json

@app.post("/api/research/stream")
async def stream_research(request: ResearchRequest):
    """流式研究接口（MVP 版本）"""
    
    async def event_generator():
        try:
            # 1. 开始
            yield sse_event("start", {"prompt": request.prompt})
            
            # 2. 规划
            steps = planner_agent(request.prompt)
            yield sse_event("plan", {"steps": steps})
            
            # 3. 执行步骤
            history = []
            for i, step in enumerate(steps):
                yield sse_event("progress", {
                    "step": i + 1,
                    "total": len(steps),
                    "message": step
                })
                
                _, agent, output = executor_agent_step(step, history, request.prompt)
                history.append((step, agent, output))
            
            # 4. 完成
            final_report = history[-1][2]
            yield sse_event("done", {"report": final_report})
            
        except Exception as e:
            yield sse_event("error", {"message": str(e)})
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

def sse_event(event: str, data: dict) -> str:
    """格式化 SSE 事件（简化版）"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
```

**不需要**:
- ❌ 任务队列（Celery + Redis）- 过度设计
- ❌ 心跳机制 - 浏览器自动处理
- ❌ 复杂的重连策略 - EventSource 自带
- ❌ traceId - MVP 不需要



#### 2. 错误处理

**原风险**: 流式响应中的错误难以处理  
**MVP 方案**: 简单的 try-catch + error 事件  
**概率**: 20%  
**影响**: 最小  
**缓解措施**:

```python
async def event_generator():
    try:
        # 正常流程
        yield sse_event("start", {"prompt": prompt})
        steps = planner_agent(prompt)
        
        for step in steps:
            _, agent, output = executor_agent_step(step, history, prompt)
        
        yield sse_event("done", {"report": final_report})
        
    except Exception as e:
        # 简单错误处理
        yield sse_event("error", {"message": str(e)})
```

**不需要**:
- ❌ 步骤级错误恢复 - 过度设计
- ❌ 错误分类（可恢复/不可恢复）- MVP 不需要
- ❌ 详细的错误码 - HTTP 状态码够用

### 🟡 可选风险（延后处理）

#### 3. 性能问题

**风险描述**: 并发连接数限制  
**MVP 方案**: 暂时不处理，Vercel/Render 有基础限制  
**概率**: 10%（用户少）  
**影响**: 最小  
**后续优化**: 等有性能问题再加连接池

#### 4. 鉴权缺失

**风险描述**: 无认证可能被滥用  
**MVP 方案**: 看需求决定  
**概率**: 30%  
**影响**: 中等  
**简单方案**:

```python
# 最简单的 API Key（可选）
API_KEY = os.getenv("API_KEY", "demo-key-123")

@app.post("/api/research/stream")
async def stream_research(request: Request, research_request: ResearchRequest):
    # 可选的简单验证
    if request.headers.get("X-API-Key") != API_KEY:
        raise HTTPException(401, "Invalid API key")
    # ...
```

**不需要**:
- ❌ JWT Token - 过度设计
- ❌ OAuth - 过度设计
- ❌ 复杂的权限系统 - MVP 不需要

---

## 🔧 MVP 核心设计

### 1. 统一响应格式（简化版）

**MVP 方案**: 最简单的成功/失败模型

```python
# models.py
from pydantic import BaseModel
from typing import Optional, Any

class ApiResponse(BaseModel):
    """统一响应模型（MVP 版本）"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

# 使用示例
@app.get("/api/health")
async def health():
    return ApiResponse(success=True, data={"status": "ok"})

@app.get("/api/models")
async def models():
    return ApiResponse(
        success=True,
        data={
            "models": [
                {"id": "deepseek-chat", "name": "DeepSeek Chat"},
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini"}
            ]
        }
    )
```

**不需要**:
- ❌ `code` 业务码 - HTTP 状态码够用
- ❌ `meta` 元数据 - MVP 不需要
- ❌ `traceId` 追踪ID - 过度设计

### 2. SSE 事件格式（简化版）

**MVP 方案**: 只需要 4 种事件

```typescript
// 前端事件类型定义
type StreamEvent = 
  | { type: "start", data: { prompt: string } }
  | { type: "plan", data: { steps: string[] } }
  | { type: "progress", data: { step: number, total: number, message: string } }
  | { type: "done", data: { report: string } }
  | { type: "error", data: { message: string } }
```

**不需要**:
- ❌ `heartbeat` 心跳 - 浏览器自动处理
- ❌ `tool-call` / `tool-result` - 过度设计
- ❌ `text-delta` 增量文本 - MVP 不需要
- ❌ `usage` 使用统计 - 后续再加



### 3. 全局错误处理

**MVP 方案**: 简单的全局异常处理器

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局错误处理（MVP 版本）"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 错误处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )
```

**不需要**:
- ❌ 详细的错误分类 - 过度设计
- ❌ 错误码映射表 - HTTP 状态码够用
- ❌ 结构化日志 - `print()` 够用

### 4. 延后的功能（不在 MVP 范围）

以下功能在 MVP 阶段**不实现**，等后续迭代：

#### ❌ 认证授权
```python
# 如果需要公开，可以加最简单的 API Key
# 否则暂时不加
```

#### ❌ 速率限制
```python
# MVP 阶段用户少，不需要
# Vercel/Render 有基础限制
```

#### ❌ 监控和日志
```python
# 使用平台自带的监控
# 不需要 Prometheus/ELK
```

#### ❌ 缓存策略
```python
# 研究任务每次都不同
# 缓存意义不大
```

#### ❌ traceId / requestId
```python
# MVP 阶段日志量小
# 直接看时间戳就行
```

---

## 📋 MVP 实施计划（3天）

### Day 1: 统一响应 + 基础接口（6-8小时）

#### 任务 1.1: 统一响应模型（30分钟）
```python
# models.py
from pydantic import BaseModel
from typing import Optional, Any

class ApiResponse(BaseModel):
    """统一响应模型（MVP 版本）"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
```

#### 任务 1.2: 全局错误处理（30分钟）
```python
# main.py
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)}
    )
```

#### 任务 1.3: 健康检查接口（5分钟）
```python
@app.get("/api/health")
async def health():
    return ApiResponse(success=True, data={"status": "ok"})
```

#### 任务 1.4: 模型列表接口（10分钟）
```python
@app.get("/api/models")
async def models():
    return ApiResponse(
        success=True,
        data={
            "models": [
                {"id": "deepseek-chat", "name": "DeepSeek Chat"},
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini"}
            ]
        }
    )
```

### Day 2: SSE 流式接口（6-8小时）

#### 任务 2.1: 核心流式接口（4-6小时）
```python
# main.py
from fastapi.responses import StreamingResponse
import json

@app.post("/api/research/stream")
async def stream_research(request: ResearchRequest):
    """流式研究接口（MVP 版本）"""
    
    async def event_generator():
        try:
            # 1. 开始
            yield sse_event("start", {"prompt": request.prompt})
            
            # 2. 规划
            steps = planner_agent(request.prompt)
            yield sse_event("plan", {"steps": steps})
            
            # 3. 执行步骤
            history = []
            for i, step in enumerate(steps):
                yield sse_event("progress", {
                    "step": i + 1,
                    "total": len(steps),
                    "message": step
                })
                
                _, agent, output = executor_agent_step(step, history, request.prompt)
                history.append((step, agent, output))
            
            # 4. 完成
            final_report = history[-1][2]
            yield sse_event("done", {"report": final_report})
            
        except Exception as e:
            yield sse_event("error", {"message": str(e)})
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

def sse_event(event: str, data: dict) -> str:
    """格式化 SSE 事件"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
```

#### 任务 2.2: 本地测试（1-2小时）
```bash
# 启动服务
uvicorn main:app --reload

# 测试健康检查
curl http://localhost:8000/api/health

# 测试 SSE（使用 curl 或浏览器）
curl -N http://localhost:8000/api/research/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "研究量子计算"}'
```

### Day 3: 测试 + 文档 + 部署验证（6-8小时）

#### 任务 3.1: 手动测试（2小时）
- ✅ 测试所有接口
- ✅ 测试 SSE 连接
- ✅ 测试错误处理
- ✅ 测试不同的研究主题

#### 任务 3.2: 简单文档（1小时）
```markdown
# API 文档

## 健康检查
GET /api/health

## 模型列表
GET /api/models

## 流式研究
POST /api/research/stream
Content-Type: application/json

{
  "prompt": "研究主题"
}

## SSE 事件
- start: 开始
- plan: 规划完成
- progress: 进度更新
- done: 完成
- error: 错误
```

#### 任务 3.3: 部署验证（1-2小时）
```bash
# 部署到 Render
git push origin main

# 测试生产环境
curl https://your-app.onrender.com/api/health

# 测试 SSE
curl -N https://your-app.onrender.com/api/research/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "测试"}'
```

#### 任务 3.4: 防休眠配置（10分钟）
- 使用 cron-job.org
- 每 10 分钟 ping `/api/health`

---

## ✅ MVP 验收标准（简化版）

### 核心功能验收

- [ ] **统一响应**
  - [ ] 所有接口返回 `ApiResponse` 格式
  - [ ] 成功: `success=true, data=...`
  - [ ] 失败: `success=false, error=...`

- [ ] **SSE 流式接口**
  - [ ] `/api/research/stream` 可以正常工作
  - [ ] 事件顺序正确: start → plan → progress → done
  - [ ] 错误时返回 error 事件
  - [ ] 浏览器可以正常接收

- [ ] **基础接口**
  - [ ] `/api/health` 返回 ok
  - [ ] `/api/models` 返回模型列表

- [ ] **错误处理**
  - [ ] 全局异常被捕获
  - [ ] 返回友好的错误消息
  - [ ] 不暴露敏感信息

### 功能测试

- [ ] **手动测试**
  - [ ] 用 curl 测试所有接口
  - [ ] 用浏览器测试 SSE
  - [ ] 测试至少 3 个不同的研究主题
  - [ ] 测试错误情况（无效输入等）

- [ ] **部署验证**
  - [ ] 部署到 Render 成功
  - [ ] 生产环境接口可访问
  - [ ] SSE 在生产环境正常工作
  - [ ] 防休眠配置生效

### 性能验收（基础）

- [ ] **响应时间**
  - [ ] 健康检查 < 100ms
  - [ ] SSE 首个事件 < 2秒
  - [ ] 完整研究 < 5分钟

- [ ] **稳定性**
  - [ ] 连续 5 次请求无错误
  - [ ] SSE 连接不中断
  - [ ] 无明显内存泄漏

### 不需要验收的项目

- ❌ 并发压测 - MVP 不需要
- ❌ 契约测试 - MVP 不需要
- ❌ 性能指标 - MVP 不需要
- ❌ 监控告警 - MVP 不需要
- ❌ 安全审计 - MVP 不需要

---

## 💰 成本和时间分析（MVP 版本）

### 时间对比

| 项目 | 完整方案 | MVP 方案 | 节省 |
|------|---------|---------|------|
| 架构设计 | 1天 | 0天（直接开发） | -1天 |
| 统一响应 + 基础接口 | 1天 | 1天 | 0 |
| SSE 流式接口 | 2-3天 | 1天 | -1-2天 |
| 认证/限流/监控 | 1-2天 | 0天（延后） | -1-2天 |
| 测试文档 | 1天 | 1天 | 0 |
| **总计** | **6-8天** | **3天** | **-3-5天** |

### 成本分析

**开发成本**:
- 时间: 3 天（MVP）
- 人力: 1 人全职
- 总成本: $1,500 - $2,000

**节省**:
- 相比完整方案节省 $2,000 - $3,000
- 相比原计划准时完成

**技术债务**:
- ✅ 最小化 - 只做核心功能
- ✅ 后续可迭代 - 架构支持扩展
- ✅ 维护成本低 - 代码简单

---

## 🎯 最终建议（MVP 版本）

### 核心方案

**采用**: 简化的 SSE 流式接口

**理由**:
1. ✅ 与 ai-chatbot 架构一致
2. ✅ 用户体验好
3. ✅ 实现简单（去掉复杂功能）
4. ✅ 3 天可完成
5. ✅ 后续可迭代

### 关键决策

#### 1. 使用流式 SSE ✅
- **决定**: 是
- **理由**: 与前端架构一致，用户体验好
- **简化**: 不需要心跳、重连等复杂机制

#### 2. 统一响应格式 ✅
- **决定**: 是（简化版）
- **理由**: 前端需要统一处理
- **简化**: 只需要 success/data/error 三个字段

#### 3. 认证授权 🟡
- **决定**: 可选
- **理由**: 看是否公开使用
- **简化**: 如需要，用最简单的 API Key

#### 4. 速率限制 ❌
- **决定**: 延后
- **理由**: MVP 阶段用户少
- **简化**: 使用平台自带限制

#### 5. 监控日志 ❌
- **决定**: 延后
- **理由**: 使用平台自带监控
- **简化**: `print()` 够用

#### 6. 缓存策略 ❌
- **决定**: 延后
- **理由**: 研究任务不重复
- **简化**: 不需要

### 实施优先级

**P0 (必须 - Day 1-2)**:
- ✅ 统一响应封装
- ✅ SSE 流式接口
- ✅ 健康检查
- ✅ 模型列表
- ✅ 全局错误处理

**P1 (重要 - 后续迭代)**:
- 🟡 简单认证（如需要）
- 🟡 速率限制（如有滥用）
- 🟡 详细日志（如需调试）

**P2 (可选 - 按需添加)**:
- ⚪ 缓存策略
- ⚪ 监控指标
- ⚪ 任务持久化
- ⚪ 版本化路由

---

## 📝 下一步行动（MVP 版本）

### 立即开始（Day 1）

**上午**:
1. ✅ 创建统一响应模型（30分钟）
2. ✅ 添加全局错误处理（30分钟）
3. ✅ 实现健康检查接口（5分钟）
4. ✅ 实现模型列表接口（10分钟）

**下午**:
1. ✅ 开始 SSE 流式接口开发
2. ✅ 实现基础事件生成器
3. ✅ 本地测试

### 第二天（Day 2）

**全天**:
1. ✅ 完成 SSE 流式接口
2. ✅ 集成 planner_agent 和 executor_agent_step
3. ✅ 测试完整流程
4. ✅ 修复 bug

### 第三天（Day 3）

**上午**:
1. ✅ 手动测试所有接口
2. ✅ 测试不同的研究主题
3. ✅ 测试错误情况

**下午**:
1. ✅ 编写简单文档
2. ✅ 部署到 Render
3. ✅ 生产环境验证
4. ✅ 配置防休眠

---

## 🎉 总结

### 核心发现（MVP 版本）

1. **简化后风险大幅降低** 🟢
   - 去掉复杂功能
   - 只做核心接口
   - 3 天可完成

2. **时间估算准确** ✅
   - MVP 方案: 3 天
   - 符合原计划
   - 无需延期

3. **功能取舍合理** ✅
   - 保留核心功能
   - 延后非必需功能
   - 后续可迭代

### MVP 原则

**"能跑就行，快速上线，后续迭代"**

### 采纳的功能

✅ **必须实现**:
- 统一响应封装（简化版）
- SSE 流式接口（基础版）
- 健康检查
- 模型列表
- 全局错误处理

🟡 **可选实现**:
- 简单 API Key 认证（如需要）

❌ **延后实现**:
- 详细错误码
- 版本化路由
- 速率限制
- 监控日志
- 缓存策略
- traceId
- 契约测试

### 最终建议

**立即开始开发**，按照 3 天计划执行：
- Day 1: 统一响应 + 基础接口
- Day 2: SSE 流式接口
- Day 3: 测试 + 文档 + 部署

**不要过度设计**，只做核心功能。

**快速上线**，后续根据实际需求迭代。

---

**创建日期**: 2025-10-30  
**最后更新**: 2025-10-30  
**版本**: 2.0 (MVP)  
**状态**: ✅ 评估完成 - MVP 方案确定  
**建议**: 立即开始开发，3 天完成
