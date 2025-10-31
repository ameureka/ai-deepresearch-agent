# Phase 3: Next.js 前端改造 - UI 设计详细报告

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 3 - Next.js 前端改造
- **版本**: 1.0
- **创建日期**: 2025-10-31
- **设计基准**: 现有 AI Chatbot UI (achive/ai-chatbot-main)
- **状态**: 待实施

---

## 目录

1. [设计概述](#设计概述)
2. [完整用户旅程](#完整用户旅程)
3. [组件层级架构](#组件层级架构)
4. [数据流设计](#数据流设计)
5. [详细 UI 设计](#详细-ui-设计)
6. [关键组件实现](#关键组件实现)
7. [样式设计规范](#样式设计规范)
8. [交互动画设计](#交互动画设计)
9. [响应式设计](#响应式设计)
10. [验收标准](#验收标准)

---

## 设计概述

### 核心设计原则

**1. 零侵入性**
- 不修改现有的 Messages/PreviewMessage/MessageActions 组件
- 在 Chat 组件级别添加研究功能
- 保持现有交互模式不变

**2. 视觉一致性**
- 遵循现有 UI 的设计语言
- 使用相同的颜色系统、字体、间距
- 匹配现有按钮和卡片样式

**3. 用户体验优先**
- 研究按钮自动检测并显示
- 实时进度反馈
- 无缝集成 Artifact 展示

**4. 性能优化**
- 使用 React.memo 避免不必要的重渲染
- SSE 连接生命周期清晰管理
- 状态更新节流处理

---

## 完整用户旅程

### 🎬 端到端用户流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     用户旅程时间线                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  T0: 用户打开应用                                                 │
│  │                                                                │
│  │  [初始界面]                                                    │
│  │  - Hello there! How can I help you today?                     │
│  │  - 建议问题卡片 x 4                                            │
│  │  - 输入框                                                      │
│  │                                                                │
│  ├─> T1: 用户输入研究问题 (0:00)                                  │
│  │   输入: "请帮我研究一下 React Server Components 的最佳实践"     │
│  │                                                                │
│  │  [用户消息显示]                                                │
│  │  - 蓝色气泡，右对齐                                            │
│  │  - [Copy] [Edit] 按钮（hover 显示）                           │
│  │                                                                │
│  ├─> T2: AI 理解并回复 (0:02)                                    │
│  │                                                                │
│  │  [AI 回复消息]                                                 │
│  │  - Sparkles 头像                                              │
│  │  - "我理解您想研究 React Server Components 的最佳实践。       │
│  │     点击下面的按钮开始深度研究，我将为您生成详细的报告。"       │
│  │  - [Copy] [👍] [👎] 操作按钮                                  │
│  │                                                                │
│  ├─> T3: ResearchButton 自动显示 (0:02)                          │
│  │                                                                │
│  │  [研究按钮出现] (在输入框上方，sticky 定位)                     │
│  │  ┌────────────────────────────────────────┐                   │
│  │  │  ✨ Start Research                     │                   │
│  │  └────────────────────────────────────────┘                   │
│  │  - 渐入动画 (fade in)                                          │
│  │  - 位置固定，不随滚动移动                                      │
│  │                                                                │
│  ├─> T4: 用户点击按钮 (0:05)                                     │
│  │                                                                │
│  │  [按钮状态变化]                                                │
│  │  ┌────────────────────────────────────────┐                   │
│  │  │  ⏳ Starting research...     [disabled] │                   │
│  │  └────────────────────────────────────────┘                   │
│  │  - 按钮 scale 动画                                             │
│  │  - 文本变为 "Starting research..."                            │
│  │  - 按钮禁用，防止重复点击                                      │
│  │                                                                │
│  ├─> T5: SSE 连接建立 (0:06)                                     │
│  │                                                                │
│  │  [进度组件显示]                                                │
│  │  ┌────────────────────────────────────────┐                   │
│  │  │  🔄 Connecting to research service...  │                   │
│  │  └────────────────────────────────────────┘                   │
│  │                                                                │
│  ├─> T6: 研究进行中 (0:08 - 2:00)                                │
│  │                                                                │
│  │  [实时进度更新]                                                │
│  │  ┌─────────────────────────────────────────┐                  │
│  │  │  📊 Research Progress                   │                  │
│  │  │  ━━━━━━━━━━━━━━━━━━━━ 35%              │                  │
│  │  │                                         │                  │
│  │  │  ✅ Planning research strategy          │                  │
│  │  │     → Identified 5 key areas            │                  │
│  │  │                                         │                  │
│  │  │  ✅ Searching React documentation       │                  │
│  │  │     → Found 12 relevant articles        │                  │
│  │  │                                         │                  │
│  │  │  🔄 Analyzing community best practices  │                  │
│  │  │     → Processing GitHub discussions     │                  │
│  │  │                                         │                  │
│  │  │  ⏳ Synthesizing findings...            │                  │
│  │  │                                         │                  │
│  │  │  ⏹️ Generating report...                │                  │
│  │  └─────────────────────────────────────────┘                  │
│  │  - 每个步骤实时更新                                            │
│  │  - 进度条平滑过渡                                              │
│  │  - 百分比动态显示                                              │
│  │                                                                │
│  ├─> T7: 研究完成 (2:00)                                         │
│  │                                                                │
│  │  [进度组件最终状态]                                            │
│  │  ┌─────────────────────────────────────────┐                  │
│  │  │  ✅ Research Complete                   │                  │
│  │  │  ━━━━━━━━━━━━━━━━━━━━ 100%             │                  │
│  │  │                                         │                  │
│  │  │  ✅ All steps completed                 │                  │
│  │  │  📄 Sending report to AI...             │                  │
│  │  └─────────────────────────────────────────┘                  │
│  │  - 完成动画 (check mark)                                       │
│  │  - 2 秒后自动消失                                              │
│  │                                                                │
│  ├─> T8: 自动发送报告给 AI (2:01)                                │
│  │                                                                │
│  │  [新消息出现]                                                  │
│  │  ┌────────────────────────────────────────┐                   │
│  │  │ 👤 User [Auto-sent]         2:01 PM    │                   │
│  │  │                                        │                   │
│  │  │ Research completed:                    │                   │
│  │  │                                        │                   │
│  │  │ [研究报告内容...]                       │                   │
│  │  └────────────────────────────────────────┘                   │
│  │  - 淡蓝色背景标识自动发送                                      │
│  │  - [Auto-sent] 标签                                           │
│  │                                                                │
│  ├─> T9: AI 处理报告 (2:02)                                      │
│  │                                                                │
│  │  [AI 思考中]                                                   │
│  │  - "Thinking..." 动画                                         │
│  │  - Sparkles 图标旋转                                          │
│  │                                                                │
│  ├─> T10: AI 创建 Artifact (2:05)                                │
│  │                                                                │
│  │  [AI 回复]                                                     │
│  │  "我已经为您创建了详细的研究报告，点击右侧查看完整内容。"       │
│  │  [Copy] [👍] [👎]                                             │
│  │                                                                │
│  │  [Artifact 全屏展示]                                           │
│  │  ┌──────────┬─────────────────────────────────┐              │
│  │  │ Chat     │ 📄 React Server Components      │              │
│  │  │ (400px)  │    Best Practices               │              │
│  │  │          │                         [× 关闭] │              │
│  │  │          ├─────────────────────────────────┤              │
│  │  │          │                                 │              │
│  │  │          │ # React Server Components...    │              │
│  │  │          │                                 │              │
│  │  │          │ ## 1. 核心概念                  │              │
│  │  │          │ ...                             │              │
│  │  │          │                                 │              │
│  │  │          │ [📋 Copy] [💾 Export]           │              │
│  │  └──────────┴─────────────────────────────────┘              │
│  │  - 滑入动画 (slide in from right)                             │
│  │  - 聊天区域压缩到 400px                                        │
│  │  - Artifact 占据剩余空间                                      │
│  │                                                                │
│  ├─> T11: 用户追问 (2:10)                                        │
│  │   输入: "能否补充一些实际的代码示例？"                          │
│  │                                                                │
│  │  [AI 更新 Artifact]                                           │
│  │  ┌──────────┬─────────────────────────────────┐              │
│  │  │          │ 📄 React Server Components      │              │
│  │  │          │    Best Practices [Updated]     │              │
│  │  │          │                                 │              │
│  │  │          │ ...                             │              │
│  │  │          │                                 │              │
│  │  │          │ ## 4. 实战案例 ⭐ NEW           │              │
│  │  │          │                                 │              │
│  │  │          │ ```typescript                   │              │
│  │  │          │ // Server Component             │              │
│  │  │          │ async function UserProfile...   │              │
│  │  │          │ ```                             │              │
│  │  └──────────┴─────────────────────────────────┘              │
│  │  - [Updated] 标签闪烁                                         │
│  │  - 新内容高亮显示 (2 秒)                                       │
│  │  - 滚动到新增内容位置                                          │
│  │                                                                │
│  └─> T12: 用户满意，关闭 Artifact (2:15)                        │
│                                                                   │
│      [Artifact 滑出]                                              │
│      - 滑出动画 (slide out to right)                              │
│      - 聊天区域恢复全宽                                            │
│      - 历史记录保持可访问                                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 组件层级架构

### 🏗️ 完整组件树

```
app/(chat)/[id]/page.tsx
│
└─> Chat 组件 (components/chat.tsx)
    │
    ├─> useChat Hook (AI SDK)
    │   ├── messages: ChatMessage[]
    │   ├── sendMessage: (msg) => void  ⭐ 关键 API
    │   ├── status: 'idle' | 'submitted' | 'streaming'
    │   └── regenerate, stop, resumeStream
    │
    ├─> 研究状态管理 (新增)
    │   ├── researchPrompt: string | null
    │   ├── showResearchUI: boolean
    │   ├── lastAiMessage: ChatMessage | undefined
    │   └── shouldShowResearchButton: boolean
    │
    ├─> useResearchProgress Hook (新增)
    │   ├── events: ProgressEvent[]
    │   ├── status: ResearchStatus
    │   ├── report: string | null
    │   └── error: string | null
    │
    ├─> 布局结构
    │   │
    │   ├─> ChatHeader
    │   │   └── 标题、模型选择、可见性设置
    │   │
    │   ├─> Messages 组件 (不修改)
    │   │   │
    │   │   └─> 消息容器 (可滚动区域)
    │   │       │
    │   │       ├─> Greeting (空状态)
    │   │       │
    │   │       └─> PreviewMessage (循环渲染)
    │   │           │
    │   │           ├─> 头像 (AI: Sparkles, User: none)
    │   │           │
    │   │           ├─> 消息内容
    │   │           │   ├── Text parts
    │   │           │   ├── Attachments
    │   │           │   ├── Tool results (weather, documents)
    │   │           │   └── Reasoning
    │   │           │
    │   │           └─> MessageActions
    │   │               ├── Copy
    │   │               ├── Edit (用户消息)
    │   │               ├── Upvote (AI 消息)
    │   │               └── Downvote (AI 消息)
    │   │
    │   ├─> ResearchPanel (新增，sticky 定位)
    │   │   │
    │   │   └─> 条件渲染
    │   │       │
    │   │       ├─> ResearchButton (研究未开始时)
    │   │       │   ├── Sparkles 图标
    │   │       │   ├── "Start Research" 文本
    │   │       │   └── onClick 处理
    │   │       │
    │   │       └─> ResearchProgress (研究进行中)
    │   │           ├── 标题栏
    │   │           ├── 进度条 (百分比)
    │   │           ├── 步骤列表
    │   │           │   ├── start 事件
    │   │           │   ├── plan 事件
    │   │           │   ├── progress 事件 (多个)
    │   │           │   ├── done 事件
    │   │           │   └── error 事件 (如有)
    │   │           └── 状态图标
    │   │
    │   └─> MultimodalInput (不修改)
    │       ├── 输入框
    │       ├── 附件按钮
    │       ├── 模型选择器
    │       └── 发送按钮
    │
    └─> Artifact 组件 (不修改)
        ├── 关闭按钮
        ├── 标题栏
        ├── 内容区域
        │   ├── TextArtifact
        │   ├── CodeArtifact
        │   ├── ImageArtifact
        │   └── SheetArtifact
        └── 操作栏
            ├── Copy
            ├── Export
            └── Regenerate
```

### 📦 新增组件详细说明

#### 1. ResearchPanel 组件 (新增)

**文件**: `components/research-panel.tsx`

**职责**:
- 统一管理 ResearchButton 和 ResearchProgress 的显示
- 处理布局和样式
- 提供一致的动画效果

**Props**:
```typescript
interface ResearchPanelProps {
  prompt: string;
  isActive: boolean;
  events: ProgressEvent[];
  status: ResearchStatus;
  onStart: (prompt: string) => void;
}
```

#### 2. ResearchButton 组件 (新增)

**文件**: `components/research-button.tsx`

**职责**:
- 显示研究按钮
- 处理点击事件
- 管理按钮状态 (idle/starting/disabled)

**Props**:
```typescript
interface ResearchButtonProps {
  prompt: string;
  onStart: (prompt: string) => void;
  disabled?: boolean;
}
```

#### 3. ResearchProgress 组件 (新增)

**文件**: `components/research-progress.tsx`

**职责**:
- 显示研究进度
- 渲染步骤列表
- 显示进度条和百分比

**Props**:
```typescript
interface ResearchProgressProps {
  events: ProgressEvent[];
  status: ResearchStatus;
}
```

#### 4. useResearchProgress Hook (新增)

**文件**: `hooks/use-research-progress.ts`

**职责**:
- 管理 SSE 连接
- 处理事件流
- 维护进度状态
- 触发完成回调

**签名**:
```typescript
function useResearchProgress(props: {
  prompt: string | null;
  onComplete?: (report: string) => void;
}): {
  events: ProgressEvent[];
  status: ResearchStatus;
  report: string | null;
  error: string | null;
}
```

---

## 数据流设计

### 🔄 完整数据流图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Phase 3 数据流                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐
│  用户    │       │  Chat    │       │  Hook    │       │  API     │
│  操作    │       │  组件    │       │          │       │  Route   │
└─────┬────┘       └────┬─────┘       └────┬─────┘       └────┬─────┘
      │                 │                  │                  │
      │ 1. 输入研究问题  │                  │                  │
      │────────────────>│                  │                  │
      │                 │                  │                  │
      │                 │ 2. sendMessage   │                  │
      │                 │─────────────────>│                  │
      │                 │                  │                  │
      │                 │                  │ 3. POST /api/chat│
      │                 │                  │─────────────────>│
      │                 │                  │                  │
      │                 │ 4. AI 回复流      │                  │
      │                 │<─────────────────│<─────────────────│
      │                 │                  │                  │
      │ 5. 显示 AI 消息  │                  │                  │
      │<────────────────│                  │                  │
      │                 │                  │                  │
      │                 │ 6. 检测关键词     │                  │
      │                 │    detectResearch │                  │
      │                 │    Keywords()    │                  │
      │                 │                  │                  │
      │ 7. 显示研究按钮  │                  │                  │
      │<────────────────│                  │                  │
      │                 │                  │                  │
      │ 8. 点击按钮      │                  │                  │
      │────────────────>│                  │                  │
      │                 │                  │                  │
      │                 │ 9. setResearch   │                  │
      │                 │    Prompt(prompt)│                  │
      │                 │                  │                  │
      │                 │                  │                  │
      │                 │                  │ 10. useEffect    │
      │                 │                  │     触发         │
      │                 │                  │                  │
      │                 │                  │ 11. fetchEvent   │
      │                 │                  │     Source       │
      │                 │                  │─────────────────>│
      │                 │                  │                  │
      │                 │                  │                  │ 12. Proxy
      │                 │                  │                  │───────>
      │                 │                  │                  │    FastAPI
      │                 │                  │                  │    Backend
      │                 │                  │                  │
      │                 │                  │ 13. SSE Stream   │
      │                 │                  │<─────────────────│
      │                 │                  │                  │
      │                 │ 14. events 更新   │                  │
      │                 │<─────────────────│                  │
      │                 │                  │                  │
      │ 15. 显示进度     │                  │                  │
      │<────────────────│                  │                  │
      │                 │                  │                  │
      │                 │                  │ 16. done event   │
      │                 │                  │<─────────────────│
      │                 │                  │                  │
      │                 │                  │ 17. onComplete() │
      │                 │                  │     callback     │
      │                 │                  │                  │
      │                 │ 18. sendMessage  │                  │
      │                 │     (report)     │                  │
      │                 │<─────────────────│                  │
      │                 │                  │                  │
      │                 │ 19. POST /api/chat (report)         │
      │                 │─────────────────────────────────────>│
      │                 │                  │                  │
      │                 │ 20. AI 处理报告   │                  │
      │                 │<─────────────────────────────────────│
      │                 │                  │                  │
      │                 │ 21. 调用         │                  │
      │                 │     createDocument│                  │
      │                 │     工具         │                  │
      │                 │                  │                  │
      │                 │ 22. DataStream   │                  │
      │                 │     data-* events│                  │
      │                 │<─────────────────────────────────────│
      │                 │                  │                  │
      │ 23. Artifact 显示│                  │                  │
      │<────────────────│                  │                  │
      │                 │                  │                  │
```

### 📊 状态管理流程

#### Chat 组件状态

```typescript
// components/chat.tsx

export function Chat({ ... }) {
  // ========== AI SDK 状态 ==========
  const {
    messages,        // ChatMessage[] - 所有消息
    sendMessage,     // (msg) => void - 发送消息给 AI
    status,          // 'idle' | 'submitted' | 'streaming'
    stop,            // () => void - 停止生成
    regenerate,      // () => void - 重新生成
    setMessages,     // (msgs) => void - 设置消息
  } = useChat({ ... });

  // ========== 研究状态 (新增) ==========
  const [researchPrompt, setResearchPrompt] = useState<string | null>(null);
  const [showResearchUI, setShowResearchUI] = useState(false);

  // ========== 派生状态 ==========
  const lastAiMessage = useMemo(() => {
    return messages
      .filter(m => m.role === 'assistant')
      .pop();
  }, [messages]);

  const shouldShowResearchButton = useMemo(() => {
    return lastAiMessage &&
           detectResearchKeywords(lastAiMessage.content) &&
           !researchPrompt;
  }, [lastAiMessage, researchPrompt]);

  // ========== 研究 Hook ==========
  const { events, status: researchStatus, report, error } = useResearchProgress({
    prompt: researchPrompt,
    onComplete: (report) => {
      // 发送报告给 AI
      sendMessage({
        role: 'user',
        parts: [{
          type: 'text',
          text: `Research completed:\n\n${report}`
        }]
      });

      // 清理状态
      setResearchPrompt(null);
      setShowResearchUI(false);
    }
  });

  // ========== 事件处理 ==========
  const handleStartResearch = useCallback((prompt: string) => {
    setResearchPrompt(prompt);
    setShowResearchUI(true);
  }, []);

  // ... 渲染逻辑
}
```

#### useResearchProgress Hook 状态

```typescript
// hooks/use-research-progress.ts

export function useResearchProgress({ prompt, onComplete }) {
  // ========== 状态定义 ==========
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [status, setStatus] = useState<ResearchStatus>('idle');
  const [report, setReport] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!prompt) return;

    // ========== 连接管理 ==========
    const abortController = new AbortController();

    const startResearch = async () => {
      setStatus('running');
      setEvents([]);
      setError(null);

      try {
        await fetchEventSource('/api/research/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt }),
          signal: abortController.signal,

          // ========== 事件处理 ==========
          onopen: async (response) => {
            if (response.ok) {
              console.log('SSE connected');
            } else {
              throw new Error(`SSE error: ${response.status}`);
            }
          },

          onmessage: (event) => {
            const data = JSON.parse(event.data);
            const progressEvent: ProgressEvent = {
              type: event.event,
              data,
            };

            // 添加事件到列表
            setEvents(prev => [...prev, progressEvent]);

            // 根据事件类型更新状态
            switch (event.event) {
              case 'start':
                setStatus('running');
                break;

              case 'done':
                setStatus('completed');
                setReport(data.report);

                // 触发完成回调
                if (onComplete) {
                  onComplete(data.report);
                }
                break;

              case 'error':
                setStatus('failed');
                setError(data.message);
                break;
            }
          },

          onerror: (err) => {
            console.error('SSE error:', err);
            setStatus('failed');
            setError('Connection failed');
            throw err;
          },
        });
      } catch (err) {
        console.error('Research error:', err);
        setStatus('failed');
        setError('Research failed');
      }
    };

    startResearch();

    // ========== 清理 ==========
    return () => {
      abortController.abort();
      setStatus('idle');
    };
  }, [prompt, onComplete]);

  return { events, status, report, error };
}
```

---

## 详细 UI 设计

### 🎨 各阶段 UI 详细设计

#### 阶段 1: 初始状态

```
┌─────────────────────────────────────────────────────────────────┐
│  AI Chatbot                                            [Account]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│                         Hello there!                              │
│                    How can I help you today?                      │
│                                                                   │
│  ┌────────────────────────────┐  ┌────────────────────────────┐ │
│  │ What are the advantages of │  │ Write code to demonstrate  │ │
│  │ using Next.js?             │  │ Dijkstra's algorithm       │ │
│  └────────────────────────────┘  └────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────┐  ┌────────────────────────────┐ │
│  │ Help me write an essay     │  │ What is the weather in     │ │
│  │ about Silicon Valley       │  │ San Francisco?             │ │
│  └────────────────────────────┘  └────────────────────────────┘ │
│                                                                   │
│                                                                   │
│                                                                   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Send a message...                                     [Send]││
│  │                                                              ││
│  │ [📎] [🎨 Model Selector ▼]                                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

CSS 类名:
- 容器: "flex h-dvh flex-col bg-background"
- 欢迎区: "flex-1 flex items-center justify-center"
- 标题: "text-2xl font-semibold"
- 副标题: "text-muted-foreground"
- 建议卡片: "rounded-lg border p-4 hover:bg-muted cursor-pointer"
- 输入区: "sticky bottom-0 border-t bg-background p-4"
```

#### 阶段 2: 用户输入 + AI 回复

```
┌─────────────────────────────────────────────────────────────────┐
│  AI Chatbot                                            [Account]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [消息历史区域 - 可滚动]                                          │
│                                                                   │
│                            研究一下 React Server Components      │
│                                          的最佳实践               │
│                                                     10:30 AM      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [🤖]                                            10:30 AM  │  │
│  │                                                           │  │
│  │ 我理解您想研究 React Server Components 的最佳实践。      │  │
│  │ 这是一个很好的话题！我可以为您启动一个深度研究，         │  │
│  │ 分析最新的文档、社区实践和实际案例，为您生成一份         │  │
│  │ 详细的研究报告。                                          │  │
│  │                                                           │  │
│  │ 点击下面的按钮开始研究：                                  │  │
│  │                                                           │  │
│  │ [📋 Copy] [👍 Upvote] [👎 Downvote]                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  [空白区域 - 用于滚动缓冲]                                        │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  [ResearchPanel 显示区域 - sticky bottom-[72px]]                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  ┌───────────────────────────────────────────────────────┐ ││
│  │  │  ✨ Start Research                                     │ ││
│  │  └───────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Send a message...                                     [Send]││
│  │ [📎] [🎨 Model Selector ▼]                                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

CSS 类名:
- 消息区: "flex-1 overflow-y-scroll"
- 用户消息: "ml-auto max-w-[80%] rounded-2xl bg-blue-500 text-white px-3 py-2"
- AI 消息容器: "flex gap-3 items-start"
- AI 头像: "size-8 rounded-full bg-background ring-1 ring-border"
- AI 消息内容: "flex-1 space-y-4"
- 操作按钮: "flex gap-2 -ml-0.5"
- ResearchPanel: "sticky bottom-[72px] z-10 mx-auto w-full max-w-4xl px-4"
- ResearchButton: "w-full rounded-lg border bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-3"
```

#### 阶段 3: 研究进行中

```
┌─────────────────────────────────────────────────────────────────┐
│  AI Chatbot                                            [Account]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [消息历史区域 - 可滚动]                                          │
│                                                                   │
│  [AI 消息 - "我理解您想研究..."]                                  │
│                                                                   │
│  [空白区域]                                                       │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  [ResearchProgress 显示区域 - sticky bottom-[72px]]              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  ┌───────────────────────────────────────────────────────┐ ││
│  │  │  ⏳ Research in progress...                [disabled] │ ││
│  │  └───────────────────────────────────────────────────────┘ ││
│  │                                                             ││
│  │  ┌───────────────────────────────────────────────────────┐ ││
│  │  │  📊 Research Progress                                 │ ││
│  │  │  ━━━━━━━━━━━━━━━━━━━━━━━ 60%                         │ ││
│  │  │                                                        │ ││
│  │  │  ✅ Planning research strategy                        │ ││
│  │  │     → Identified 5 key areas to investigate           │ ││
│  │  │                                                        │ ││
│  │  │  ✅ Searching React documentation                     │ ││
│  │  │     → Found 12 relevant articles                      │ ││
│  │  │                                                        │ ││
│  │  │  🔄 Analyzing community best practices                │ ││
│  │  │     → Processing GitHub discussions                   │ ││
│  │  │                                                        │ ││
│  │  │  ⏳ Synthesizing findings...                          │ ││
│  │  │                                                        │ ││
│  │  │  ⏹️ Generating comprehensive report                   │ ││
│  │  └───────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Send a message...                                     [Send]││
│  │ [📎] [🎨 Model Selector ▼]                                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

CSS 类名:
- ResearchProgress 容器: "rounded-lg border bg-white dark:bg-gray-800 p-4 shadow-sm"
- 标题行: "flex items-center gap-2 mb-3"
- 加载图标: "w-5 h-5 animate-spin text-blue-500"
- 进度条容器: "w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-4"
- 进度条填充: "h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-300"
- 步骤列表: "space-y-2"
- 步骤项: "flex items-start gap-2 text-sm"
- 完成步骤: "text-green-600 dark:text-green-400"
- 进行中步骤: "text-blue-600 dark:text-blue-400"
- 待处理步骤: "text-gray-500 dark:text-gray-400"
```

#### 阶段 4: 研究完成

```
┌─────────────────────────────────────────────────────────────────┐
│  AI Chatbot                                            [Account]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [消息历史区域 - 可滚动]                                          │
│                                                                   │
│  [AI 消息 - "我理解您想研究..."]                                  │
│                                                                   │
│  [空白区域]                                                       │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  [完成状态显示 - 2 秒后消失]                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  ┌───────────────────────────────────────────────────────┐ ││
│  │  │  ✅ Research Complete!                                │ ││
│  │  └───────────────────────────────────────────────────────┘ ││
│  │                                                             ││
│  │  ┌───────────────────────────────────────────────────────┐ ││
│  │  │  ✅ All steps completed                               │ ││
│  │  │  ━━━━━━━━━━━━━━━━━━━━━━━ 100%                        │ ││
│  │  │                                                        │ ││
│  │  │  📄 Sending report to AI...                           │ ││
│  │  └───────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Send a message...                                     [Send]││
│  │ [📎] [🎨 Model Selector ▼]                                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

动画:
- ResearchProgress 淡出 (fade-out, 2 秒)
- 成功图标脉冲动画 (pulse)
- 进度条填充到 100% (smooth transition)
```

#### 阶段 5: 自动发送报告

```
┌─────────────────────────────────────────────────────────────────┐
│  AI Chatbot                                            [Account]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [消息历史区域 - 可滚动]                                          │
│                                                                   │
│  [AI 消息 - "我理解您想研究..."]                                  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Research completed:                    │  │
│  │                                                           │  │
│  │ # React Server Components 最佳实践研究报告               │  │
│  │                                                           │  │
│  │ ## 执行摘要                                               │  │
│  │                                                           │  │
│  │ React Server Components (RSC) 是 React 18 引入的...      │  │
│  │                                                           │  │
│  │ ## 核心概念                                               │  │
│  │                                                           │  │
│  │ 1. **服务端渲染优势**                                     │  │
│  │    - 减少客户端 JavaScript 包大小                         │  │
│  │    - 直接访问后端资源（数据库、文件系统）                 │  │
│  │    - 提升首屏加载性能                                     │  │
│  │                                                           │  │
│  │ [... 更多内容 ...]                                        │  │
│  │                                                           │  │
│  │                                           [Auto-sent] 2:01PM │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [🤖] Thinking...                                10:32 AM  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Send a message...                                     [Send]││
│  │ [📎] [🎨 Model Selector ▼]                                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

CSS 类名:
- 自动发送消息: "rounded-2xl bg-blue-500/10 border border-blue-500/20 px-3 py-2"
- Auto-sent 标签: "text-xs text-blue-600 dark:text-blue-400 font-medium"
- Thinking 消息: "text-sm text-muted-foreground animate-pulse"
```

#### 阶段 6: Artifact 展示

```
┌──────────────────┬──────────────────────────────────────────────┐
│  Chatbot         │  📄 React Server Components Best Practices   │
│  [🗑️] [+]        │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  [▭] [🔒]        │                                    [× Close] │
│                  ├──────────────────────────────────────────────┤
│ Conversations    │                                              │
│  → Chat 3        │  # React Server Components 最佳实践          │
│  - Chat 1        │                                              │
│  - Chat 2        │  > 研究完成于: 2025-10-31 14:32              │
│                  │  > 数据来源: React 官方文档、GitHub、Stack... │
│ [👤 Guest ˅]     │                                              │
│                  │  ## 1. 核心概念                              │
│                  │                                              │
│                  │  React Server Components (RSC) 是一种新的... │
│                  │                                              │
│                  │  ### 1.1 服务端渲染优势                      │
│                  │                                              │
│                  │  - **性能提升**: 减少客户端 JavaScript 体积  │
│                  │  - **数据访问**: 直接访问后端资源            │
│                  │  - **SEO 优化**: 完整的 HTML 内容            │
│                  │                                              │
│                  │  ## 2. 使用场景                              │
│                  │                                              │
│                  │  ### 2.1 何时使用 Server Components         │
│                  │                                              │
│                  │  ```typescript                              │
│                  │  // ✅ 适合 Server Component                │
│                  │  async function UserProfile({ userId }) {   │
│                  │    const user = await db.user.findUnique({  │
│                  │      where: { id: userId }                  │
│                  │    });                                      │
│                  │    return <div>{user.name}</div>;           │
│                  │  }                                          │
│                  │  ```                                        │
│                  │                                              │
│                  │  [... 滚动查看更多内容 ...]                  │
│                  │                                              │
│                  │  ┌─────────────────────────────────────┐    │
│                  │  │  📋 Copy  💾 Export  🔄 Regenerate  │    │
│                  │  └─────────────────────────────────────┘    │
└──────────────────┴──────────────────────────────────────────────┘

CSS 类名:
- 布局容器: "flex h-screen"
- 左侧边栏: "w-[400px] border-r"
- Artifact 区域: "flex-1 overflow-hidden"
- Artifact 头部: "border-b px-4 py-3 flex items-center justify-between"
- Artifact 内容: "h-[calc(100%-120px)] overflow-y-auto px-8 py-6 prose prose-sm"
- 操作栏: "border-t px-4 py-3 flex gap-2"

动画:
- Artifact 滑入: "animate-in slide-in-from-right duration-300"
- 内容淡入: "animate-in fade-in duration-500"
- 聊天区域压缩: "transition-all duration-300"
```

---

## 关键组件实现

### 📄 完整代码实现

#### 1. Chat 组件修改 (components/chat.tsx)

```typescript
"use client";

import { useChat } from "@ai-sdk/react";
import { useEffect, useMemo, useState, useCallback } from "react";
import { ChatHeader } from "@/components/chat-header";
import { Messages } from "@/components/messages";
import { MultimodalInput } from "@/components/multimodal-input";
import { Artifact } from "./artifact";
import { ResearchPanel } from "./research-panel"; // ⭐ 新增
import { useResearchProgress } from "@/hooks/use-research-progress"; // ⭐ 新增
import { detectResearchKeywords, extractResearchQuery } from "@/lib/research-utils"; // ⭐ 新增

export function Chat({
  id,
  initialMessages,
  initialChatModel,
  initialVisibilityType,
  isReadonly,
  autoResume,
  initialLastContext,
}) {
  // ========== 现有代码 ==========
  const {
    messages,
    setMessages,
    sendMessage, // ⭐ 关键：用于发送研究报告
    status,
    stop,
    regenerate,
    resumeStream,
  } = useChat({
    id,
    messages: initialMessages,
    // ... 现有配置
  });

  // ========== 新增：研究状态管理 ==========
  const [researchPrompt, setResearchPrompt] = useState<string | null>(null);
  const [showResearchUI, setShowResearchUI] = useState(false);

  // 检测最后一条 AI 消息是否需要显示研究按钮
  const lastAiMessage = useMemo(() => {
    return messages
      .filter(m => m.role === 'assistant')
      .pop();
  }, [messages]);

  const shouldShowResearchButton = useMemo(() => {
    return (
      lastAiMessage &&
      detectResearchKeywords(lastAiMessage.content) &&
      !researchPrompt && // 未开始研究时显示
      !showResearchUI   // 研究 UI 未显示时显示
    );
  }, [lastAiMessage, researchPrompt, showResearchUI]);

  // ========== 新增：研究 Hook ==========
  const { events, status: researchStatus, report, error } = useResearchProgress({
    prompt: researchPrompt,
    onComplete: useCallback((report: string) => {
      console.log('Research completed, sending to AI:', report.substring(0, 100));

      // ⭐ 关键：使用 sendMessage 发送报告给 AI
      sendMessage({
        role: 'user',
        parts: [{
          type: 'text',
          text: `Research completed:\n\n${report}`
        }]
      });

      // 清理状态
      setResearchPrompt(null);
      setShowResearchUI(false);
    }, [sendMessage])
  });

  // ========== 事件处理 ==========
  const handleStartResearch = useCallback((prompt: string) => {
    console.log('Starting research with prompt:', prompt);
    setResearchPrompt(prompt);
    setShowResearchUI(true);
  }, []);

  // ========== 渲染 ==========
  return (
    <>
      <div className="overscroll-behavior-contain flex h-dvh min-w-0 touch-pan-y flex-col bg-background">
        <ChatHeader
          chatId={id}
          isReadonly={isReadonly}
          selectedVisibilityType={initialVisibilityType}
        />

        {/* ========== 消息列表 (不修改) ========== */}
        <Messages
          chatId={id}
          isArtifactVisible={isArtifactVisible}
          isReadonly={isReadonly}
          messages={messages}
          regenerate={regenerate}
          selectedModelId={initialChatModel}
          setMessages={setMessages}
          status={status}
          votes={votes}
        />

        {/* ========== 新增：研究面板 (sticky 定位) ========== */}
        {(shouldShowResearchButton || showResearchUI) && (
          <ResearchPanel
            prompt={extractResearchQuery(lastAiMessage?.content || '')}
            isActive={showResearchUI}
            events={events}
            status={researchStatus}
            onStart={handleStartResearch}
          />
        )}

        {/* ========== 输入框 (不修改) ========== */}
        <div className="sticky bottom-0 z-1 mx-auto flex w-full max-w-4xl gap-2 border-t-0 bg-background px-2 pb-3 md:px-4 md:pb-4">
          {!isReadonly && (
            <MultimodalInput
              attachments={attachments}
              chatId={id}
              input={input}
              messages={messages}
              onModelChange={setCurrentModelId}
              selectedModelId={currentModelId}
              selectedVisibilityType={visibilityType}
              sendMessage={sendMessage}
              setAttachments={setAttachments}
              setInput={setInput}
              setMessages={setMessages}
              status={status}
              stop={stop}
              usage={usage}
            />
          )}
        </div>
      </div>

      {/* ========== Artifact (不修改) ========== */}
      <Artifact
        attachments={attachments}
        chatId={id}
        input={input}
        isReadonly={isReadonly}
        messages={messages}
        regenerate={regenerate}
        selectedModelId={currentModelId}
        selectedVisibilityType={visibilityType}
        sendMessage={sendMessage}
        setAttachments={setAttachments}
        setInput={setInput}
        setMessages={setMessages}
        status={status}
        stop={stop}
        votes={votes}
      />
    </>
  );
}
```

#### 2. ResearchPanel 组件 (components/research-panel.tsx)

```typescript
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ResearchButton } from "./research-button";
import { ResearchProgress } from "./research-progress";
import type { ProgressEvent, ResearchStatus } from "@/lib/types";

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
  onStart,
}: ResearchPanelProps) {
  return (
    <div className="sticky bottom-[72px] z-10 mx-auto w-full max-w-4xl px-2 md:px-4">
      <AnimatePresence mode="wait">
        {!isActive && (
          <motion.div
            key="button"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="rounded-lg border bg-background p-4 shadow-lg">
              <ResearchButton
                prompt={prompt}
                onStart={onStart}
                disabled={status === 'running'}
              />
            </div>
          </motion.div>
        )}

        {isActive && (
          <motion.div
            key="progress"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="rounded-lg border bg-background p-4 shadow-lg">
              <ResearchProgress events={events} status={status} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
```

#### 3. ResearchButton 组件 (components/research-button.tsx)

```typescript
"use client";

import { useState } from "react";
import { Sparkles } from "lucide-react";
import { Button } from "./ui/button";

interface ResearchButtonProps {
  prompt: string;
  onStart: (prompt: string) => void;
  disabled?: boolean;
}

export function ResearchButton({ prompt, onStart, disabled }: ResearchButtonProps) {
  const [isStarting, setIsStarting] = useState(false);

  const handleClick = async () => {
    setIsStarting(true);
    try {
      await onStart(prompt);
    } finally {
      // 保持 starting 状态，直到研究 Hook 接管
      setTimeout(() => setIsStarting(false), 300);
    }
  };

  return (
    <Button
      onClick={handleClick}
      disabled={disabled || isStarting}
      className="w-full gap-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all duration-200"
      size="lg"
    >
      <Sparkles className={`h-5 w-5 ${isStarting ? 'animate-pulse' : ''}`} />
      {isStarting ? 'Starting research...' : 'Start Research'}
    </Button>
  );
}
```

#### 4. ResearchProgress 组件 (components/research-progress.tsx)

```typescript
"use client";

import { useMemo } from "react";
import { Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";
import type { ProgressEvent, ResearchStatus } from "@/lib/types";

interface ResearchProgressProps {
  events: ProgressEvent[];
  status: ResearchStatus;
}

export function ResearchProgress({ events, status }: ResearchProgressProps) {
  // 计算进度百分比
  const percentage = useMemo(() => {
    if (status === 'completed') return 100;
    if (status === 'failed') return 0;
    if (events.length === 0) return 0;

    // 根据事件类型计算进度
    const weights = {
      start: 10,
      plan: 20,
      progress: 10,
      done: 100,
    };

    const total = events.reduce((sum, event) => {
      return sum + (weights[event.type] || 0);
    }, 0);

    return Math.min(Math.round(total), 95); // 最高 95%，完成后才到 100%
  }, [events, status]);

  // 获取状态图标
  const StatusIcon = useMemo(() => {
    switch (status) {
      case 'completed':
        return CheckCircle2;
      case 'failed':
        return XCircle;
      case 'running':
        return Loader2;
      default:
        return Clock;
    }
  }, [status]);

  return (
    <div className="space-y-4">
      {/* 标题栏 */}
      <div className="flex items-center gap-2">
        <StatusIcon
          className={`h-5 w-5 ${
            status === 'running' ? 'animate-spin text-blue-500' :
            status === 'completed' ? 'text-green-500' :
            status === 'failed' ? 'text-red-500' :
            'text-gray-500'
          }`}
        />
        <span className="font-medium">
          {status === 'completed' ? 'Research Complete' :
           status === 'failed' ? 'Research Failed' :
           status === 'running' ? 'Research in Progress' :
           'Research Starting'}
        </span>
        <span className="ml-auto text-sm text-muted-foreground">
          {percentage}%
        </span>
      </div>

      {/* 进度条 */}
      <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ease-out ${
            status === 'completed' ? 'bg-green-500' :
            status === 'failed' ? 'bg-red-500' :
            'bg-gradient-to-r from-blue-500 to-purple-600'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* 步骤列表 */}
      <div className="space-y-2 max-h-[200px] overflow-y-auto">
        {events.map((event, index) => (
          <EventItem key={index} event={event} />
        ))}
      </div>

      {/* 完成消息 */}
      {status === 'completed' && (
        <div className="text-sm text-green-600 dark:text-green-400 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4" />
          All steps completed. Sending report to AI...
        </div>
      )}

      {/* 错误消息 */}
      {status === 'failed' && (
        <div className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
          <XCircle className="h-4 w-4" />
          Research failed. Please try again.
        </div>
      )}
    </div>
  );
}

function EventItem({ event }: { event: ProgressEvent }) {
  const icon = useMemo(() => {
    switch (event.type) {
      case 'start':
        return '🚀';
      case 'plan':
        return '📋';
      case 'progress':
        return '🔄';
      case 'done':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '•';
    }
  }, [event.type]);

  return (
    <div className="flex items-start gap-2 text-sm">
      <span className="mt-0.5">{icon}</span>
      <div className="flex-1">
        <div className="font-medium">{event.data.message || event.data.step}</div>
        {event.data.detail && (
          <div className="text-muted-foreground text-xs mt-0.5">
            → {event.data.detail}
          </div>
        )}
      </div>
    </div>
  );
}
```

#### 5. useResearchProgress Hook (hooks/use-research-progress.ts)

```typescript
"use client";

import { useState, useEffect } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import type { ProgressEvent, ResearchStatus } from "@/lib/types";

interface UseResearchProgressProps {
  prompt: string | null;
  onComplete?: (report: string) => void;
}

export function useResearchProgress({
  prompt,
  onComplete
}: UseResearchProgressProps) {
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [status, setStatus] = useState<ResearchStatus>('idle');
  const [report, setReport] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!prompt) {
      setStatus('idle');
      setEvents([]);
      setReport(null);
      setError(null);
      return;
    }

    const abortController = new AbortController();

    const startResearch = async () => {
      setStatus('running');
      setEvents([]);
      setError(null);

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
              console.log('SSE connection established');
            } else {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
          },

          onmessage: (event) => {
            try {
              const data = JSON.parse(event.data);
              const progressEvent: ProgressEvent = {
                type: event.event as any,
                data,
              };

              console.log('SSE event received:', progressEvent);

              // 添加事件到列表
              setEvents(prev => [...prev, progressEvent]);

              // 根据事件类型更新状态
              switch (event.event) {
                case 'start':
                  setStatus('running');
                  break;

                case 'done':
                  setStatus('completed');
                  setReport(data.report);

                  console.log('Research completed, calling onComplete');

                  // 触发完成回调
                  if (onComplete) {
                    onComplete(data.report);
                  }
                  break;

                case 'error':
                  setStatus('failed');
                  setError(data.message || 'Research failed');
                  break;
              }
            } catch (err) {
              console.error('Failed to parse SSE event:', err);
            }
          },

          onerror: (err) => {
            console.error('SSE connection error:', err);
            setStatus('failed');
            setError('Connection failed');

            // 让 fetch-event-source 处理重连
            throw err;
          },

          // 重连配置 (fetch-event-source 内置)
          openWhenHidden: true,
        });
      } catch (err) {
        console.error('Research error:', err);
        setStatus('failed');
        setError(err instanceof Error ? err.message : 'Research failed');
      }
    };

    startResearch();

    // 清理函数
    return () => {
      console.log('Cleaning up research connection');
      abortController.abort();
    };
  }, [prompt, onComplete]);

  return { events, status, report, error };
}
```

#### 6. 工具函数 (lib/research-utils.ts)

```typescript
/**
 * 检测消息内容是否包含研究关键词
 */
export function detectResearchKeywords(content: string): boolean {
  if (!content) return false;

  const keywords = [
    // 英文关键词
    'research',
    'investigate',
    'study',
    'analyze',
    'analysis',
    'explore',
    'examine',
    'survey',
    'review',

    // 中文关键词
    '研究',
    '调查',
    '分析',
    '探索',
    '考察',
    '审查',
    '综述',
    '调研',
  ];

  const lowerContent = content.toLowerCase();

  return keywords.some(keyword =>
    lowerContent.includes(keyword.toLowerCase())
  );
}

/**
 * 从消息内容中提取研究问题
 */
export function extractResearchQuery(content: string): string {
  if (!content) return '';

  // 移除常见的礼貌用语和连接词
  const cleaned = content
    .replace(/^(please|can you|could you|would you|help me|i want to|i need to)/gi, '')
    .replace(/^(请|能否|可以|帮我|我想|我需要)/g, '')
    .trim();

  // 如果清理后太短，返回原内容
  if (cleaned.length < 10) {
    return content;
  }

  return cleaned;
}

/**
 * 格式化研究报告用于发送给 AI
 */
export function formatResearchReport(report: string): string {
  return `Research completed:\n\n${report}`;
}
```

#### 7. API 路由 (app/api/research/stream/route.ts)

```typescript
import { NextRequest } from 'next/server';

export const runtime = 'nodejs';

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json();

    // 验证输入
    if (!prompt || typeof prompt !== 'string') {
      return new Response(
        JSON.stringify({ error: 'Prompt is required' }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    if (prompt.length < 10) {
      return new Response(
        JSON.stringify({ error: 'Prompt must be at least 10 characters' }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // 获取后端 URL
    const backendUrl = process.env.RESEARCH_API_URL;
    if (!backendUrl) {
      return new Response(
        JSON.stringify({ error: 'Research API not configured' }),
        {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // 代理请求到 FastAPI 后端
    const response = await fetch(`${backendUrl}/api/research/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    // 返回 SSE 流
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (error) {
    console.error('Research API error:', error);
    return new Response(
      JSON.stringify({
        error: 'Failed to start research',
        details: error instanceof Error ? error.message : 'Unknown error'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// 处理 OPTIONS 请求（CORS）
export async function OPTIONS() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
```

#### 8. 类型定义 (lib/types.ts)

```typescript
// 新增类型定义

export type ProgressEvent = {
  type: 'start' | 'plan' | 'progress' | 'done' | 'error';
  data: {
    message?: string;
    step?: string;
    detail?: string;
    report?: string;
    error?: string;
    [key: string]: any;
  };
};

export type ResearchStatus = 'idle' | 'running' | 'completed' | 'failed';

// 现有类型保持不变
export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  parts: MessagePart[];
  createdAt?: Date;
};

// ... 其他现有类型
```

---

## 样式设计规范

### 🎨 设计 Token

#### 颜色系统

```css
/* 主题颜色 */
--primary: #006cff;          /* 用户消息背景 */
--primary-hover: #0052cc;    /* 按钮 hover */
--secondary: #6366f1;        /* 研究按钮渐变起始 */
--secondary-end: #8b5cf6;    /* 研究按钮渐变结束 */

/* 状态颜色 */
--success: #10b981;          /* 成功/完成 */
--error: #ef4444;            /* 错误/失败 */
--warning: #f59e0b;          /* 警告 */
--info: #3b82f6;             /* 信息/进行中 */

/* 背景颜色 */
--background: #ffffff;       /* 主背景 */
--surface: #f9fafb;          /* 卡片背景 */
--border: #e5e7eb;           /* 边框 */

/* 深色模式 */
@media (prefers-color-scheme: dark) {
  --background: #111827;
  --surface: #1f2937;
  --border: #374151;
}

/* 文本颜色 */
--text-primary: #111827;
--text-secondary: #6b7280;
--text-muted: #9ca3af;

@media (prefers-color-scheme: dark) {
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --text-muted: #9ca3af;
}
```

#### 间距系统

```css
/* Tailwind 间距 */
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-5: 1.25rem;  /* 20px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */

/* 组件间距 */
--message-gap: 1rem;           /* 消息之间 */
--component-padding: 1rem;     /* 组件内边距 */
--section-gap: 1.5rem;         /* 区域间距 */
```

#### 圆角和阴影

```css
/* 圆角 */
--radius-sm: 0.375rem;  /* 6px - 小按钮 */
--radius-md: 0.5rem;    /* 8px - 卡片 */
--radius-lg: 0.75rem;   /* 12px - 大卡片 */
--radius-xl: 1rem;      /* 16px - 消息气泡 */
--radius-full: 9999px;  /* 圆形 */

/* 阴影 */
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
```

### 📱 组件样式

#### ResearchButton

```css
.research-button {
  /* 布局 */
  width: 100%;
  padding: 0.75rem 1rem;

  /* 外观 */
  background: linear-gradient(to right, #3b82f6, #8b5cf6);
  color: white;
  border-radius: 0.5rem;
  border: none;

  /* 文字 */
  font-weight: 500;
  font-size: 0.875rem;

  /* 交互 */
  cursor: pointer;
  transition: all 0.2s ease;

  /* 图标 */
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.research-button:hover:not(:disabled) {
  background: linear-gradient(to right, #2563eb, #7c3aed);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.research-button:active:not(:disabled) {
  transform: translateY(0);
}

.research-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

#### ResearchProgress

```css
.research-progress {
  /* 布局 */
  padding: 1rem;

  /* 外观 */
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}

.progress-bar {
  /* 容器 */
  width: 100%;
  height: 0.5rem;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  /* 填充 */
  height: 100%;
  background: linear-gradient(to right, #3b82f6, #8b5cf6);
  transition: width 0.5s ease-out;
}

.progress-step {
  /* 步骤项 */
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.875rem;
  padding: 0.25rem 0;
}

.progress-step.completed {
  color: #10b981;
}

.progress-step.running {
  color: #3b82f6;
}

.progress-step.pending {
  color: #6b7280;
}
```

#### ResearchPanel (Sticky)

```css
.research-panel {
  /* 定位 */
  position: sticky;
  bottom: 72px;  /* 输入框高度 */
  z-index: 10;

  /* 布局 */
  margin: 0 auto;
  width: 100%;
  max-width: 56rem;  /* 896px - 与消息区域对齐 */
  padding: 0 0.5rem;
}

@media (min-width: 768px) {
  .research-panel {
    padding: 0 1rem;
  }
}

.research-panel-card {
  /* 外观 */
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

@media (prefers-color-scheme: dark) {
  .research-panel-card {
    background: #1f2937;
    border-color: #374151;
  }
}
```

---

## 交互动画设计

### 🎬 动画时序

#### 1. ResearchButton 出现动画

```typescript
// Framer Motion 配置
const buttonVariants = {
  hidden: {
    opacity: 0,
    y: 20,
    scale: 0.95
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.3,
      ease: "easeOut"
    }
  },
  exit: {
    opacity: 0,
    y: -20,
    scale: 0.95,
    transition: {
      duration: 0.2
    }
  }
};

<motion.div
  variants={buttonVariants}
  initial="hidden"
  animate="visible"
  exit="exit"
>
  <ResearchButton />
</motion.div>
```

#### 2. 按钮点击动画

```typescript
const clickAnimation = {
  scale: [1, 0.95, 1],
  transition: {
    duration: 0.2,
    times: [0, 0.5, 1]
  }
};

<motion.button
  whileTap={clickAnimation}
  whileHover={{ scale: 1.02 }}
>
  Start Research
</motion.button>
```

#### 3. ResearchProgress 切换动画

```typescript
const progressVariants = {
  hidden: {
    opacity: 0,
    y: 20,
    height: 0
  },
  visible: {
    opacity: 1,
    y: 0,
    height: "auto",
    transition: {
      duration: 0.3,
      ease: "easeOut"
    }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: {
      duration: 0.5,
      ease: "easeIn"
    }
  }
};

<AnimatePresence mode="wait">
  {showProgress && (
    <motion.div
      variants={progressVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
    >
      <ResearchProgress />
    </motion.div>
  )}
</AnimatePresence>
```

#### 4. 进度条填充动画

```css
.progress-fill {
  transition: width 0.5s cubic-bezier(0.4, 0.0, 0.2, 1);
}

/* 成功完成动画 */
@keyframes success-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.progress-fill.completed {
  animation: success-pulse 1s ease-in-out;
}
```

#### 5. 步骤项出现动画

```typescript
const stepVariants = {
  hidden: {
    opacity: 0,
    x: -20
  },
  visible: (index: number) => ({
    opacity: 1,
    x: 0,
    transition: {
      delay: index * 0.1,
      duration: 0.3
    }
  })
};

{events.map((event, index) => (
  <motion.div
    key={index}
    custom={index}
    variants={stepVariants}
    initial="hidden"
    animate="visible"
  >
    <EventItem event={event} />
  </motion.div>
))}
```

#### 6. Artifact 展开动画

```typescript
const artifactVariants = {
  hidden: {
    x: "100%",
    opacity: 0
  },
  visible: {
    x: 0,
    opacity: 1,
    transition: {
      duration: 0.4,
      ease: "easeOut"
    }
  },
  exit: {
    x: "100%",
    opacity: 0,
    transition: {
      duration: 0.3,
      ease: "easeIn"
    }
  }
};

// 同时聊天区域压缩动画
const chatVariants = {
  full: {
    width: "100%",
    transition: { duration: 0.4 }
  },
  compressed: {
    width: "400px",
    transition: { duration: 0.4 }
  }
};
```

---

## 响应式设计

### 📱 断点系统

```typescript
// tailwind.config.ts
export default {
  theme: {
    screens: {
      'sm': '640px',   // 手机横屏
      'md': '768px',   // 平板
      'lg': '1024px',  // 笔记本
      'xl': '1280px',  // 桌面
      '2xl': '1536px', // 大屏
    }
  }
}
```

### 🎯 响应式布局

#### 移动端 (< 768px)

```
┌─────────────────────────────┐
│  Header                     │
├─────────────────────────────┤
│                             │
│  Messages (全宽)             │
│                             │
│  [用户消息 - 右对齐]         │
│  [AI 消息 - 左对齐]          │
│                             │
├─────────────────────────────┤
│  [ResearchButton - 全宽]    │
│  或                          │
│  [ResearchProgress - 全宽]  │
├─────────────────────────────┤
│  [Input - 全宽]             │
└─────────────────────────────┘

CSS:
.research-panel {
  padding: 0 1rem;
  bottom: 60px;  /* 移动端输入框更小 */
}

.research-button {
  font-size: 0.875rem;
  padding: 0.75rem 1rem;
}

.progress-step {
  font-size: 0.8125rem;
}
```

#### 平板端 (768px - 1024px)

```
┌───────────────────────────────────┐
│  Header                           │
├───────────────────────────────────┤
│                                   │
│  Messages (max-w-4xl, 居中)       │
│                                   │
│                                   │
├───────────────────────────────────┤
│  [ResearchPanel - max-w-4xl]     │
├───────────────────────────────────┤
│  [Input - max-w-4xl, 居中]        │
└───────────────────────────────────┘

CSS:
.research-panel {
  max-width: 56rem;
  padding: 0 1.5rem;
}
```

#### 桌面端 (> 1024px)

```
┌─────────────┬──────────────────────────┐
│  Sidebar    │  Header                  │
│  (可折叠)   ├──────────────────────────┤
│             │                          │
│  History    │  Messages (max-w-4xl)    │
│             │                          │
│             ├──────────────────────────┤
│             │  [ResearchPanel]         │
│             ├──────────────────────────┤
│  [Account]  │  [Input]                 │
└─────────────┴──────────────────────────┘

带 Artifact:
┌──────┬───────────┬──────────────────┐
│ Side │  Chat     │  Artifact        │
│ bar  │  (400px)  │  (flex-1)        │
│      │           │                  │
│      │  Messages │  [报告内容]      │
│      │           │                  │
│      │  [Panel]  │                  │
│      │  [Input]  │                  │
└──────┴───────────┴──────────────────┘
```

### 📐 响应式 CSS

```css
/* 移动优先 */
.research-panel {
  position: sticky;
  bottom: 60px;
  padding: 0 0.5rem;
}

.research-button {
  font-size: 0.875rem;
  padding: 0.75rem 1rem;
}

.progress-step {
  font-size: 0.8125rem;
}

/* 平板 */
@media (min-width: 768px) {
  .research-panel {
    bottom: 72px;
    padding: 0 1rem;
  }

  .research-button {
    font-size: 1rem;
    padding: 0.875rem 1.25rem;
  }

  .progress-step {
    font-size: 0.875rem;
  }
}

/* 桌面 */
@media (min-width: 1024px) {
  .research-panel {
    padding: 0 1.5rem;
  }

  /* Artifact 激活时聊天区域压缩 */
  .chat-container.artifact-active {
    width: 400px;
  }
}

/* 大屏 */
@media (min-width: 1536px) {
  .research-panel {
    max-width: 64rem;
  }
}
```

---

## 验收标准

### ✅ 功能验收

#### 1. 研究按钮显示
- [ ] AI 消息包含研究关键词时自动显示
- [ ] 按钮位置正确 (sticky bottom-[72px])
- [ ] 按钮样式匹配设计 (渐变背景, Sparkles 图标)
- [ ] 移动端和桌面端都正确显示

#### 2. 研究流程
- [ ] 点击按钮后正确发起 SSE 连接
- [ ] ResearchButton 切换为 ResearchProgress
- [ ] 进度实时更新（< 1 秒延迟）
- [ ] 所有 SSE 事件正确接收（start, plan, progress, done, error）
- [ ] 进度百分比准确计算
- [ ] 步骤列表按时间顺序显示

#### 3. 报告发送
- [ ] done 事件触发 onComplete 回调
- [ ] sendMessage 正确调用
- [ ] 报告格式正确 ("Research completed:\n\n...")
- [ ] 新消息显示在聊天中
- [ ] AI 正确接收并处理报告

#### 4. Artifact 创建
- [ ] AI 调用 createDocument 工具
- [ ] Artifact 正确展示报告
- [ ] Markdown 渲染正确
- [ ] 复制、导出功能正常
- [ ] 追问后 updateDocument 正常工作

#### 5. 错误处理
- [ ] 连接失败时显示错误消息
- [ ] 重连机制正常工作（最多 3 次）
- [ ] 用户可以重试失败的研究
- [ ] 错误不导致应用崩溃

### 🎨 UI/UX 验收

#### 1. 视觉一致性
- [ ] 颜色系统匹配现有 UI
- [ ] 字体和字号一致
- [ ] 间距和圆角统一
- [ ] 深色模式正常工作

#### 2. 动画效果
- [ ] ResearchButton 淡入动画流畅
- [ ] 按钮点击有反馈动画
- [ ] ResearchProgress 切换动画自然
- [ ] 进度条填充平滑
- [ ] 步骤项逐个出现
- [ ] Artifact 展开动画流畅

#### 3. 响应式设计
- [ ] 移动端布局正确
- [ ] 平板端布局正确
- [ ] 桌面端布局正确
- [ ] Artifact 激活时布局适配
- [ ] 所有断点过渡平滑

#### 4. 交互体验
- [ ] 按钮 hover 状态明显
- [ ] 按钮 disabled 状态清晰
- [ ] 进度显示实时更新
- [ ] 完成后自动消失（2 秒）
- [ ] 用户可以随时滚动消息

### ⚡ 性能验收

#### 1. 加载性能
- [ ] 初始加载无明显延迟
- [ ] 组件渲染 < 100ms
- [ ] SSE 连接建立 < 2s
- [ ] 无不必要的重渲染

#### 2. 运行性能
- [ ] 进度更新不卡顿
- [ ] 长时间研究不内存泄漏
- [ ] 大报告渲染流畅
- [ ] 动画帧率 > 30 FPS

#### 3. 网络性能
- [ ] SSE 连接稳定
- [ ] 网络中断自动重连
- [ ] 弱网环境可用
- [ ] 超时正确处理

### 🧪 测试覆盖

#### 1. 单元测试
- [ ] detectResearchKeywords 函数测试
- [ ] extractResearchQuery 函数测试
- [ ] useResearchProgress Hook 测试
- [ ] 事件处理逻辑测试

#### 2. 组件测试
- [ ] ResearchButton 组件测试
- [ ] ResearchProgress 组件测试
- [ ] ResearchPanel 组件测试
- [ ] 状态切换测试

#### 3. 集成测试
- [ ] 完整研究流程测试
- [ ] sendMessage 集成测试
- [ ] Artifact 创建流程测试
- [ ] 错误场景测试

#### 4. E2E 测试
- [ ] 用户完整旅程测试
- [ ] 多种研究查询测试
- [ ] 追问流程测试
- [ ] 跨浏览器测试

---

## 附录

### 📚 参考文档

1. [AI SDK React Documentation](https://sdk.vercel.ai/docs/reference/ai-sdk-react)
2. [Framer Motion API](https://www.framer.com/motion/)
3. [Tailwind CSS Documentation](https://tailwindcss.com/docs)
4. [fetch-event-source Library](https://github.com/Azure/fetch-event-source)
5. [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)

### 🔗 相关文件

- `requirements.md` - 功能需求
- `design.md` - 技术设计
- `tasks.md` - 任务分解
- `ARCHITECTURE_CHANGES.md` - 架构变更
- Phase 2 实施报告 - 后端 API 文档

### 📊 设计决策记录

#### 决策 1: 在 Chat 组件级别管理研究状态

**原因**:
- 零侵入性，不修改现有组件
- 直接访问 sendMessage
- 清晰的数据流
- 易于维护

**替代方案**:
- 通过 Context 传递 sendMessage
- 在 MessageActions 中扩展

**结论**: 采用 Chat 组件级别管理

#### 决策 2: 使用 sticky 定位而非在消息中内联

**原因**:
- 始终可见，用户体验好
- 不影响消息滚动
- 清晰的视觉层级

**替代方案**:
- 在 AI 消息后内联显示
- 悬浮窗模式

**结论**: 采用 sticky 定位

#### 决策 3: 使用 fetch-event-source 而非原生 EventSource

**原因**:
- 支持 POST 方法
- 内置重连机制
- 更好的错误处理

**替代方案**:
- 原生 EventSource (仅支持 GET)
- WebSocket

**结论**: 采用 fetch-event-source

---

**文档版本**: 1.0
**最后更新**: 2025-10-31
**状态**: 已批准实施
**审核人**: [待填写]
