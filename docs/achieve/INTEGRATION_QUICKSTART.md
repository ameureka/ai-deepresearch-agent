# 🚀 项目整合快速实施指南

## 🎯 整合目标

将**研究报告生成系统**（Python/FastAPI）与 **AI Chatbot**（TypeScript/Next.js）整合，打造统一的 AI 研究助手平台。

---

## ⚡ 快速开始（30 分钟 POC）

### 步骤 1: 启动两个服务

#### 启动研究服务（FastAPI）
```bash
# 终端 1
cd /Users/ameureka/Desktop/agentic-ai-public-main
./start.sh
# 运行在 http://localhost:8000
```

#### 启动聊天服务（Next.js）
```bash
# 终端 2
cd /Users/ameureka/Desktop/agentic-ai-public-main/achive/ai-chatbot-main
pnpm install
pnpm dev
# 运行在 http://localhost:3000
```

### 步骤 2: 创建 API 桥接

在 Next.js 项目中创建研究 API 路由：

```bash
cd achive/ai-chatbot-main
mkdir -p app/api/research
```

创建文件 `app/api/research/route.ts`:

```typescript
// app/api/research/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/app/(auth)/auth';

export async function POST(request: NextRequest) {
  try {
    // 1. 验证用户身份
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // 2. 获取请求数据
    const { prompt } = await request.json();

    // 3. 调用 FastAPI 研究服务
    const response = await fetch('http://localhost:8000/generate_report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error('Research service error');
    }

    const data = await response.json();

    // 4. 返回结果
    return NextResponse.json({
      taskId: data.task_id,
      message: 'Research task started successfully',
    });
  } catch (error) {
    console.error('Research API error:', error);
    return NextResponse.json(
      { error: 'Failed to start research task' },
      { status: 500 }
    );
  }
}
```

创建进度查询路由 `app/api/research/[taskId]/route.ts`:

```typescript
// app/api/research/[taskId]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { taskId: string } }
) {
  try {
    const { taskId } = params;

    // 调用 FastAPI 进度端点
    const response = await fetch(
      `http://localhost:8000/task_progress/${taskId}`
    );

    if (!response.ok) {
      throw new Error('Failed to fetch progress');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Progress API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch progress' },
      { status: 500 }
    );
  }
}
```

### 步骤 3: 创建研究面板组件

创建文件 `components/research-panel.tsx`:

```typescript
// components/research-panel.tsx
'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';

interface Step {
  title: string;
  status: 'pending' | 'running' | 'done' | 'error';
  description: string;
}

export function ResearchPanel() {
  const [prompt, setPrompt] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const startResearch = async () => {
    if (!prompt.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      const data = await response.json();
      setTaskId(data.taskId);
    } catch (error) {
      console.error('Failed to start research:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 轮询进度
  useEffect(() => {
    if (!taskId) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/research/${taskId}`);
        const data = await response.json();
        setSteps(data.steps || []);

        // 检查是否完成
        const allDone = data.steps?.every(
          (s: Step) => s.status === 'done' || s.status === 'error'
        );
        if (allDone) {
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Failed to fetch progress:', error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId]);

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <h2 className="text-xl font-bold mb-4">AI 研究助手</h2>
        
        <Textarea
          placeholder="输入研究主题，例如：Large Language Models for scientific discovery"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={4}
          className="mb-4"
        />
        
        <Button
          onClick={startResearch}
          disabled={isLoading || !prompt.trim()}
          className="w-full"
        >
          {isLoading ? '启动中...' : '开始研究'}
        </Button>
      </Card>

      {steps.length > 0 && (
        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-4">研究进度</h3>
          <div className="space-y-2">
            {steps.map((step, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${
                  step.status === 'done'
                    ? 'bg-green-50 border-green-200'
                    : step.status === 'running'
                    ? 'bg-blue-50 border-blue-200'
                    : step.status === 'error'
                    ? 'bg-red-50 border-red-200'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">
                    {step.status === 'done' && '✅'}
                    {step.status === 'running' && '⏳'}
                    {step.status === 'error' && '❌'}
                    {step.status === 'pending' && '⏸️'}
                  </span>
                  <span className="text-sm font-medium">{step.title}</span>
                </div>
                {step.description && (
                  <p className="text-xs text-gray-600 mt-1">
                    {step.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
```

### 步骤 4: 添加到主页面

修改 `app/(chat)/page.tsx`:

```typescript
// app/(chat)/page.tsx
import { ResearchPanel } from '@/components/research-panel';
import { Chat } from '@/components/chat';

export default function Page() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">
      {/* 左侧：聊天界面 */}
      <div>
        <Chat />
      </div>
      
      {/* 右侧：研究面板 */}
      <div>
        <ResearchPanel />
      </div>
    </div>
  );
}
```

### 步骤 5: 测试整合

1. 确保两个服务都在运行
2. 访问 http://localhost:3000
3. 在研究面板输入主题
4. 点击"开始研究"
5. 观察实时进度更新

---

## 🎯 完整整合方案

### 方案架构

```
┌─────────────────────────────────────────────────────────┐
│              Next.js Frontend (Port 3000)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Chat UI     │  │ Research UI  │  │  Artifacts   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Next.js API Routes                          │
│  /api/chat          /api/research       /api/document    │
└─────────────────────────────────────────────────────────┘
         ↓                      ↓
┌──────────────────┐  ┌──────────────────┐
│  AI SDK          │  │  FastAPI         │
│  (聊天服务)       │  │  (研究服务)       │
│  Port 3000       │  │  Port 8000       │
└──────────────────┘  └──────────────────┘
         ↓                      ↓
┌─────────────────────────────────────────┐
│        PostgreSQL Database               │
│  • users                                 │
│  • chats                                 │
│  • messages                              │
│  • research_tasks                        │
│  • documents                             │
└─────────────────────────────────────────┘
```

---

## 📋 数据库整合

### 创建统一 Schema

```sql
-- 在 Next.js 项目中添加研究相关表

-- lib/db/schema.ts
import { pgTable, uuid, text, timestamp, varchar, json } from 'drizzle-orm/pg-core';

// 研究任务表
export const researchTask = pgTable('research_task', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').references(() => user.id),
  prompt: text('prompt').notNull(),
  status: varchar('status', { length: 20 }).notNull(),
  result: json('result'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
});

// 研究步骤表
export const researchStep = pgTable('research_step', {
  id: uuid('id').primaryKey().defaultRandom(),
  taskId: uuid('task_id').references(() => researchTask.id),
  title: text('title').notNull(),
  status: varchar('status', { length: 20 }).notNull(),
  description: text('description'),
  output: text('output'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});
```

### 运行迁移

```bash
cd achive/ai-chatbot-main
pnpm db:generate
pnpm db:migrate
```

---

## 🔧 高级功能

### 1. 将研究作为聊天工具

```typescript
// lib/ai/tools/start-research.ts
import { tool } from 'ai';
import { z } from 'zod';

export const startResearch = tool({
  description: 'Start a comprehensive research task using multi-agent workflow',
  inputSchema: z.object({
    topic: z.string().describe('Research topic or question'),
  }),
  execute: async ({ topic }) => {
    // 调用研究服务
    const response = await fetch('http://localhost:8000/generate_report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: topic }),
    });

    const data = await response.json();

    return {
      taskId: data.task_id,
      message: `Research task started. You can check progress at /research/${data.task_id}`,
    };
  },
});
```

### 2. 实时进度通知

```typescript
// 使用 Server-Sent Events (SSE)
export async function GET(
  request: NextRequest,
  { params }: { params: { taskId: string } }
) {
  const encoder = new TextEncoder();
  
  const stream = new ReadableStream({
    async start(controller) {
      const interval = setInterval(async () => {
        const response = await fetch(
          `http://localhost:8000/task_progress/${params.taskId}`
        );
        const data = await response.json();
        
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify(data)}\n\n`)
        );
        
        // 检查是否完成
        const allDone = data.steps?.every(
          (s: any) => s.status === 'done' || s.status === 'error'
        );
        if (allDone) {
          clearInterval(interval);
          controller.close();
        }
      }, 1000);
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

### 3. 研究结果作为 Artifact

```typescript
// 当研究完成时，创建 Artifact
const createArtifactFromResearch = async (taskId: string) => {
  // 获取研究结果
  const response = await fetch(`http://localhost:8000/task_status/${taskId}`);
  const data = await response.json();
  
  // 创建文档
  await saveDocument({
    title: `Research: ${data.prompt}`,
    content: data.result.html_report,
    kind: 'text',
    source: 'research',
    sourceId: taskId,
  });
};
```

---

## 🚀 部署方案

### Docker Compose 部署

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: local
      POSTGRES_DB: appdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # FastAPI 研究服务
  research-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://app:local@postgres:5432/appdb
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      TAVILY_API_KEY: ${TAVILY_API_KEY}
    depends_on:
      - postgres

  # Next.js 聊天服务
  chat-service:
    build: ./achive/ai-chatbot-main
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://app:local@postgres:5432/appdb
      AI_GATEWAY_API_KEY: ${AI_GATEWAY_API_KEY}
      RESEARCH_SERVICE_URL: http://research-service:8000
    depends_on:
      - postgres
      - research-service

volumes:
  postgres_data:
```

### 启动整合服务

```bash
docker-compose up -d
```

---

## ✅ 验证清单

### 基础功能
- [ ] FastAPI 服务正常运行
- [ ] Next.js 服务正常运行
- [ ] API 桥接工作正常
- [ ] 数据库连接成功

### 核心功能
- [ ] 可以启动研究任务
- [ ] 实时进度更新
- [ ] 研究结果正确显示
- [ ] 错误处理正常

### 高级功能
- [ ] 聊天中可以触发研究
- [ ] 研究结果作为 Artifact
- [ ] 用户认证集成
- [ ] 历史记录保存

---

## 📚 下一步

1. **完善 UI** - 优化研究面板设计
2. **添加功能** - 实现更多整合功能
3. **性能优化** - 缓存、并发处理
4. **测试** - 单元测试、集成测试
5. **文档** - 用户文档、API 文档
6. **部署** - 生产环境部署

---

## 💡 最佳实践

1. **错误处理** - 完善的错误提示和重试机制
2. **日志记录** - 详细的日志便于调试
3. **监控** - 服务健康检查和性能监控
4. **安全** - API 认证和数据验证
5. **文档** - 清晰的代码注释和文档

---

**创建日期**: 2025-01-XX  
**状态**: ✅ 已完成  
**预计实施时间**: 30 分钟（POC）- 10 周（完整版）
