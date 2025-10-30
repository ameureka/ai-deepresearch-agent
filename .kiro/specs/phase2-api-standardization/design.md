# Phase 2: API 接口标准化 - 设计文档

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 2 - API 接口标准化
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **状态**: 待实施
- **依赖**: Phase 1 (DeepSeek 集成) 必须完成

---

## 概述

### 设计目标

Phase 2 的设计目标是为 Next.js 前端设计最小可用的标准化 API 接口：

1. **统一响应**: 所有接口返回统一格式
2. **实时进度**: 通过 SSE 推送研究进度
3. **简化设计**: 只做核心功能，避免过度设计
4. **快速上线**: 3 天完成开发和部署
5. **易于维护**: 代码简单清晰

### MVP 原则

**"只做核心功能，避免过度设计"**

**包含**:
- ✅ 统一响应格式（简化版）
- ✅ SSE 流式接口（基础版）
- ✅ 健康检查和模型列表
- ✅ 全局错误处理
- ✅ CORS 配置

**不包含**（延后）:
- ❌ 复杂的错误码体系
- ❌ 版本化路由
- ❌ 认证授权
- ❌ 速率限制
- ❌ traceId 追踪
- ❌ 心跳机制
- ❌ 缓存策略

---

## 架构设计

### API 架构

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Global Error Handler                    │   │
│  │  - Exception Handler                              │   │
│  │  - HTTPException Handler                          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │              CORS Middleware                      │   │
│  │  - Allow Origins                                  │   │
│  │  - Allow Methods                                  │   │
│  │  - Allow Headers                                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Health    │  │   Models    │  │  Research   │     │
│  │   Check     │  │    List     │  │   Stream    │     │
│  │             │  │             │  │             │     │
│  │ GET /api/   │  │ GET /api/   │  │ POST /api/  │     │
│  │ health      │  │ models      │  │ research/   │     │
│  │             │  │             │  │ stream      │     │
│  └─────────────┘  └─────────────┘  └──────┬──────┘     │
│                                            │             │
│                                            │             │
│                                   ┌────────▼────────┐   │
│                                   │  Event Generator│   │
│                                   │  - start        │   │
│                                   │  - plan         │   │
│                                   │  - progress     │   │
│                                   │  - done         │   │
│                                   │  - error        │   │
│                                   └────────┬────────┘   │
│                                            │             │
│                                   ┌────────▼────────┐   │
│                                   │  Phase 1 Agents │   │
│                                   │  - planner      │   │
│                                   │  - researcher   │   │
│                                   │  - writer       │   │
│                                   │  - editor       │   │
│                                   └─────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 请求流程

```
Client Request
    ↓
CORS Middleware
    ↓
Route Handler
    ↓
Request Validation (Pydantic)
    ↓
Business Logic
    ↓
Response / SSE Stream
    ↓
Global Error Handler (if error)
    ↓
Client Response
```

---

## 组件设计

### 1. 统一响应模型

**定义**:

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

**使用示例**:

```python
# 成功响应
return ApiResponse(success=True, data={"status": "ok"})

# 失败响应
return ApiResponse(success=False, error="Invalid request")
```

### 2. 全局错误处理

**实现**:

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局错误处理（MVP 版本）"""
    logger.error(f"Unhandled exception: {exc}")
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

### 3. 健康检查接口

**实现**:

```python
@app.get("/api/health")
async def health():
    """健康检查接口"""
    return ApiResponse(success=True, data={"status": "ok"})
```

**特点**:
- 极简实现
- 快速响应（< 100ms）
- 不需要认证
- 用于监控和防休眠

### 4. 模型列表接口

**实现**:

```python
@app.get("/api/models")
async def models():
    """模型列表接口"""
    return ApiResponse(
        success=True,
        data={
            "models": [
                {"id": "deepseek-chat", "name": "DeepSeek Chat"},
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
                {"id": "o1-mini", "name": "OpenAI o1-mini"},
            ]
        }
    )
```

### 5. SSE 流式研究接口

**请求模型**:

```python
class ResearchRequest(BaseModel):
    """研究请求模型"""
    prompt: str
```

**核心实现**:

```python
from fastapi.responses import StreamingResponse
import json

@app.post("/api/research/stream")
async def stream_research(request: ResearchRequest):
    """流式研究接口（MVP 版本）"""
    
    async def event_generator():
        try:
            # 1. 开始事件
            yield sse_event("start", {"prompt": request.prompt})
            
            # 2. 规划阶段
            steps = planner_agent(request.prompt)
            yield sse_event("plan", {"steps": steps})
            
            # 3. 执行步骤
            history = []
            for i, step in enumerate(steps):
                # 发送进度事件
                yield sse_event("progress", {
                    "step": i + 1,
                    "total": len(steps),
                    "message": step
                })
                
                # 执行步骤
                _, agent, output = executor_agent_step(
                    step, history, request.prompt
                )
                history.append((step, agent, output))
            
            # 4. 完成事件
            final_report = history[-1][2] if history else ""
            yield sse_event("done", {"report": final_report})
            
        except Exception as e:
            # 5. 错误事件
            logger.error(f"Research error: {e}")
            yield sse_event("error", {"message": str(e)})
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

def sse_event(event: str, data: dict) -> str:
    """格式化 SSE 事件"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
```

**关键点**:
- 使用 async generator 生成事件
- 标准 SSE 格式
- 禁用缓冲（X-Accel-Buffering: no）
- 异常自动转换为 error 事件

### 6. CORS 配置

**实现**:

```python
from fastapi.middleware.cors import CORSMiddleware
import os

# CORS 配置
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",              # 开发环境
        "https://your-app.vercel.app",        # 生产环境
        "https://your-app-*.vercel.app",      # 预览环境
    ] + allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 数据模型

### SSE 事件格式

```typescript
// TypeScript 类型定义（供前端参考）

type SSEEvent = 
  | StartEvent
  | PlanEvent
  | ProgressEvent
  | DoneEvent
  | ErrorEvent;

interface StartEvent {
  type: "start";
  data: {
    prompt: string;
  };
}

interface PlanEvent {
  type: "plan";
  data: {
    steps: string[];
  };
}

interface ProgressEvent {
  type: "progress";
  data: {
    step: number;
    total: number;
    message: string;
  };
}

interface DoneEvent {
  type: "done";
  data: {
    report: string;
  };
}

interface ErrorEvent {
  type: "error";
  data: {
    message: string;
  };
}
```

### API 响应格式

```typescript
// 成功响应
interface SuccessResponse<T> {
  success: true;
  data: T;
  error: null;
}

// 失败响应
interface ErrorResponse {
  success: false;
  data: null;
  error: string;
}

type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;
```

---

## 错误处理

### 错误分类

1. **请求验证错误** (400)
   - 缺少必需字段
   - 字段类型错误
   - 字段值无效

2. **服务器错误** (500)
   - 未捕获的异常
   - 代理执行失败
   - 数据库错误

3. **SSE 流错误**
   - 研究过程中的异常
   - 通过 error 事件通知

### 错误处理策略

```python
# 1. 请求验证错误 - Pydantic 自动处理
# FastAPI 自动返回 422 状态码

# 2. 业务逻辑错误 - 手动抛出 HTTPException
from fastapi import HTTPException

if not prompt:
    raise HTTPException(status_code=400, detail="Prompt is required")

# 3. 未捕获异常 - 全局错误处理器
# 自动返回 500 状态码和错误信息

# 4. SSE 流错误 - 发送 error 事件
try:
    # 执行研究
    pass
except Exception as e:
    yield sse_event("error", {"message": str(e)})
```

---

## 测试策略

### 手动测试

**测试工具**: curl

**测试用例**:

```bash
# 1. 测试健康检查
curl http://localhost:8000/api/health

# 预期: {"success": true, "data": {"status": "ok"}}

# 2. 测试模型列表
curl http://localhost:8000/api/models

# 预期: {"success": true, "data": {"models": [...]}}

# 3. 测试 SSE 流
curl -N http://localhost:8000/api/research/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "研究量子计算"}'

# 预期: 接收到 start, plan, progress, done 事件

# 4. 测试错误处理
curl http://localhost:8000/api/research/stream \
  -H "Content-Type: application/json" \
  -d '{}'

# 预期: 422 状态码，验证错误
```

### 集成测试

**测试场景**:
1. 完整研究流程
2. 错误场景（无效输入、API 失败）
3. 并发连接（5 个）
4. 长时间运行（5 分钟）

### 生产环境验证

**验证步骤**:
1. 部署到 Render
2. 测试健康检查
3. 测试 SSE 连接
4. 配置防休眠
5. 监控运行状态

---

## 部署考虑

### 环境变量

**必需**:
- ALLOWED_ORIGINS（CORS 配置）

**可选**:
- LOG_LEVEL（日志级别，默认 INFO）

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Render 配置

**构建命令**: (留空，使用 Dockerfile)  
**启动命令**: (留空，使用 Dockerfile CMD)  
**环境变量**:
```
DEEPSEEK_API_KEY=xxx
OPENAI_API_KEY=xxx
TAVILY_API_KEY=xxx
ALLOWED_ORIGINS=https://your-app.vercel.app
```

### 防休眠配置

**使用 cron-job.org**:
- URL: `https://your-app.onrender.com/api/health`
- 间隔: 每 10 分钟
- 方法: GET

---

## 性能优化

### 1. 响应时间优化

- 健康检查: 直接返回，无业务逻辑
- 模型列表: 静态数据，无数据库查询
- SSE 流: 异步生成器，不阻塞

### 2. 并发处理

- FastAPI 原生支持异步
- 使用 async/await
- 不需要额外配置

### 3. 内存管理

- SSE 使用 generator，按需生成
- 不缓存完整响应
- 连接关闭时自动清理

---

## 安全考虑

### 1. 输入验证

- 使用 Pydantic 模型验证
- 自动类型检查
- 自动必填字段检查

### 2. 错误信息

- 不暴露堆栈跟踪
- 不暴露内部路径
- 提供友好的错误消息

### 3. CORS 配置

- 明确允许的域名
- 不使用通配符 `*`
- 支持凭证传递

---

## 监控和日志

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
```

### 关键日志点

```python
# 1. API 请求
logger.info(f"API request: {request.method} {request.url}")

# 2. SSE 连接
logger.info(f"SSE connection established: {request.client.host}")

# 3. 研究任务
logger.info(f"Research started: {prompt}")
logger.info(f"Research completed: {len(report)} chars")

# 4. 错误
logger.error(f"Error: {exc}")
```

---

## 简化设计说明

### 不实现的功能

#### 1. 复杂错误码
**原因**: HTTP 状态码已足够  
**替代**: 使用标准 HTTP 状态码（200, 400, 500）

#### 2. 版本化路由
**原因**: 只有一个版本  
**替代**: 直接使用 /api/ 路径

#### 3. 认证授权
**原因**: MVP 阶段不需要  
**替代**: 延后到 Phase 3 或 Phase 4

#### 4. 速率限制
**原因**: 用户少，平台有基础限制  
**替代**: 使用 Render/Vercel 的限制

#### 5. traceId
**原因**: 日志量小，时间戳足够  
**替代**: 使用时间戳关联日志

#### 6. 心跳机制
**原因**: 浏览器 EventSource 自动重连  
**替代**: 客户端重连逻辑

#### 7. 缓存策略
**原因**: 研究任务每次都不同  
**替代**: 不缓存

---

## 附录

### A. SSE 格式示例

```
event: start
data: {"prompt": "研究量子计算"}

event: plan
data: {"steps": ["搜索资料", "分析数据", "撰写报告"]}

event: progress
data: {"step": 1, "total": 3, "message": "搜索资料"}

event: progress
data: {"step": 2, "total": 3, "message": "分析数据"}

event: progress
data: {"step": 3, "total": 3, "message": "撰写报告"}

event: done
data: {"report": "# 量子计算研究报告\n\n..."}
```

### B. API 文档示例

```markdown
# API 文档

## 健康检查
GET /api/health

响应:
{
  "success": true,
  "data": {"status": "ok"}
}

## 模型列表
GET /api/models

响应:
{
  "success": true,
  "data": {
    "models": [
      {"id": "deepseek-chat", "name": "DeepSeek Chat"},
      {"id": "gpt-4o-mini", "name": "GPT-4o Mini"}
    ]
  }
}

## 流式研究
POST /api/research/stream
Content-Type: application/json

请求:
{
  "prompt": "研究主题"
}

响应: text/event-stream

事件类型:
- start: 开始
- plan: 规划完成
- progress: 进度更新
- done: 完成
- error: 错误
```

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待实施
