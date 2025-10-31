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
2. **添加研究**: 用户触发研究、实时进度显示
3. **简化实现**: MVP 原则，3 周完成
4. **用户体验**: 流畅的研究体验

### 架构变更说明 ⚠️

**原架构问题**: AI SDK 工具调用模式（startResearch）不适合长时间 SSE 连接，execute 函数返回后会导致 SSE 流关闭

**新架构方案**: 用户手动触发 + 直接 SSE 订阅
- 用户点击 ResearchButton 发起研究
- useResearchProgress Hook 直接 POST SSE 连接
- Hook 通过 onComplete 回调通知父组件
- 父组件通过 `sendMessage` (from `useChat`) 发送报告给 AI
- AI 调用 createDocument 生成 Artifact

### MVP 原则

**"保留核心，简化实现，快速上线"**

**包含**:
- ✅ ResearchButton 组件（用户触发）
- ✅ useResearchProgress Hook（接受 prompt）
- ✅ API 代理路由（仅 POST）
- ✅ ResearchProgress 组件
- ✅ 数据库 Schema 扩展
- ✅ 聊天流程改造
- ✅ Artifact 集成

**不包含**（延后）:
- ❌ startResearch 工具（架构调整，已删除）
- ❌ traceId 追踪
- ❌ 复杂心跳机制
- ❌ 回退机制
- ❌ 性能优化（懒加载、虚拟滚动）
- ❌ 高级错误分类

---

## 架构设计

### 技术方案

**用户触发 + 直接 SSE 订阅架构**

```
用户输入（包含研究关键词）→ 聊天界面检测关键词 → 显示 ResearchButton
  ↓
用户点击按钮 → useResearchProgress Hook 发起 POST SSE 连接
  ↓
实时接收进度事件 → ResearchProgress 组件显示进度
  ↓
研究完成 → Hook 调用 onComplete 回调 → 父组件通过 sendMessage 发送报告给 AI
  ↓
AI 调用 createDocument → 生成 Artifact 报告
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
│  │  - User Input (关键词检测)                        │   │
│  │  - ResearchButton (用户触发) ⭐ 新增              │   │
│  │  - Message List                                   │   │
│  │  - ResearchProgress Component                    │   │
│  └────────┬─────────────────────────┬─────────────────┘   │
│           │                         │                     │
│           │                         ▼                     │
│           │         ┌────────────────────────────┐       │
│           │         │  useResearchProgress Hook  │       │
│           │         │  - fetch-event-source      │       │
│           │         │  - POST SSE Connection     │       │
│           │         │  - State Management        │       │
│           │         │  - onComplete Callback     │       │
│           │         └──────────┬─────────────────┘       │
│           │                    │                         │
│           │                    ▼                         │
│           │         ┌────────────────────────────┐       │
│           │         │    API Proxy Route         │       │
│           │         │ POST /api/research/stream  │       │
│           │         └──────────┬─────────────────┘       │
│           │                    │                         │
│           │                    ▼                         │
│           │         ┌────────────────────────────┐       │
│           │         │   FastAPI Backend          │       │
│           │         │  POST /api/research/stream │       │
│           │         │  (Phase 2 API)             │       │
│           │         └──────────┬─────────────────┘       │
│           │                    │                         │
│           │                    │ SSE Events              │
│           │                    │ (start/plan/progress/   │
│           │                    │  done/error)            │
│           │                    ▼                         │
│           │         ┌────────────────────────────┐       │
│           │         │ ResearchProgress Component │       │
│           │         │  - Status Display          │       │
│           │         │  - Progress List           │       │
│           │         │  - Error Display           │       │
│           │         └────────────────────────────┘       │
│           │                                               │
│           │ (研究完成后，sendMessage 发送报告)            │
│           ▼                                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │           AI SDK (streamText)                     │   │
│  │  - System Prompt                                  │   │
│  │  - Tools: createDocument, updateDocument         │   │
│  │  - 接收报告，调用 createDocument                  │   │
│  └────────┬─────────────────────────────────────────┘   │
│           │                                               │
│           ▼                                               │
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
└─────────────────────────────────────────────────────────┘
```

---

## 组件设计

### ~~1. startResearch 工具~~ (已删除 - 架构调整)

**变更说明**:
- **原设计问题**: AI SDK 工具调用模式不适合长时间 SSE 连接，execute 函数返回后会导致 SSE 流关闭
- **解决方案**: 采用用户手动触发 + 直接 SSE 订阅的架构（见组件 7: ResearchButton）
- **影响**: 不再需要 taskId，Hook 直接接受 prompt 参数发起研究

### 1. ResearchButton 组件 ⭐ (新增)

**文件**: `components/research-button.tsx`

**职责**: 用户手动触发研究任务

**接口设计**:

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';

interface ResearchButtonProps {
  prompt: string;  // 从用户输入中提取的研究主题
  onStart: (prompt: string) => void;  // 启动研究的回调
  disabled?: boolean;
}

export function ResearchButton({ prompt, onStart, disabled }: ResearchButtonProps) {
  const [isStarting, setIsStarting] = useState(false);

  const handleClick = async () => {
    setIsStarting(true);
    try {
      await onStart(prompt);
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <Button
      onClick={handleClick}
      disabled={disabled || isStarting}
      variant="outline"
      size="sm"
      className="gap-2"
    >
      <Sparkles className="h-4 w-4" />
      {isStarting ? 'Starting research...' : 'Start Research'}
    </Button>
  );
}
```

**关键词检测逻辑**:

```typescript
// 在聊天界面中检测研究关键词
function detectResearchIntent(message: string): string | null {
  const keywords = ['research', '研究', 'investigate', '调查', 'analyze', '分析'];
  const lowerMsg = message.toLowerCase();

  for (const keyword of keywords) {
    if (lowerMsg.includes(keyword)) {
      return message;  // 返回完整消息作为 prompt
    }
  }

  return null;
}
```

**关键点**:
- 简单的按钮组件，用户主动触发
- 关键词检测决定是否显示
- 状态管理（loading/disabled）
- 移动端友好的设计

### 2. useResearchProgress Hook

**文件**: `hooks/use-research-progress.ts`

**职责**: 直接发起 POST SSE 连接，管理进度状态，处理重连

**架构变更**: 不再接受 taskId，改为接受 prompt 参数直接发起研究

**接口设计**:

```typescript
import { useState, useEffect } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';

type ProgressEvent = {
  type: 'start' | 'plan' | 'progress' | 'done' | 'error';
  data: any;
};

type ResearchStatus = 'idle' | 'running' | 'completed' | 'failed';

interface UseResearchProgressProps {
  prompt: string | null;
  onComplete?: (report: string) => void;
}

export function useResearchProgress({ prompt, onComplete }: UseResearchProgressProps) {
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [status, setStatus] = useState<ResearchStatus>('idle');
  const [report, setReport] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!prompt) return;

    let abortController = new AbortController();

    const startResearch = async () => {
      setStatus('running');

      try {
        await fetchEventSource('/api/research/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt }),
          signal: abortController.signal,

          onopen: async (response) => {
            if (response.ok) {
              console.log('SSE connected');
            } else {
              throw new Error(`SSE error: ${response.status}`);
            }
          },

          onmessage: (event) => {
            try {
              const data = JSON.parse(event.data);
              const progressEvent: ProgressEvent = {
                type: event.event as any,
                data,
              };

              setEvents(prev => [...prev, progressEvent]);

              switch (event.event) {
                case 'start':
                  setStatus('running');
                  break;
                case 'done':
                  setStatus('completed');
                  setReport(data.report);

                  // 调用回调函数，由父组件通过 sendMessage 发送给 AI
                  if (onComplete) {
                    onComplete(data.report);
                  }
                  break;
                case 'error':
                  setStatus('failed');
                  setError(data.message);
                  break;
              }
            } catch (err) {
              console.error('Failed to parse SSE event:', err);
            }
          },

          onerror: (err) => {
            console.error('SSE error:', err);
            setStatus('failed');
            setError('Connection failed');
            throw err;  // 让 fetch-event-source 处理重连
          },
        });
      } catch (err) {
        console.error('Research error:', err);
        setStatus('failed');
        setError('Research failed');
      }
    };

    startResearch();

    return () => {
      abortController.abort();
      setStatus('idle');
    };
  }, [prompt, onComplete]);

  return { events, status, report, error };
}
```

**关键点**:
- ⚠️ **不使用 `useUIState`**: 该应用使用 `useChat` Hook，不是 `useUIState`/`useActions` 模式
- ✅ **使用回调函数**: 通过 `onComplete` 回调将报告传递给父组件
- ✅ **父组件责任**: 父组件（Message/Chat）负责调用 `sendMessage` 发送报告给 AI
- 使用 fetch-event-source 支持 POST SSE
- 直接发起研究，无需 taskId
- 使用 AbortController 管理连接生命周期
- fetch-event-source 内置重连机制
- 状态管理清晰
- 组件卸载时清理

**集成示例** (在 Message 组件中):
```typescript
import { useChat } from 'ai/react';

const { sendMessage } = useChat();
const { events, status } = useResearchProgress({
  prompt: researchPrompt,
  onComplete: (report) => {
    // 使用 sendMessage 发送报告给 AI
    sendMessage({
      role: 'user',
      parts: [{ type: 'text', text: `Research completed:\n\n${report}` }]
    });
  }
});
```

### 3. API 代理路由

**文件**: `app/api/research/stream/route.ts`

**职责**: 代理 FastAPI 的 SSE 流，处理 CORS

**架构简化**: 仅需简单的 POST 代理，无需 GET 接口（fetch-event-source 支持 POST SSE）

**接口设计**:

```typescript
import { NextRequest } from 'next/server';

export const runtime = 'nodejs';  // 使用 Node.js runtime，不用 edge

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json();

    if (!prompt || prompt.length < 10) {
      return new Response(
        JSON.stringify({ error: 'Prompt must be at least 10 characters' }),
        { status: 400 }
      );
    }

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
        'Access-Control-Allow-Origin': '*',  // CORS
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
```

**关键点**:
- 仅支持 POST（符合 Phase 2 API）
- 简化实现，无需 GET 端点
- 参数验证（prompt 长度）
- 处理 CORS
- 错误处理
- 禁用 Nginx 缓冲

### 4. ResearchPanel 组件 ⭐ (新增)

**文件**: `components/research-panel.tsx`

**职责**: 统一管理 ResearchButton 和 ResearchProgress，提供 sticky 定位和动画

**接口设计**:

```typescript
'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { ResearchButton } from './research-button';
import { ResearchProgress } from './research-progress';

interface ResearchPanelProps {
  prompt: string;
  isActive: boolean;
  events: ProgressEvent[];
  status: ResearchStatus;
  onStart: (prompt: string) => void;
}

export function ResearchPanel({
  prompt,
  isActive,
  events,
  status,
  onStart
}: ResearchPanelProps) {
  return (
    <AnimatePresence>
      {(isActive || status !== 'idle') && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.2 }}
          className="sticky bottom-[72px] z-10 mx-4 mb-4"
        >
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 max-h-[400px] overflow-y-auto">
            {!isActive && (
              <ResearchButton
                prompt={prompt}
                onStart={onStart}
                disabled={status === 'running'}
              />
            )}
            {isActive && (
              <ResearchProgress events={events} status={status} />
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

**关键点**:
- 使用 sticky 定位在 bottom-[72px]（聊天输入框上方）
- 使用 Framer Motion 实现滑入/滑出动画
- 根据 isActive 状态切换显示 ResearchButton 或 ResearchProgress
- 统一样式（白色背景、圆角、阴影）
- 防止内容溢出（max-h-[400px] overflow-y-auto）

### 5. ResearchProgress 组件

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

**文件**: `app/(chat)/page.tsx` 和 `app/(chat)/api/chat/route.ts`

**职责**: 集成 ResearchButton，接收研究报告，调用 createDocument

**架构变更**:
- **旧流程**: AI 调用 startResearch 工具 → 返回 taskId → Hook 订阅
- **新流程**: 用户点击 ResearchButton → Hook 直接 SSE → AI 接收报告

**关键修改**:

**1. Chat 组件集成** (`components/chat.tsx`):

```typescript
'use client';

import { useChat } from 'ai/react';
import { ResearchButton } from '@/components/research-button';
import { useResearchProgress } from '@/hooks/use-research-progress';
import { ResearchProgress } from '@/components/research-progress';

export function Chat({ id, initialMessages }: { id: string; initialMessages: ChatMessage[] }) {
  const { messages, sendMessage, status } = useChat({ id, initialMessages });
  const [researchPrompt, setResearchPrompt] = useState<string | null>(null);
  const [showResearchUI, setShowResearchUI] = useState(false);

  // 检测最后一条 AI 消息是否包含研究关键词
  const lastAiMessage = useMemo(() => {
    return messages.filter(m => m.role === 'assistant').pop();
  }, [messages]);

  const shouldShowResearchButton = useMemo(() => {
    return lastAiMessage && detectResearchKeywords(lastAiMessage.content) && !researchPrompt;
  }, [lastAiMessage, researchPrompt]);

  const { events, status: researchStatus } = useResearchProgress({
    prompt: researchPrompt,
    onComplete: useCallback((report: string) => {
      // 使用 sendMessage 将报告发送给 AI
      sendMessage({
        role: 'user',
        parts: [{ type: 'text', text: `Research completed:\n\n${report}` }]
      });
      setResearchPrompt(null);
      setShowResearchUI(false);
    }, [sendMessage])
  });

  const handleStartResearch = (prompt: string) => {
    setResearchPrompt(prompt);
    setShowResearchUI(true);
  };

  return (
    <>
      <Messages messages={messages} ... />

      {/* ResearchPanel - sticky 定位在聊天输入框上方 */}
      {(shouldShowResearchButton || showResearchUI) && (
        <ResearchPanel
          prompt={extractResearchQuery(lastAiMessage?.content || '')}
          isActive={showResearchUI}
          events={events}
          status={researchStatus}
          onStart={handleStartResearch}
        />
      )}

      <MultimodalInput ... />
      <Artifact ... />
    </>
  );
}
```

**关键点**:
- ✅ 使用 `useChat` Hook 获取 `sendMessage` 函数
- ✅ 在 `onComplete` 回调中通过 `sendMessage` 发送报告
- ✅ ResearchPanel 集成在 Chat 组件中，使用 sticky 定位在聊天输入框上方
- ✅ 检测最后一条 AI 消息（而非用户消息）是否包含研究关键词
- ✅ 使用 ResearchPanel 统一管理 ResearchButton 和 ResearchProgress

**2. AI Chat Route** (`app/(chat)/api/chat/route.ts`):

```typescript
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

          // ❌ 不再需要 startResearch 工具
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

**架构变更**: AI 不再调用 startResearch，仅需处理接收到的研究报告

**新增研究提示**:

```typescript
export const systemPrompt = ({ selectedChatModel, requestHints }) => {
  const basePrompt = `You are a friendly AI research assistant.`;

  const researchPrompt = `
When you receive a research report (starting with "Research completed:"):
1. Parse the report content
2. Call createDocument to create an Artifact with the report
3. Provide a brief summary to the user
4. If users ask follow-up questions, call updateDocument to refine the report

Example flow:
[User clicks "Start Research" button in UI]
[System automatically sends you: "Research completed:\n\n<report content>"]
You: [Call createDocument({ title: "Research Report", kind: "text", content: report })]
You: "I've created a research report for you. The key findings are... What would you like to know more about?"

User: "Add more details about quantum entanglement"
You: [Call updateDocument({ documentId, description: "add more details about quantum entanglement" })]

Important:
- DO NOT try to research yourself
- DO NOT call any research-starting tools
- When you see "Research completed:", extract the report and call createDocument
- The research progress is shown automatically in the UI
- Focus on creating high-quality Artifacts from the reports
`;

  return `${basePrompt}\n\n${researchPrompt}\n\n${artifactsPrompt}`;
};
```

**关键点**:
- AI 通过 sendMessage 被动接收报告
- 不再需要主动调用工具启动研究
- 专注于 createDocument 和 updateDocument
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
// 确保只有一个 SSE 连接
useEffect(() => {
  // ...
  return () => {
    abortController.abort();  // 清理
  };
}, [prompt]);
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

### A. 事件流示例 (新架构)

```
用户: "研究量子计算"
  ↓
[前端检测关键词 "研究" → 显示 ResearchButton]
  ↓
用户: [点击 "Start Research" 按钮]
  ↓
[useResearchProgress Hook 发起 POST SSE 连接]
  ↓
[POST /api/research/stream, body: { prompt: "研究量子计算" }]
  ↓
接收 SSE 事件:
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
  ↓
[Hook 使用 sendMessage 发送报告给 AI]
  ↓
[系统消息: "Research completed:\n\n<report>"]
  ↓
AI: [调用 createDocument({ title: "量子计算研究", content: report })]
  ↓
AI: "研究完成！我已经创建了一份报告。主要发现包括..."
```

### B. 组件层次结构

```
App
├── Chat Page
│   ├── Chat Interface
│   │   ├── Message List
│   │   │   ├── User Message
│   │   │   ├── AI Message
│   │   │   ├── ResearchButton ← 新增（关键词检测后显示）
│   │   │   └── ResearchProgress ← 新增（显示进度）
│   │   └── Input Area
│   └── Artifact Display
│       └── Research Report ← 新增（AI 创建的 Artifact）
└── API Routes
    └── /api/research/stream ← 新增（POST 代理）
```

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待实施
