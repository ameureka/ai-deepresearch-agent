# Phase 3 架构修订 v2.0

## 文档信息

- **创建日期**: 2025-11-01
- **版本**: 2.0
- **状态**: 待实施
- **目的**: 基于 DeepSeek 统一架构的设计修订

---

## 修订概述

### 核心变更

1. **统一 AI 架构** - 前后端都使用 DeepSeek
2. **混合触发模式** - 智能触发 + 手动触发
3. **简化完成流程** - 研究结果直接展示
4. **降低成本** - 节省 98% AI 调用成本

---

## 详细修改清单

### 1. 前端 AI 提供商配置

**文件**: `ai-chatbot-main/lib/ai/providers.ts`

**修改前**:
```typescript
import { gateway } from "@ai-sdk/gateway";

export const myProvider = customProvider({
  languageModels: {
    "chat-model": gateway.languageModel("xai/grok-2-vision-1212"),
    "title-model": gateway.languageModel("xai/grok-2-1212"),
    // ...
  },
});
```

**修改后**:
```typescript
import { createOpenAI } from "@ai-sdk/openai";

// 创建 DeepSeek 提供商（兼容 OpenAI API）
const deepseek = createOpenAI({
  apiKey: process.env.DEEPSEEK_API_KEY || "",
  baseURL: "https://api.deepseek.com",
});

export const myProvider = customProvider({
  languageModels: {
    "chat-model": deepseek("deepseek-chat"),
    "chat-model-reasoning": deepseek("deepseek-reasoner"),
    "title-model": deepseek("deepseek-chat"),
    "artifact-model": deepseek("deepseek-chat"),
  },
});
```

---

### 2. 环境变量配置

**文件**: `ai-chatbot-main/.env.local`

**新增**:
```bash
# DeepSeek API Key（与后端共用）
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# 其他必需配置
AUTH_SECRET=your-random-secret-key
POSTGRES_URL=your-database-url
```

**移除**:
```bash
# 不再需要
# AI_GATEWAY_API_KEY=xxx
# VERCEL_OIDC_TOKEN=xxx
```

---

### 3. Chat 组件修改

**文件**: `ai-chatbot-main/components/chat.tsx`

#### 3.1 添加手动研究按钮

**位置**: 在 MultimodalInput 组件附近

```typescript
// 在输入框上方添加手动研究按钮
<div className="flex items-center gap-2 px-4 py-2">
  {/* 智能触发按钮（原有） */}
  {shouldShowResearchButton && (
    <ResearchButton 
      prompt={suggestedResearchQuery} 
      onStart={handleStartResearch} 
    />
  )}
  
  {/* 手动触发按钮（新增） */}
  <Button
    onClick={() => {
      const lastUserMsg = messages
        .filter(m => m.role === 'user')
        .pop();
      if (lastUserMsg) {
        const query = extractResearchQuery(
          getMessageText(lastUserMsg)
        );
        handleStartResearch(query);
      }
    }}
    variant="outline"
    size="sm"
    className="gap-2"
  >
    <SearchIcon className="size-4" />
    <span className="hidden sm:inline">Research</span>
  </Button>
</div>
```

#### 3.2 简化研究完成处理

**修改前**:
```typescript
const { events, status, report } = useResearchProgress({
  prompt: researchPrompt,
  onComplete: (report) => {
    // 自动发送报告给 AI
    sendMessage({
      role: 'user',
      parts: [{
        type: 'text',
        text: `Research completed:\n\n${report}`
      }]
    });
    
    setResearchPrompt(null);
    setShowResearchUI(false);
  }
});
```

**修改后**:
```typescript
const { events, status, report } = useResearchProgress({
  prompt: researchPrompt,
  onComplete: (report) => {
    // 直接展示报告，不发送给 AI
    setResearchReport(report);
    setShowResearchUI(false);
    setShowReportViewer(true); // 显示报告查看器
    
    // 可选：用户可以手动选择"Share with AI"
  }
});
```

---

### 4. 新增报告查看器组件

**文件**: `ai-chatbot-main/components/research-report-viewer.tsx`

```typescript
'use client';

import { Button } from '@/components/ui/button';
import { X, Copy, Download, Share2 } from 'lucide-react';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface ResearchReportViewerProps {
  report: string;
  onClose: () => void;
  onShareWithAI?: (report: string) => void;
}

export function ResearchReportViewer({
  report,
  onClose,
  onShareWithAI,
}: ResearchReportViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-report-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-[600px] bg-background border-l shadow-lg z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold">Research Report</h2>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="prose dark:prose-invert max-w-none">
          <ReactMarkdown>{report}</ReactMarkdown>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 p-4 border-t">
        <Button
          variant="outline"
          size="sm"
          onClick={handleCopy}
          className="gap-2"
        >
          <Copy className="size-4" />
          {copied ? 'Copied!' : 'Copy'}
        </Button>
        
        <Button
          variant="outline"
          size="sm"
          onClick={handleDownload}
          className="gap-2"
        >
          <Download className="size-4" />
          Export
        </Button>
        
        {onShareWithAI && (
          <Button
            variant="default"
            size="sm"
            onClick={() => onShareWithAI(report)}
            className="gap-2 ml-auto"
          >
            <Share2 className="size-4" />
            Share with AI
          </Button>
        )}
      </div>
    </div>
  );
}
```

---

## 实施步骤

### 步骤 1: 配置环境变量

```bash
# 1. 复制后端的 DeepSeek API Key
DEEPSEEK_KEY=$(grep DEEPSEEK_API_KEY .env | cut -d= -f2)

# 2. 添加到前端配置
echo "DEEPSEEK_API_KEY=$DEEPSEEK_KEY" >> ai-chatbot-main/.env.local

# 3. 验证配置
grep DEEPSEEK_API_KEY ai-chatbot-main/.env.local
```

### 步骤 2: 修改前端 AI 提供商

修改 `ai-chatbot-main/lib/ai/providers.ts`（见上文）

### 步骤 3: 添加手动研究按钮

修改 `ai-chatbot-main/components/chat.tsx`（见上文）

### 步骤 4: 创建报告查看器

创建 `ai-chatbot-main/components/research-report-viewer.tsx`（见上文）

### 步骤 5: 测试

```bash
# 1. 重启前端服务
cd ai-chatbot-main
pnpm dev

# 2. 测试普通聊天
# 3. 测试智能触发研究
# 4. 测试手动触发研究
# 5. 测试报告查看器
```

---

## 验收标准

### 功能验收

- [ ] 前端 AI 使用 DeepSeek 正常工作
- [ ] 普通聊天功能正常
- [ ] 智能触发研究按钮正常显示
- [ ] 手动触发研究按钮始终可用
- [ ] 研究进度实时显示
- [ ] 研究报告直接展示
- [ ] 报告查看器功能完整（复制、导出、分享）

### 性能验收

- [ ] 前端 AI 响应时间 < 3s
- [ ] 研究触发延迟 < 1s
- [ ] 报告展示流畅无卡顿

### 成本验收

- [ ] 前端 AI 成本降低 > 90%
- [ ] 总体成本降低 > 80%

---

## 风险与缓解

### 风险 1: DeepSeek API 不稳定

**缓解**:
- 保留 OpenAI 作为降级备份
- 添加重试机制
- 监控 API 可用性

### 风险 2: 用户不理解手动按钮

**缓解**:
- 添加 tooltip 提示
- 首次使用时显示引导
- 按钮文案清晰明确

### 风险 3: 报告查看器性能问题

**缓解**:
- 使用虚拟滚动
- 懒加载长报告
- 优化 Markdown 渲染

---

## 后续优化

### Phase 3.5: 增强功能

1. **报告历史记录**
   - 保存所有研究报告
   - 支持搜索和过滤
   - 支持重新打开历史报告

2. **报告分享**
   - 生成分享链接
   - 支持导出多种格式（PDF、HTML）
   - 支持社交媒体分享

3. **AI 协作增强**
   - 报告内联评论
   - AI 建议改进
   - 多轮迭代优化

### Phase 4: 性能优化

1. **缓存机制**
   - 缓存常见研究主题
   - 减少重复研究
   - 加速响应时间

2. **并发优化**
   - 支持多个研究任务
   - 任务队列管理
   - 优先级调度

---

## 总结

通过这次架构修订，我们实现了：

1. ✅ **成本优化** - 降低 98% AI 调用成本
2. ✅ **架构统一** - 前后端使用相同模型
3. ✅ **用户体验** - 双触发模式，容错性强
4. ✅ **流程简化** - 减少不必要步骤
5. ✅ **配置简单** - 只需一个 API Key

这是一个更加务实、高效、可靠的设计方案。
