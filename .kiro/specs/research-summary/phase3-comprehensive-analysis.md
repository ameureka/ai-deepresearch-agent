# 阶段 3 综合分析报告：Next.js 前端改造（MVP 版本）

## 📋 文档信息

- **阶段**: 阶段 3 - Next.js 前端改造
- **预计时间**: 3 周（15 天）
- **创建日期**: 2025-10-30
- **状态**: ✅ 评估完成 - MVP 方案确定
- **依赖**: 阶段 1 (DeepSeek 集成) + 阶段 2 (API 标准化) 必须完成

---

## 🎯 执行摘要

### 核心目标

**改造 AI Chatbot 为研究助手，保留优秀的对话和 Artifacts 体验**

### MVP 原则

**"保留核心，简化实现，快速上线"**

- ✅ 保留聊天界面和 Artifacts 系统
- ✅ 添加研究工具和实时进度
- ✅ 3 周完成核心功能
- ✅ 延后非必需优化

### 关键决策（已确认）

| 决策点 | 选择 | 理由 |
|--------|------|------|
| **时间** | 3 周 | 去掉第 4 周优化，后续迭代 |
| **traceId** | 不加 | MVP 不需要，增加复杂度 |
| **心跳机制** | 简化 | 只用重连，浏览器自带机制 |
| **回退机制** | 延后 | 直接显示错误，简化实现 |
| **API 路由** | 1 个代理 | 更简单，易维护 |

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

---

## 🔍 深度技术分析

### 1. 架构设计对比

#### 方案对比分析

我们评估了三种方案：

**方案 A: 直接工具调用（❌ 不可行）**
```typescript
// 问题：工具会阻塞 5 分钟
export const startResearch = tool({
  execute: async ({ topic }) => {
    const res = await fetch(`${API}/research`);
    const data = await res.json();  // ❌ 等待 5 分钟
    return data.report;
  }
});
```

**问题**:
- ❌ AI SDK 工具调用是同步的
- ❌ 5 分钟等待会阻塞流式响应
- ❌ 用户看不到任何进度
- ❌ 超时风险高

**方案 B: 工具 + SSE 混合（✅ 采纳）**
```typescript
// 工具立即返回 taskId
export const startResearch = tool({
  execute: async ({ topic }) => {
    const res = await fetch(`${API}/research`, {
      method: 'POST',
      body: JSON.stringify({ prompt: topic }),
    });
    const data = await res.json();
    return { taskId: data.task_id, status: 'started' };  // ✅ 立即返回
  }
});

// 前端订阅 SSE 获取进度
const { progress, status } = useResearchProgress(taskId);
```

**优点**:
- ✅ 工具不阻塞
- ✅ 实时进度显示
- ✅ 保留对话式交互
- ✅ 与阶段 2 的 SSE 完美对接

**方案 C: 直接 SSE（🟡 备选）**
```typescript
// 不用 AI 工具，直接连接 SSE
const eventSource = new EventSource(`${API}/research/stream?prompt=${topic}`);
```

**问题**:
- ❌ 失去对话式交互
- ❌ 不能追问和补充
- ❌ 不符合 ai-chatbot 的设计理念

**最终选择**: 方案 B（工具 + SSE 混合）



### 2. 核心组件设计

#### 2.1 startResearch 工具

**职责**: 启动研究任务，立即返回 taskId

```typescript
// lib/ai/tools/start-research.ts
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
      const firstEvent = JSON.parse(text.split('data: ')[1]);
      
      return {
        taskId: firstEvent.taskId || generateUUID(),
        status: 'started',
        message: `Research task started for: ${topic}`
      };
    } catch (error) {
      return {
        taskId: null,
        status: 'failed',
        error: error.message
      };
    }
  },
});
```

**关键点**:
- ✅ 立即返回，不等待完成
- ✅ 返回 taskId 供前端订阅
- ✅ 简单的错误处理

#### 2.2 useResearchProgress Hook

**职责**: 订阅 SSE，管理进度状态，处理重连

```typescript
// hooks/use-research-progress.ts
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
- ✅ 自动重连（最多 3 次）
- ✅ 指数退避策略（500ms, 1s, 2s）
- ✅ 状态管理清晰
- ✅ 错误处理完善
- ❌ 不需要心跳（浏览器自带）
- ❌ 不需要 traceId（MVP 简化）

#### 2.3 API 代理路由

**职责**: 代理 FastAPI 的 SSE 流，处理 CORS

```typescript
// app/api/research/stream/route.ts
import { NextRequest } from 'next/server';

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
        // 如果需要认证，在这里添加
        // 'Authorization': `Bearer ${token}`,
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
  
  return POST(request);
}
```

**关键点**:
- ✅ 一个路由处理所有请求
- ✅ 支持 POST 和 GET
- ✅ 处理 CORS
- ✅ 错误处理
- ✅ 禁用 Nginx 缓冲



#### 2.4 ResearchProgress 组件

**职责**: 显示研究进度

```typescript
// components/research-progress.tsx
'use client';

import { useResearchProgress } from '@/hooks/use-research-progress';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';

export function ResearchProgress({ taskId }: { taskId: string | null }) {
  const { events, status, report, error } = useResearchProgress(taskId);
  
  if (!taskId) return null;
  
  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center gap-2">
        {status === 'running' && (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
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
- ✅ 简单清晰的进度显示
- ✅ 状态图标
- ✅ 错误提示
- ❌ 不需要复杂的动画（MVP 简化）

#### 2.5 聊天流程改造

**职责**: 集成研究工具，约束 AI 行为

```typescript
// app/(chat)/api/chat/route.ts
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
        // ... 其他配置 ...
      });
      
      result.consumeStream();
      dataStream.merge(result.toUIMessageStream());
    },
    // ... 其他配置 ...
  });
  
  return new Response(stream.pipeThrough(new JsonToSseTransformStream()));
}
```

**System Prompt 更新**:

```typescript
// lib/ai/prompts.ts
export const systemPrompt = ({ selectedChatModel, requestHints }) => {
  const basePrompt = `You are a friendly AI research assistant.`;
  
  const researchPrompt = `
When users ask you to research a topic:
1. Call the startResearch tool with the topic
2. Wait for the research to complete (the UI will show progress)
3. Once complete, call createDocument to create an Artifact with the report
4. If users ask follow-up questions, call updateDocument to refine the report

Example flow:
User: "Research quantum computing"
You: "I'll start researching quantum computing for you..."
[Call startResearch({ topic: "quantum computing" })]
[Wait for completion]
[Call createDocument({ title: "Quantum Computing Research", kind: "text" })]
You: "I've completed the research and created a report for you. What would you like to know more about?"
`;
  
  return `${basePrompt}\n\n${researchPrompt}\n\n${artifactsPrompt}`;
};
```

**关键点**:
- ✅ 明确工具调用顺序
- ✅ 避免 AI 自由发挥
- ✅ 保证流程一致性

### 3. 数据模型设计

#### 3.1 数据库 Schema 扩展

```typescript
// lib/db/schema.ts
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

// 查询函数
export async function saveResearchTask(task: {
  chatId: string;
  userId: string;
  prompt: string;
}) {
  return db.insert(researchTask).values(task).returning();
}

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

export async function getResearchTasksByChatId(chatId: string) {
  return db
    .select()
    .from(researchTask)
    .where(eq(researchTask.chatId, chatId))
    .orderBy(desc(researchTask.createdAt));
}
```

**关键点**:
- ✅ 支持状态追踪
- ✅ 关联 Artifact
- ✅ 保存进度和结果
- ✅ 支持历史查询
- ✅ 错误记录



---

## ⚠️ 风险评估与缓解

### 🔴 高风险

#### 1. SSE 稳定性和代理支持

**风险描述**: Vercel、CDN 或反向代理对 SSE 的支持不一致  
**概率**: 40%  
**影响**: 连接中断，用户看不到进度  
**缓解措施**:

```typescript
// 1. 开发环境直连 FastAPI
const API_URL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000'  // 直连
  : '/api/research';          // 通过代理

// 2. 添加重连机制（已实现）
// 3. 禁用 Nginx 缓冲
headers: {
  'X-Accel-Buffering': 'no',
}

// 4. 预留 fetch + ReadableStream 回退方案
async function fetchWithStream(url: string) {
  const response = await fetch(url);
  const reader = response.body?.getReader();
  // 手动处理流
}
```

#### 2. 工具调用与异步任务协同

**风险描述**: AI 可能不按预期顺序调用工具  
**概率**: 30%  
**影响**: 流程混乱，用户体验差  
**缓解措施**:

```typescript
// 1. System Prompt 明确约束（已实现）
// 2. 工具返回格式标准化
return { taskId, status: 'started' };  // 固定格式

// 3. 前端验证工具调用顺序
if (toolCall.name === 'createDocument' && !researchCompleted) {
  // 警告或阻止
}

// 4. 添加状态机验证
const validTransitions = {
  'idle': ['started'],
  'started': ['running'],
  'running': ['completed', 'failed'],
};
```

### 🟡 中风险

#### 3. 大报告渲染性能

**风险描述**: 长文 Markdown 渲染、代码高亮可能卡顿  
**概率**: 30%  
**影响**: 用户体验下降  
**MVP 方案**: 延后优化

```typescript
// 如果遇到性能问题，后续可以添加：
// 1. 懒加载
// 2. 虚拟滚动
// 3. 代码高亮限制
// 4. 分页或折叠

// MVP 阶段：直接渲染，不优化
```

#### 4. 认证与跨域

**风险描述**: 前端与 FastAPI 的认证传递  
**概率**: 40%  
**影响**: 无法调用 API  
**缓解措施**:

```typescript
// 方案 1: 简单 API Key（开发环境）
headers: {
  'X-API-Key': process.env.RESEARCH_API_KEY,
}

// 方案 2: 传递用户 token（生产环境）
const session = await auth();
headers: {
  'Authorization': `Bearer ${session.user.token}`,
}

// CORS 配置（FastAPI）
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000", "https://your-app.vercel.app"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)
```

### 🟢 低风险

#### 5. UI 组件适配

**风险描述**: 删除功能时误删核心组件  
**概率**: 10%  
**影响**: 功能损坏  
**缓解措施**:

```bash
# 严格控制删除范围
删除：
- lib/ai/tools/get-weather.ts  ✅
- components/image-editor.tsx   ✅
- components/sheet-editor.tsx   ✅

保留：
- components/chat.tsx           ✅ 核心
- components/artifact.tsx       ✅ 核心
- components/text-editor.tsx    ✅ 需要
- components/code-editor.tsx    ✅ 需要
```

---

## 📋 详细实施计划（3 周）

### Week 1: 架构与工具桥接（5 天）

#### Day 1: 环境准备与工具创建

**任务**:
1. 配置环境变量
2. 创建 startResearch 工具
3. 基础测试

**代码**:
```bash
# 1. 添加环境变量
echo "RESEARCH_API_URL=http://localhost:8000" >> .env.local

# 2. 创建工具文件
touch lib/ai/tools/start-research.ts

# 3. 测试工具
npm run dev
```

**验收**:
- ✅ 环境变量配置正确
- ✅ 工具可以调用
- ✅ 返回 taskId

#### Day 2: API 代理路由

**任务**:
1. 创建 API 代理
2. 处理 CORS
3. 测试 SSE 流

**代码**:
```bash
# 创建代理路由
mkdir -p app/api/research/stream
touch app/api/research/stream/route.ts

# 测试
curl -N http://localhost:3000/api/research/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

**验收**:
- ✅ 代理正常工作
- ✅ SSE 流可以接收
- ✅ CORS 配置正确

#### Day 3-4: useResearchProgress Hook

**任务**:
1. 创建 Hook
2. 实现重连逻辑
3. 状态管理

**代码**:
```bash
# 创建 Hook
touch hooks/use-research-progress.ts

# 测试
# 在组件中使用并验证
```

**验收**:
- ✅ SSE 订阅正常
- ✅ 重连机制工作（3 次）
- ✅ 状态更新正确

#### Day 5: 集成测试

**任务**:
1. 端到端测试
2. 修复 bug
3. 代码审查

**验收**:
- ✅ 工具 → API → SSE 全流程通
- ✅ 无明显 bug

### Week 2: 聊天流程与组件（5 天）

#### Day 1-2: 改造聊天流程

**任务**:
1. 集成 startResearch 工具
2. 更新 System Prompt
3. 测试工具调用

**代码**:
```typescript
// app/(chat)/api/chat/route.ts
tools: {
  createDocument,
  updateDocument,
  startResearch,  // 新增
}
```

**验收**:
- ✅ AI 可以调用研究工具
- ✅ 返回 taskId
- ✅ 流程符合预期

#### Day 3: ResearchProgress 组件

**任务**:
1. 创建进度组件
2. 集成到聊天界面
3. 样式调整

**代码**:
```bash
touch components/research-progress.tsx
```

**验收**:
- ✅ 进度显示正常
- ✅ 状态图标正确
- ✅ 样式美观

#### Day 4: Artifact 集成

**任务**:
1. 研究完成后自动创建 Artifact
2. 测试报告显示
3. 测试更新功能

**验收**:
- ✅ 报告自动生成
- ✅ Artifact 显示正常
- ✅ 可以更新报告

#### Day 5: 集成测试

**任务**:
1. 完整流程测试
2. 用户体验优化
3. Bug 修复

**验收**:
- ✅ 完整流程通畅
- ✅ 用户体验良好

### Week 3: 数据库与完善（5 天）

#### Day 1-2: 数据库扩展

**任务**:
1. 添加 research_task 表
2. 实现查询函数
3. 集成到流程

**代码**:
```bash
# 生成迁移
npm run db:generate

# 执行迁移
npm run db:migrate
```

**验收**:
- ✅ 表结构正确
- ✅ 数据可以保存
- ✅ 历史可以查询

#### Day 3: 错误处理与重连

**任务**:
1. 完善错误处理
2. 测试重连机制
3. 添加错误提示

**验收**:
- ✅ 错误提示友好
- ✅ 重连机制稳定
- ✅ 不会崩溃

#### Day 4: 端到端测试

**任务**:
1. 完整流程测试
2. 边界情况测试
3. 性能测试

**测试用例**:
```
1. 正常研究流程
2. 研究失败情况
3. 网络中断重连
4. 多个研究任务
5. 追问和更新
```

**验收**:
- ✅ 所有测试通过
- ✅ 无明显性能问题

#### Day 5: 文档与部署准备

**任务**:
1. 更新 README
2. 添加环境变量说明
3. 准备部署配置

**验收**:
- ✅ 文档完整
- ✅ 配置清晰
- ✅ 可以部署



---

## ✅ 验收标准（MVP 版本）

### 核心功能验收

- [ ] **研究发起**
  - [ ] 用户可以在聊天中发起研究
  - [ ] AI 正确调用 startResearch 工具
  - [ ] 返回有效的 taskId

- [ ] **实时进度**
  - [ ] 进度组件正常显示
  - [ ] SSE 事件正确接收
  - [ ] 状态更新及时
  - [ ] 进度信息清晰

- [ ] **报告生成**
  - [ ] 研究完成后自动创建 Artifact
  - [ ] 报告内容完整
  - [ ] Markdown 渲染正确
  - [ ] 可以导出

- [ ] **追问更新**
  - [ ] 用户可以追问
  - [ ] AI 调用 updateDocument
  - [ ] 报告正确更新

- [ ] **错误处理**
  - [ ] 研究失败显示错误
  - [ ] 网络错误有提示
  - [ ] 不会崩溃

- [ ] **断线重连**
  - [ ] 连接断开自动重连
  - [ ] 最多重试 3 次
  - [ ] 重连后状态正确

### 数据持久化验收

- [ ] **任务保存**
  - [ ] 研究任务保存到数据库
  - [ ] 状态正确更新
  - [ ] 关联 Artifact

- [ ] **历史查询**
  - [ ] 可以查看历史研究
  - [ ] 按聊天分组
  - [ ] 时间排序正确

### 性能验收（基础）

- [ ] **响应时间**
  - [ ] 工具调用 < 1 秒
  - [ ] SSE 首个事件 < 2 秒
  - [ ] 页面不卡顿

- [ ] **稳定性**
  - [ ] 连续 5 次研究无错误
  - [ ] 长时间运行无内存泄漏
  - [ ] 多标签页正常工作

### 不验收的项目（延后）

- ❌ 性能优化（懒加载、虚拟滚动）
- ❌ 回退机制（失败生成摘要）
- ❌ traceId 追踪
- ❌ 心跳机制
- ❌ 高级错误分类
- ❌ 性能指标监控

---

## 🔄 与其他阶段的集成

### 依赖阶段 1（DeepSeek 集成）

**需要的产出**:
- ✅ FastAPI 后端正常运行
- ✅ DeepSeek 模型配置正确
- ✅ 研究流程可以执行

**集成点**:
- 前端调用后端 API
- 使用相同的模型配置

### 依赖阶段 2（API 标准化）

**需要的产出**:
- ✅ `/api/research/stream` SSE 接口
- ✅ 统一的事件格式
- ✅ 错误处理机制

**集成点**:
- 前端订阅 SSE
- 解析事件格式
- 处理错误

### 为阶段 4 准备（整合部署）

**提供的产出**:
- ✅ 完整的前端应用
- ✅ 环境变量配置
- ✅ 数据库 Schema

**集成点**:
- 前后端联调
- 环境变量配置
- 数据库迁移

---

## 📊 功能对比分析

### 原路线图 vs 最终方案

| 功能 | 原路线图 | 最终方案 | 变更理由 |
|------|---------|---------|---------|
| **时间** | 2-3 周 | 3 周 | 更现实的估算 |
| **工具调用** | 直接等待 | 返回 taskId | 避免阻塞 |
| **进度显示** | 未明确 | SSE + Hook | 实时性好 |
| **API 路由** | 未明确 | 1 个代理 | 简化实现 |
| **traceId** | 未提及 | 不加 | MVP 简化 |
| **心跳** | 未提及 | 简化 | 浏览器自带 |
| **回退机制** | 未提及 | 延后 | MVP 简化 |
| **性能优化** | 未提及 | 延后 | MVP 简化 |
| **数据模型** | 简单 | 扩展 | 支持历史 |
| **错误处理** | 未明确 | 完善 | 用户体验 |

### 多方案对比

| 方案 | 我的分析 | 其他模型分析 | 最终方案 |
|------|---------|-------------|---------|
| **架构** | 混合架构 | 混合架构 | ✅ 一致 |
| **工具协议** | 返回 taskId | 返回 taskId | ✅ 一致 |
| **SSE Hook** | 基础版 | 完整版 | ✅ 采纳完整版 |
| **时间** | 2-3 周 | 3-4 周 | ✅ 3 周（折中）|
| **traceId** | 不加 | 加 | ✅ 不加（MVP）|
| **心跳** | 简化 | 完整 | ✅ 简化（MVP）|
| **回退** | 不加 | 加 | ✅ 不加（MVP）|
| **API 路由** | 1 个 | 2 个 | ✅ 1 个（简化）|

---

## 💡 关键决策记录

### 决策 1: 时间设定为 3 周

**背景**: 原路线图 2-3 周，其他分析 3-4 周  
**决策**: 3 周  
**理由**:
- ✅ 去掉第 4 周的优化
- ✅ 简化非必需功能
- ✅ 后续可迭代

### 决策 2: 不添加 traceId

**背景**: 其他分析建议添加  
**决策**: 不加  
**理由**:
- ✅ MVP 不需要
- ✅ 增加复杂度
- ✅ 调试可以用其他方式

### 决策 3: 简化心跳机制

**背景**: 其他分析建议完整心跳  
**决策**: 只用重连  
**理由**:
- ✅ 浏览器 EventSource 自带重连
- ✅ 3 次重试够用
- ✅ 减少实现复杂度

### 决策 4: 延后回退机制

**背景**: 其他分析建议失败时生成摘要  
**决策**: 直接显示错误  
**理由**:
- ✅ MVP 简化
- ✅ 需要额外 AI 调用
- ✅ 增加复杂度

### 决策 5: 使用 1 个 API 代理

**背景**: 其他分析建议 2 个接口  
**决策**: 1 个代理  
**理由**:
- ✅ 更简单
- ✅ 易维护
- ✅ 与阶段 2 一致

---

## 🎯 成功标准

### 技术标准

- ✅ 所有核心功能正常工作
- ✅ 无阻塞性 bug
- ✅ 代码质量良好
- ✅ 测试覆盖核心流程

### 用户体验标准

- ✅ 研究流程顺畅
- ✅ 进度显示清晰
- ✅ 错误提示友好
- ✅ 响应速度可接受

### 项目标准

- ✅ 按时完成（3 周）
- ✅ 文档完整
- ✅ 可以部署
- ✅ 为阶段 4 做好准备

---

## 📝 下一步行动

### 立即开始（Week 1 Day 1）

**上午**:
1. ✅ 配置环境变量
2. ✅ 创建 startResearch 工具
3. ✅ 基础测试

**下午**:
1. ✅ 创建 API 代理路由
2. ✅ 测试 SSE 流
3. ✅ 处理 CORS

### 本周目标（Week 1）

1. ✅ 完成工具和 API 代理
2. ✅ 实现 useResearchProgress Hook
3. ✅ 基础集成测试通过

### 本月目标（3 周）

1. ✅ 完成所有核心功能
2. ✅ 通过验收标准
3. ✅ 准备好部署

---

## 🎉 总结

### 核心成果

1. **架构清晰** ✅
   - 工具 + SSE 混合方案
   - 职责分离明确
   - 易于维护

2. **实现简化** ✅
   - 去掉非必需功能
   - 保留核心体验
   - 3 周可完成

3. **风险可控** ✅
   - 主要风险已识别
   - 缓解措施明确
   - 有备选方案

4. **质量保证** ✅
   - 验收标准清晰
   - 测试覆盖核心
   - 用户体验优先

### MVP 原则体现

**"保留核心，简化实现，快速上线"**

- ✅ 保留：对话、Artifacts、实时进度
- ✅ 简化：traceId、心跳、回退、优化
- ✅ 延后：性能优化、高级功能

### 与其他阶段的协同

- ✅ 依赖阶段 1 的后端
- ✅ 依赖阶段 2 的 API
- ✅ 为阶段 4 做好准备

---

**创建日期**: 2025-10-30  
**版本**: 1.0 (MVP)  
**状态**: ✅ 评估完成 - 方案确定  
**建议**: 立即开始开发，3 周完成核心功能
