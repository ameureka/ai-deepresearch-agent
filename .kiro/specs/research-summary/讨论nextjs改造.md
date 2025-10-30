重新评估 Next.js 功能
1️⃣ 聊天界面（包含思考输出）
你看到的界面特点:

左侧：对话历史
右侧：AI 回复（带思考过程）
底部：输入框
为什么我建议删除:

我以为你只想要"一次性研究报告生成"
但其实聊天界面非常适合研究场景！
重新建议：保留并改造 ✅

改造方案:

// 保留聊天界面，但改为"研究对话"模式

用户: "帮我研究量子计算的最新进展"
    ↓
AI: "好的，我将启动多代理研究工作流..."
    [显示实时进度]
    ✅ 步骤1: Tavily 搜索完成
    ⏳ 步骤2: arXiv 搜索中...
    ↓
AI: "研究完成！这是我的发现：[完整报告]"
    ↓
用户: "能加上成本分析吗？"
    ↓
AI: "当然，让我补充成本分析..."
保留的价值:

✅ 对话式交互更自然
✅ 可以追问和补充
✅ 思考过程可视化（Grok Reasoning）
✅ 历史记录管理
2️⃣ Artifacts 编辑器
什么是 Artifacts: 这是 AI Chatbot 的核心创新功能！

工作原理:

┌─────────────────────────────────────────┐
│  左侧：对话区                             │
│  用户: "帮我写一个排序算法"               │
│  AI: "好的，我来创建一个代码文档..."      │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  右侧：Artifact 实时编辑器                │
│  ┌───────────────────────────────────┐  │
│  │ # 排序算法                         │  │
│  │ def bubble_sort(arr):             │  │
│  │     for i in range(len(arr)):     │  │
│  │         ...                       │  │
│  └───────────────────────────────────┘  │
│  [复制] [下载] [编辑]                    │
└─────────────────────────────────────────┘
支持的类型:

text - Markdown 文档
code - 代码编辑器（Python、JS 等）
sheet - 电子表格（CSV）
image - 图片编辑器
为什么我建议删除:

我以为你只需要"静态报告展示"
但 Artifacts 非常适合展示研究报告！
重新建议：保留并利用 ✅

用于研究场景:

// 将研究报告作为 Artifact 展示

用户: "研究 GPT-4 的技术细节"
    ↓
AI 调用 FastAPI 研究服务
    ↓
研究完成后，创建 Artifact:
┌─────────────────────────────────────┐
│  Artifact: GPT-4 技术分析报告        │
│  ┌───────────────────────────────┐  │
│  │ # GPT-4 技术分析               │  │
│  │                               │  │
│  │ ## 1. 架构设计                 │  │
│  │ GPT-4 采用 Transformer...     │  │
│  │                               │  │
│  │ ## 2. 训练方法                 │  │
│  │ ...                           │  │
│  └───────────────────────────────┘  │
│  [导出 PDF] [复制] [继续研究]       │
└─────────────────────────────────────┘
保留的价值:

✅ 报告实时生成和展示
✅ 可以编辑和导出
✅ 支持 Markdown 渲染
✅ 用户体验极佳
3️⃣ 多模态输入
什么是多模态输入:

输入框支持：
- 📝 文本输入
- 📎 文件上传（PDF、图片、CSV）
- 🖼️ 图片拖拽
- 📊 数据文件
示例:

用户上传一篇 PDF 论文
    ↓
AI: "我看到你上传了一篇关于 Transformer 的论文"
    ↓
用户: "帮我总结这篇论文的核心观点"
    ↓
AI: 分析 PDF 内容并生成总结
为什么我建议删除:

你的 FastAPI 系统目前不支持文件处理
增加复杂度
重新建议：暂时保留，未来扩展 ⚠️

当前阶段:

先禁用文件上传功能
只保留文本输入
未来扩展:

支持上传论文 PDF
支持上传数据文件
AI 分析文件内容
4️⃣ 原有工具（lib/ai/tools/）
原有工具列表:

lib/ai/tools/
├── get-weather.ts        // 天气查询
├── create-document.ts    // 创建 Artifact 文档
├── update-document.ts    // 更新 Artifact 文档
└── request-suggestions.ts // 请求编辑建议
这些工具的作用:

AI 在对话中可以"调用工具"
例如：用户问天气 → AI 调用 get-weather → 返回天气信息
为什么我建议删除:

你的研究功能在 FastAPI 中实现
这些工具是为聊天场景设计的
重新建议：部分保留，部分改造 ✅

保留:

create-document.ts - 用于创建研究报告 Artifact
update-document.ts - 用于更新报告
删除:

get-weather.ts - 研究场景不需要
request-suggestions.ts - 暂时不需要
新增:

// lib/ai/tools/start-research.ts
// 新工具：启动研究任务

export const startResearch = tool({
  description: "Start a comprehensive research task",
  inputSchema: z.object({
    topic: z.string(),
  }),
  execute: async ({ topic }) => {
    // 调用 FastAPI 研究服务
    const res = await fetch('http://localhost:8000/api/v1/research', {
      method: 'POST',
      body: JSON.stringify({ prompt: topic }),
    });
    
    const data = await res.json();
    
    return {
      taskId: data.task_id,
      message: `Research started. Task ID: ${data.task_id}`,
    };
  },
});
🎯 修正后的方案
新的简化策略
保留的核心功能:

✅ 聊天界面 - 改为"研究对话"模式
✅ Artifacts 系统 - 用于展示研究报告
✅ 认证系统 - 用户登录
✅ 数据库 - 存储历史
✅ UI 组件库 - shadcn/ui
删除的功能:

❌ 天气工具
❌ 图片编辑器（暂时）
❌ 表格编辑器（暂时）
❌ 多模态输入（暂时禁用）
改造的功能:

🔄 聊天 → 研究对话
🔄 Artifacts → 研究报告展示
🔄 工具系统 → 研究工具
📋 修正后的实施方案
阶段 3.1: 保留核心，改造交互（3-5 天）
cd achive/ai-chatbot-main

# 只删除这些
rm -rf components/weather.tsx  # 删除天气组件
rm -rf components/sheet-editor.tsx  # 删除表格编辑器
rm -rf components/image-editor.tsx  # 删除图片编辑器
rm -rf lib/ai/tools/get-weather.ts  # 删除天气工具
rm -rf lib/ai/tools/request-suggestions.ts  # 删除建议工具

# 保留这些（重要！）
# ✅ app/(chat)  - 聊天界面（改造为研究对话）
# ✅ components/artifact.tsx  - Artifact 系统
# ✅ components/text-editor.tsx  - 文本编辑器
# ✅ components/code-editor.tsx  - 代码编辑器
# ✅ lib/ai/tools/create-document.ts  - 创建文档
# ✅ lib/ai/tools/update-document.ts  - 更新文档
阶段 3.2: 添加研究工具（2-3 天）
// lib/ai/tools/start-research.ts

import { tool } from 'ai';
import { z } from 'zod';

export const startResearch = tool({
  description: 'Start a comprehensive multi-agent research task',
  inputSchema: z.object({
    topic: z.string().describe('Research topic or question'),
  }),
  execute: async ({ topic }) => {
    const RESEARCH_API = process.env.RESEARCH_API_URL;
    
    const response = await fetch(`${RESEARCH_API}/api/v1/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: topic }),
    });
    
    const data = await response.json();
    
    // 返回给 AI，让它创建 Artifact 展示报告
    return {
      taskId: data.task_id,
      status: 'started',
      message: 'Research task started successfully',
    };
  },
});
阶段 3.3: 改造聊天流程（3-4 天）
// app/(chat)/api/chat/route.ts

export async function POST(request: Request) {
  const { messages } = await request.json();
  
  const result = streamText({
    model: myProvider('chat-model'),
    messages,
    tools: {
      // 保留的工具
      createDocument: createDocument({ session, dataStream }),
      updateDocument: updateDocument({ session, dataStream }),
      
      // 新增的研究工具
      startResearch: startResearch,
      getResearchProgress: getResearchProgress,
    },
    system: `你是一个AI研究助手。当用户要求研究某个主题时，
    使用 startResearch 工具启动研究任务，然后使用 createDocument 
    创建 Artifact 展示研究报告。`,
  });
  
  return result.toDataStreamResponse();
}
💡 最终效果
用户体验流程
1. 用户登录系统
    ↓
2. 在聊天框输入："帮我研究量子计算的最新进展"
    ↓
3. AI 回复："好的，我将启动多代理研究工作流..."
   [AI 调用 startResearch 工具]
    ↓
4. 右侧显示实时进度：
   ✅ Tavily 搜索完成
   ⏳ arXiv 搜索中...
   ⏸️ 综合分析等待中
    ↓
5. 研究完成后，AI 说："研究完成！让我为你创建报告..."
   [AI 调用 createDocument 工具]
    ↓
6. 右侧 Artifact 区域显示完整报告（Markdown 格式）
   用户可以：
   - 阅读报告
   - 复制内容
   - 导出 PDF
   - 继续提问
    ↓
7. 用户追问："能加上成本分析吗？"
    ↓
8. AI 调用 updateDocument 更新报告
✅ 总结
你的直觉是对的！

聊天界面 - 非常适合研究场景，保留！
Artifacts - 完美的报告展示方式，保留！
多模态 - 未来有价值，暂时禁用
原有工具 - 部分保留，部分改造
新的删除策略:

只删除明确不需要的（天气、图片编辑等）
保留所有核心交互功能
改造而不是删除
这样既保留了优秀的用户体验，又专注于研究功能！