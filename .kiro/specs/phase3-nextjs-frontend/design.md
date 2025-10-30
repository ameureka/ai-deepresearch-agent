# Phase 3: Next.js 前端改造 - 设计文档

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 3 - Next.js 前端改造
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **状态**: 待实施
- **依赖**: Phase 1 + Phase 2 必须完成

---

## 概述

### 设计目标

Phase 3 的设计目标是改造 AI Chatbot 为研究助手：

1. **保留核心**: 对话界面、Artifacts 系统
2. **添加研究**: startResearch 工具、实时进度
3. **简化实现**: MVP 原则，3 周完成
4. **用户体验**: 流畅的研究体验

### MVP 原则

**"保留核心，简化实现，快速上线"**

**包含**:
- ✅ startResearch 工具
- ✅ useResearchProgress Hook
- ✅ API 代理路由（1 个）
- ✅ ResearchProgress 组件
- ✅ 数据库 Schema 扩展
- ✅ 聊天流程改造
- ✅ Artifact 集成

**不包含**（延后）:
- ❌ traceId 追踪
- ❌ 复杂心跳机制
- ❌ 回退机制
- ❌ 性能优化（懒加载、虚拟滚动）
- ❌ 高级错误分类

---

## 架构设计

### 技术方案

**工具调用 + SSE 订阅的混合架构**

```
用户输入 → AI 理解意图 → 调用 startResearch 工具（返回 taskId）
  ↓
前端订阅 SSE（/api/research/stream）→ 实时显示进度
  ↓
研究完成 → AI 调用 createDocument → 生成 Artifact 报告
  ↓
用户追问 → AI 调用 updateDocument → 更新报告
```

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Application                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Chat Interface                       │   │
│  │  - User Input                                     │   │
│  │  - Message List                                   │   │
│  │  - ResearchProgress Component                    │   │
│  └────────────────┬─────────────────────────────────┘   │
│                   │                                       │
│                   ▼                                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │           AI SDK (streamText)                     │   │
│  │  - System Prompt                                  │   │
│  │  - Tools: startResearch, createDocument, etc.    │   │
│  └────────┬─────────────────────┬───────────────────┘   │
│           │                     │                         │
│           ▼                     ▼                         │
│  ┌────────────────┐   ┌────────────────────────┐        │
│  │ startResearch  │   │   createDocument       │        │
│  │     Tool       │   │       Tool             │        │
│  └────────┬───────┘   └────────────────────────┘        │
│           │                                               │
│           ▼                                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │         API Proxy Route                           │   │
│  │  POST /api/research/stream                        │   │
│  │  GET  /api/research/stream?taskId=xxx            │   │
│  └────────┬─────────────────────────────────────────┘   │
│           │                                               │
│           ▼                                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │      useResearchProgress Hook                     │   │
│  │  - EventSource Connection                         │   │
│  │  - Event Handling                                 │   │
│  │  - State Management                               │   │
│  │  - Reconnection Logic                             │   │
│  └────────┬─────────────────────────────────────────┘   │
│           │                                               │
│           ▼                                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │      ResearchProgress Component                   │   │
│  │  - Status Display                                 │   │
│  │  - Progress List                                  │   │
│  │  - Error Display                                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Artifact Display                     │   │
│  │  - Research Report                                │   │
│  │  - Markdown Rendering                             │   │
│  │  - Copy/Export                                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Database (Drizzle ORM)                  │   │
│  │  - researchTask Table                             │   │
│  │  - Save/Query Functions                           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
└───────────────────────┬───────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   FastAPI Backend   │
              │  (Phase 2 API)      │
              └─────────────────────┘
```

---

## 组件设计

### 1. startResearch 工具

**文件**: `lib/ai/tools/start-research.ts`

**职责**: 启动研究任务，立即返回 taskId

**接口设计**:

```typescript
import { tool } from 'ai';
import { z } from 'zod';

export const startResearch = tool({
  description: 'Start a comprehensive research task on a given topic',
  inputSchema: z.object({
    topic: z.string().describe('The research topic or question'),
  }),
  execute: async ({ topic }) => {
    const RESEARCH_API = process.env.RESEARCH_API_URL!;
    
    try {
      const res = await fetch(`${RESEARCH_API}/api/research/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: topic }),
      });
      
      if (!res.ok) {
        throw new Error(`Research API error: ${res.status}`);
      }
      
      // 从响应头或首个事件中获取 taskId
      const reader = res.body?.getReader();
      const { value } = await reader!.read();
      const text = new TextDecoder().decode(value);
      
      // 解析首个事件获取 taskId
      const firstEvent = JSON.parse(text.split('data: ')[1]);
      const taskId = firstEvent.taskId || generateUUID();
      
      return {
        taskId,
        status: 'started',
        message: `Research task started for: ${topic}`
      };
    } catch (error) {
      console.error('startResearch error:', error);
      return {
        taskId: null,
        status: 'failed',
        error: error.message
      };
    }
  },
});

function generateUUID(): string {
  return crypto.randomUUID();
}
```

**关键点**:
- 立即返回，不等待完成
- 返回 taskId 供前端订阅
- 简单的错误处理
- 不阻塞 AI 流式响应

### 2. useResearchProgress Hook

**文件**: `hooks/use-research-progress.ts`

**职责**: 订阅 SSE，管理进度状态，处理重连

**接口设计**:

```typescript
import { useState, useEffect } from 'react';

type ProgressEvent = {
  type: 'start' | 'plan' | 'progress' | 'done' | 'error';
  data: any;
};

type ResearchStatus = 'idle' | 'running' | 'completed' | 'failed';

export function useResearchProgress(taskId: string | null) {
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [status, setStatus] = useState<ResearchStatus>('idle');
  const [report, setReport] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (!taskId) return;
    
    let retries = 0;
    const MAX_RETRIES = 3;
    let eventSource: EventSource | null = null;
    
    const connect = () => {
      // 通过 Next.js API 代理连接
      const url = `/api/research/stream?taskId=${taskId}`;
      eventSource = new EventSource(url);
      
      eventSource.onopen = () => {
        console.log('SSE connected');
        setStatus('running');
        retries = 0;  // 重置重试计数
      };
      
      eventSource.onmessage = (e) => {
        try {
          const event: ProgressEvent = JSON.parse(e.data);
          
          // 添加到事件列表
          setEvents(prev => [...prev, event]);
          
          // 处理不同类型的事件
          switch (event.type) {
            case 'start':
              setStatus('running');
              break;
            case 'progress':
              // 更新进度
              break;
            case 'done':
              setStatus('completed');
              setReport(event.data.report);
              eventSource?.close();
              break;
            case 'error':
              setStatus('failed');
              setError(event.data.message);
              eventSource?.close();
              break;
          }
        } catch (err) {
          console.error('Failed to parse SSE event:', err);
        }
      };
      
      eventSource.onerror = (err) => {
        console.error('SSE error:', err);
        eventSource?.close();
        
        // 重连逻辑（指数退避）
        if (retries < MAX_RETRIES) {
          retries++;
          const delay = 500 * Math.pow(2, retries - 1);  // 500ms, 1s, 2s
          console.log(`Reconnecting in ${delay}ms (attempt ${retries}/${MAX_RETRIES})`);
          setTimeout(connect, delay);
        } else {
          setStatus('failed');
          setError('Connection failed after 3 retries');
        }
      };
    };
    
    setStatus('running');
    connect();
    
    // 清理函数
    return () => {
      eventSource?.close();
      setStatus('idle');
    };
  }, [taskId]);
  
  return { events, status, report, error };
}
```

**关键点**:
- 自动重连（最多 3 次）
- 指数退避策略（500ms, 1s, 2s）
- 状态管理清晰
- 错误处理完善
- 组件卸载时清理

### 3. API 代理路由

**文件**: `app/api/research/stream/route.ts`

**职责**: 代理 FastAPI 的 SSE 流，处理 CORS

**接口设计**:

```typescript
import { NextRequest } from 'next/server';

export const runtime = 'nodejs';  // 使用 Node.js runtime，不用 edge

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json();
    
    const RESEARCH_API = process.env.RESEARCH_API_URL;
    if (!RESEARCH_API) {
      return new Response(
        JSON.stringify({ error: 'RESEARCH_API_URL not configured' }),
        { status: 500 }
      );
    }
    
    // 代理到 FastAPI
    const response = await fetch(`${RESEARCH_API}/api/research/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });
    
    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: `FastAPI error: ${response.status}` }),
        { status: response.status }
      );
    }
    
    // 返回 SSE 流
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',  // 禁用 Nginx 缓冲
      },
    });
  } catch (error) {
    console.error('API proxy error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500 }
    );
  }
}

// 支持 GET 方法（用于 EventSource）
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const taskId = searchParams.get('taskId');
  const prompt = searchParams.get('prompt');
  
  if (!prompt && !taskId) {
    return new Response('Missing prompt or taskId', { status: 400 });
  }
  
  // 如果有 taskId，可以从数据库恢复
  // 如果有 prompt，启动新任务
  
  // 简化实现：直接代理
  return POST(request);
}
```

**关键点**:
- 一个路由处理所有请求
- 支持 POST 和 GET
- 处理 CORS
- 错误处理
- 禁用 Nginx 缓冲

### 4. ResearchProgress 组件

**文件**: `components/research-progress.tsx`

**职责**: 显示研究进度

**接口设计**:

```typescript
'use client';

import { useResearchProgress } from '@/hooks/use-research-progress';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';

export function ResearchProgress({ taskId }: { taskId: string | null }) {
  const { events, status, report, error } = useResearchProgress(taskId);
  
  if (!taskId) return null;
  
  return (
    <div className="border rounded-lg p-4 space-y-3">
      {/* 状态头部 */}
      <div className="flex items-center gap-2">
        {status === 'running' && (
          <>
            <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
            <span className="text-sm font-medium">Research in progress...</span>
          </>
        )}
        {status === 'completed' && (
          <>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium">Research completed!</span>
          </>
        )}
        {status === 'failed' && (
          <>
            <XCircle className="h-4 w-4 text-red-600" />
            <span className="text-sm font-medium">Research failed</span>
          </>
        )}
      </div>
      
      {/* 进度列表 */}
      <div className="space-y-2">
        {events.map((event, index) => (
          <div key={index} className="text-sm text-muted-foreground">
            {event.type === 'progress' && (
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-blue-500" />
                <span>
                  Step {event.data.step}/{event.data.total}: {event.data.message}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* 错误信息 */}
      {error && (
        <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
          {error}
        </div>
      )}
    </div>
  );
}
```

**关键点**:
- 简单清晰的进度显示
- 状态图标
- 错误提示
- 响应式设计

### 5. 聊天流程改造

**文件**: `app/(chat)/api/chat/route.ts`

**职责**: 集成研究工具，约束 AI 行为

**关键修改**:

```typescript
import { startResearch } from '@/lib/ai/tools/start-research';

export async function POST(request: Request) {
  // ... 现有代码 ...
  
  const stream = createUIMessageStream({
    execute: ({ writer: dataStream }) => {
      const result = streamText({
        model: myProvider.languageModel(selectedChatModel),
        system: systemPrompt({ selectedChatModel, requestHints }),
        messages: convertToModelMessages(uiMessages),
        tools: {
          // 现有工具
          createDocument: createDocument({ session, dataStream }),
          updateDocument: updateDocument({ session, dataStream }),
          
          // 新增研究工具
          startResearch,  // ✅ 添加研究工具
        },
        onFinish: async ({ usage }) => {
          dataStream.write({ type: "data-usage", data: usage });
        },
      });
      
      result.consumeStream();
      dataStream.merge(result.toUIMessageStream());
    },
  });
  
  return new Response(stream.pipeThrough(new JsonToSseTransformStream()));
}
```

### 6. System Prompt 更新

**文件**: `lib/ai/prompts.ts`

**新增研究提示**:

```typescript
export const systemPrompt = ({ selectedChatModel, requestHints }) => {
  const basePrompt = `You are a friendly AI research assistant.`;
  
  const researchPrompt = `
When users ask you to research a topic:
1. Call the startResearch tool with the topic
2. Inform the user that research has started
3. Wait for the research to complete (the UI will show progress automatically)
4. Once complete, call createDocument to create an Artifact with the report
5. If users ask follow-up questions, call updateDocument to refine the report

Example flow:
User: "Research quantum computing"
You: "I'll start researching quantum computing for you. This may take a few minutes..."
[Call startResearch({ topic: "quantum computing" })]
[System shows progress automatically]
[When research completes, you receive the report]
[Call createDocument({ title: "Quantum Computing Research", kind: "text", content: report })]
You: "I've completed the research and created a report for you. What would you like to know more about?"

Important:
- Always call startResearch first
- Don't try to research yourself
- Wait for the tool to return before creating the document
- The progress is shown automatically, you don't need to describe it
`;
  
  return `${basePrompt}\n\n${researchPrompt}\n\n${artifactsPrompt}`;
};
```

**关键点**:
- 明确工具调用顺序
- 避免 AI 自由发挥
- 保证流程一致性

---

## 数据模型设计

### 数据库 Schema 扩展

**文件**: `lib/db/schema.ts`

**新增表**:

```typescript
import { pgTable, uuid, varchar, text, timestamp, json } from 'drizzle-orm/pg-core';

export const researchTask = pgTable('research_task', {
  id: uuid('id').primaryKey().defaultRandom(),
  chatId: uuid('chat_id').references(() => chat.id).notNull(),
  userId: uuid('user_id').references(() => user.id).notNull(),
  
  // 任务信息
  prompt: text('prompt').notNull(),
  status: varchar('status', { length: 20 }).notNull().default('started'),
  // status: 'started' | 'running' | 'completed' | 'failed'
  
  // 关联信息
  artifactId: uuid('artifact_id'),  // 关联生成的 Artifact
  
  // 进度和结果
  progress: json('progress').$type<{
    currentStep: number;
    totalSteps: number;
    steps: Array<{ name: string; status: string }>;
  }>(),
  
  result: text('result'),  // 最终报告
  error: text('error'),    // 错误信息
  
  // 时间戳
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
});
```

**查询函数**:

```typescript
// 保存研究任务
export async function saveResearchTask(task: {
  chatId: string;
  userId: string;
  prompt: string;
}) {
  return db.insert(researchTask).values(task).returning();
}

// 更新研究任务状态
export async function updateResearchTaskStatus(
  id: string,
  status: string,
  data?: { progress?: any; result?: string; error?: string }
) {
  return db
    .update(researchTask)
    .set({
      status,
      ...data,
      updatedAt: new Date(),
      ...(status === 'completed' || status === 'failed' 
        ? { completedAt: new Date() } 
        : {}),
    })
    .where(eq(researchTask.id, id));
}

// 查询聊天的研究任务
export async function getResearchTasksByChatId(chatId: string) {
  return db
    .select()
    .from(researchTask)
    .where(eq(researchTask.chatId, chatId))
    .orderBy(desc(researchTask.createdAt));
}
```

---

## 错误处理策略

### 错误分类

1. **工具调用错误**
   - API 不可达
   - 请求超时
   - 返回格式错误

2. **SSE 连接错误**
   - 连接失败
   - 连接中断
   - 事件解析错误

3. **研究过程错误**
   - 后端执行失败
   - 数据格式错误
   - 超时

### 错误处理实现

```typescript
// 1. 工具调用错误
try {
  const result = await startResearch({ topic });
  if (result.status === 'failed') {
    // 显示错误给用户
    return `Failed to start research: ${result.error}`;
  }
} catch (error) {
  console.error('Tool error:', error);
  return 'Failed to start research. Please try again.';
}

// 2. SSE 连接错误
eventSource.onerror = (err) => {
  console.error('SSE error:', err);
  
  // 尝试重连
  if (retries < MAX_RETRIES) {
    retries++;
    setTimeout(connect, delay);
  } else {
    // 显示错误
    setError('Connection failed after 3 retries');
  }
};

// 3. 研究过程错误
if (event.type === 'error') {
  setStatus('failed');
  setError(event.data.message);
  // 关闭连接
  eventSource?.close();
}
```

---

## 测试策略

### 单元测试

**测试范围**:
1. startResearch 工具
   - 成功调用
   - 失败处理
   - taskId 生成

2. useResearchProgress Hook
   - 状态管理
   - 事件处理
   - 重连逻辑

3. 数据库函数
   - 保存任务
   - 更新状态
   - 查询任务

**测试工具**: Jest + React Testing Library

### 集成测试

**测试场景**:
1. 完整研究流程
   - 用户发起研究
   - 工具调用
   - SSE 连接
   - 进度显示
   - 报告生成

2. 错误场景
   - API 失败
   - 连接中断
   - 研究失败

### 端到端测试

**测试工具**: Playwright

**测试用例**:
1. 用户注册/登录
2. 发起研究任务
3. 查看实时进度
4. 查看生成的报告
5. 追问和更新
6. 查看历史记录

---

## 性能优化

### 1. 组件优化

```typescript
// 使用 React.memo 避免不必要的重渲染
export const ResearchProgress = React.memo(({ taskId }) => {
  // ...
});

// 使用 useMemo 缓存计算结果
const progressPercentage = useMemo(() => {
  if (!events.length) return 0;
  const progressEvents = events.filter(e => e.type === 'progress');
  // ...
}, [events]);
```

### 2. 连接管理

```typescript
// 确保只有一个 EventSource 连接
useEffect(() => {
  // ...
  return () => {
    eventSource?.close();  // 清理
  };
}, [taskId]);
```

### 3. 状态更新优化

```typescript
// 使用函数式更新避免闭包问题
setEvents(prev => [...prev, event]);
```

---

## 部署考虑

### 环境变量

**必需**:
- RESEARCH_API_URL（后端 API URL）
- DATABASE_URL（数据库连接）
- AUTH_SECRET（认证密钥）
- NEXTAUTH_URL（NextAuth URL）

**示例** (`.env.example`):
```bash
# Research API
RESEARCH_API_URL=http://localhost:8000

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/research

# Auth
AUTH_SECRET=your-secret-here
NEXTAUTH_URL=http://localhost:3000
```

### Vercel 配置

**环境变量配置**:
```bash
vercel env add RESEARCH_API_URL
# 输入: https://research-backend.onrender.com

vercel env add DATABASE_URL
# 输入: postgresql://...neon.tech/db

vercel env add AUTH_SECRET
# 输入: 随机字符串

vercel env add NEXTAUTH_URL
# 输入: https://your-app.vercel.app
```

---

## 附录

### A. 事件流示例

```
用户: "研究量子计算"
  ↓
AI: "我将为你研究量子计算..."
  ↓
[调用 startResearch({ topic: "量子计算" })]
  ↓
返回: { taskId: "abc-123", status: "started" }
  ↓
[前端订阅 SSE: /api/research/stream?taskId=abc-123]
  ↓
接收事件:
  event: start
  data: {"prompt": "量子计算"}
  
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
  ↓
[AI 调用 createDocument({ title: "量子计算研究", content: report })]
  ↓
AI: "研究完成！我已经创建了一份报告。"
```

### B. 组件层次结构

```
App
├── Chat Page
│   ├── Chat Interface
│   │   ├── Message List
│   │   │   ├── User Message
│   │   │   ├── AI Message
│   │   │   └── ResearchProgress ← 新增
│   │   └── Input Area
│   └── Artifact Display
│       └── Research Report ← 新增
└── API Routes
    └── /api/research/stream ← 新增
```

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待实施
