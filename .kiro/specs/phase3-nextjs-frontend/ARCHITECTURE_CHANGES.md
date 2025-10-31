# Phase 3 架构变更总结

## 文档信息

- **创建日期**: 2025-10-31
- **最后更新**: 2025-10-31 (API 修正)
- **变更原因**:
  1. AI SDK 工具调用模式不适合长时间 SSE 连接
  2. 代码库使用 useChat 模式，不是 useUIState/useActions 模式
- **影响范围**: requirements.md, design.md, tasks.md, ARCHITECTURE_CHANGES.md
- **时间节省**: 12 小时（120h → 108h）

---

## ⚠️ 重要 API 修正 (2025-10-31)

### 问题发现

在深度分析现有代码库后，发现原设计文档中存在 **API 使用错误**:

**错误假设**:
- 使用 `useUIState` from 'ai/rsc'
- 使用 `appendMessage` API 发送消息给 AI

**实际情况** (通过代码分析确认):
- 代码库使用 `useChat` Hook from 'ai/react' ([components/chat.tsx:5](components/chat.tsx))
- 使用 `sendMessage` 函数发送消息 ([components/chat.tsx:15-20](components/chat.tsx))
- **不存在** `useUIState` 或 `appendMessage` API

### 修正方案

**Hook 设计修正**:
```typescript
// ❌ 错误设计（原文档）
import { useUIState } from 'ai/rsc';
const [, setMessages] = useUIState();
setMessages(prev => [...prev, { role: 'user', display: report }]);

// ✅ 正确设计（修正后）
interface UseResearchProgressProps {
  prompt: string | null;
  onComplete?: (report: string) => void;  // 回调函数
}
// 父组件负责调用 sendMessage
```

**集成方式修正**:
```typescript
// ✅ 在 Message 组件中集成
import { useChat } from 'ai/react';

const { sendMessage } = useChat();
const { events, status } = useResearchProgress({
  prompt: researchPrompt,
  onComplete: (report) => {
    sendMessage({
      role: 'user',
      parts: [{ type: 'text', text: `Research completed:\n\n${report}` }]
    });
  }
});
```

### 影响范围

✅ **已修正的文件**:
1. `requirements.md` - Req 2, 5, 6 更新了 API 说明
2. `design.md` - Component 2 (Hook), Component 5 (Chat Flow) 更新
3. `tasks.md` - Day 3-4, Day 6-7 任务更新
4. `ARCHITECTURE_CHANGES.md` - 添加 API 修正说明

**关键变更点**:
- Hook 不再直接调用 setMessages
- Hook 通过 onComplete 回调通知父组件
- 父组件 (Message) 负责调用 sendMessage
- 集成位置明确在 components/message.tsx

---

## 核心问题分析

### 原架构问题

**问题 1**: startResearch 工具的 SSE 连接生命周期
- AI SDK 的 `execute` 函数必须返回才能继续流式响应
- 但 SSE 连接需要保持打开直到研究完成（可能数分钟）
- 如果 `execute` 立即返回，ReadableStream 会被垃圾回收，导致连接关闭

**问题 2**: taskId 提取不可行
- Phase 2 SSE 的 start 事件只包含 `{prompt: str}`
- 没有 taskId 字段可供提取
- 原设计假设可以从首个事件提取 taskId

**问题 3**: GET 端点不存在
- Phase 2 仅实现 POST /api/research/stream
- 原设计假设可以用 GET /api/research/stream?taskId=xxx
- EventSource 原生只支持 GET 请求

### 解决方案：用户触发 + 直接 SSE 订阅

**新架构**:
1. 用户手动触发（ResearchButton 组件）
2. 使用 fetch-event-source 支持 POST SSE
3. Hook 直接发起研究（无需 taskId）
4. Hook 通过 onComplete 回调通知父组件
5. 父组件通过 sendMessage (from useChat) 发送报告给 AI
6. AI 仅调用 createDocument，不调用 startResearch

**优势**:
- 零 Phase 2 后端改动
- SSE 连接生命周期清晰（用户主动控制）
- 简化前端逻辑（无需 taskId 管理）
- 降低复杂度，节省 12 小时开发时间

---

## 文件变更详情

### 1. requirements.md 变更

#### 删除的需求

**Requirement 1: startResearch 工具创建**（完全删除）
- 原功能：AI 调用工具启动研究，返回 taskId
- 删除原因：execute 函数返回后 SSE 流关闭
- 替代方案：Requirement 21 (ResearchButton)

#### 修改的需求

**Requirement 2: useResearchProgress Hook**
- **旧**: 接受 `taskId: string | null` 参数，使用 EventSource (GET)
- **新**: 接受 `{ prompt, onComplete }` 参数，使用 fetch-event-source (POST)
- **关键变更**:
  - 不再订阅已存在的任务，而是直接发起新任务
  - 使用 AbortController 代替 EventSource
  - ⚠️ **不使用 useUIState/appendMessage**（应用使用 useChat 模式）
  - 研究完成后通过 onComplete 回调通知父组件
  - 父组件负责调用 sendMessage 发送报告给 AI

**Requirement 3: API 代理路由**
- **旧**: 支持 POST 和 GET 两种方法
- **新**: 仅支持 POST 方法
- **关键变更**:
  - 移除 GET 端点（无需 taskId 参数）
  - 简化参数验证（仅验证 prompt）
  - 添加 CORS 响应头

**Requirement 5: 聊天流程改造**
- **旧**: AI 调用 startResearch → 返回 taskId → 前端订阅
- **新**: 用户点击 ResearchButton → Hook 直接 SSE → sendMessage 发送报告给 AI
- **关键变更**:
  - 移除工具集成步骤
  - 添加按钮集成步骤（在 Message 组件中）
  - ⚠️ 使用 sendMessage (from useChat)，不是 appendMessage
  - 集成位置明确：components/message.tsx

**Requirement 6: System Prompt 更新**
- **旧**: AI 调用 startResearch 启动研究
- **新**: AI 被动接收研究报告，调用 createDocument
- **关键变更**:
  - 移除工具调用说明
  - 添加报告处理说明（识别 "Research completed:" 消息）
  - 强调不要主动研究
  - 报告通过普通用户消息传递（sendMessage）

#### 新增的需求

**Requirement 21: ResearchButton 组件创建**（新增）
- **功能**: 用户手动触发研究任务的按钮组件
- **关键特性**:
  - 关键词检测自动显示
  - 状态管理（loading/disabled）
  - 移动端友好设计
  - 集成到聊天界面

---

### 2. design.md 变更

#### 组件设计变更

**删除的组件**:
- startResearch 工具（Component 1）
  - 包括完整的 tool 定义、execute 函数、taskId 提取逻辑

**新增的组件**:
- ResearchButton 组件（Component 1 新）
  - 文件：`components/research-button.tsx`
  - Props: `prompt`, `onStart`, `disabled`
  - 功能：用户手动触发研究

**修改的组件**:

1. **useResearchProgress Hook (Component 2)**
   - 参数：`taskId` → `prompt`
   - 实现：EventSource → fetch-event-source
   - 依赖：AbortController (新增)
   - done 事件处理：添加 appendMessage 调用

2. **API 代理路由 (Component 3)**
   - 方法：POST + GET → 仅 POST
   - 验证：添加 prompt 长度验证（>= 10 字符）
   - 响应头：添加 Access-Control-Allow-Origin

3. **聊天流程改造 (Component 5)**
   - 移除：startResearch 工具集成
   - 新增：ResearchButton 集成
   - 新增：关键词检测逻辑

4. **System Prompt (Component 6)**
   - 移除：startResearch 调用说明
   - 新增：报告接收处理说明
   - 强调：不主动研究，仅处理报告

#### 架构图更新

**技术方案流程图**:
```
旧: 用户输入 → AI 理解 → 调用工具 → 前端订阅
新: 用户输入 → 检测关键词 → 显示按钮 → 用户点击 → 直接 SSE
```

**系统架构图**:
- 移除：startResearch 工具节点
- 新增：ResearchButton 组件节点
- 修改：数据流向（用户触发 → Hook → API → Backend）
- 简化：移除 taskId 传递路径

#### 附录更新

**事件流示例**:
- 移除：工具调用和 taskId 相关步骤
- 新增：按钮点击和 appendMessage 步骤

**组件层次结构**:
- 新增：ResearchButton ← 新增（关键词检测后显示）

---

### 3. tasks.md 变更

#### 整体时间调整

**Week 1**: 40h → 32h (-8h)
- Day 1: 8h → 6h (-2h)
  - 删除 startResearch 工具任务（10 个任务，约 7.5h）
  - 新增 ResearchButton 组件任务（8 个任务，约 3.5h）
  - 节省：4 小时

- Day 2: 8h → 6h (-2h)
  - 删除 GET 端点实现任务（1 个任务，45min）
  - 简化测试任务
  - 节省：1.25 小时

- Day 3-4: 16h → 14h (-2h)
  - 删除手动重连逻辑任务（3 个任务，1.5h）
  - 使用 fetch-event-source 内置重连
  - 修改 Hook 参数和实现
  - 节省：1.5 小时

**Week 2**: 40h → 36h (-4h)
- Day 6-7: 16h → 14h (-2h)
  - 删除 startResearch 工具集成任务
  - 新增 ResearchButton 集成任务
  - 简化聊天流程改造
  - 节省：2 小时

- Day 8-9: 保持不变（组件实现）

**Week 3**: 40h（保持不变）

#### 关键任务变更

**Day 1 变更**:
- ~~1.2-1.11 startResearch 工具~~（删除）
- 1.2 安装 fetch-event-source 依赖（新增）
- 1.3-1.9 ResearchButton 组件（新增）

**Day 2 变更**:
- 2.3 添加 prompt 长度验证
- 2.8 添加 CORS 响应头
- ~~2.9 GET 方法处理器~~（删除）

**Day 3-4 变更**:
- 3.1 添加 fetch-event-source 导入
- 3.2 Hook 参数改为 prompt
- 3.3 新增 useUIState (appendMessage)
- 3.4 使用 AbortController
- 3.6 使用 fetchEventSource 调用
- 3.12 done 事件添加 appendMessage
- ~~3.15-3.17 重连逻辑~~（删除，库内置）

**Day 6-7 变更**:
- ~~5.2 导入 startResearch 工具~~（删除）
- 5.x 集成 ResearchButton（新增）
- 5.x 实现关键词检测（新增）

---

## 验收标准更新

### 技术验收

**移除的验收项**:
- startResearch 工具调用成功率
- taskId 提取准确率
- GET 端点功能测试

**新增的验收项**:
- ResearchButton 显示准确率（关键词检测）
- fetch-event-source POST SSE 连接稳定性
- appendMessage 报告传递准确性
- CORS 响应头正确性

**保留的验收项**:
- SSE 事件接收完整性
- 进度显示准确性
- 错误处理正确性
- 数据库集成功能

### 用户验收

**流程变更**:
1. 用户输入包含研究关键词
2. 系统自动显示 "Start Research" 按钮
3. 用户点击按钮
4. 系统显示实时进度
5. 研究完成后 AI 自动创建 Artifact
6. 用户可以追问和修改报告

**关键体验指标**:
- 按钮响应时间 < 100ms
- 关键词检测准确率 > 95%
- SSE 连接建立 < 2s
- 报告传递成功率 100%

---

## 依赖变更

### 新增依赖

```json
{
  "@microsoft/fetch-event-source": "^2.0.1"
}
```

**原因**: 支持 POST 方法的 SSE 连接

**替代**: 原生 EventSource（仅支持 GET）

### 移除依赖

无（原设计未引入额外依赖）

---

## 风险与缓解

### 技术风险

1. **fetch-event-source 库稳定性**
   - 风险：第三方库可能有 bug
   - 缓解：该库由 Microsoft 维护，广泛使用

2. **appendMessage API 可靠性**
   - 风险：消息可能丢失或格式错误
   - 缓解：添加完善的错误处理和日志

3. **关键词检测误判**
   - 风险：可能误显示或不显示按钮
   - 缓解：可配置的关键词列表，未来可 AI 增强

### 用户体验风险

1. **额外点击操作**
   - 风险：用户需要多点击一次按钮
   - 缓解：按钮位置明显，关键词检测自动化

2. **流程理解成本**
   - 风险：用户可能不理解为何要点击按钮
   - 缓解：清晰的按钮文案和 UI 提示

---

## 后续优化建议

### 短期（Phase 3）

1. **智能关键词检测**
   - 使用简单的 NLP 判断研究意图
   - 提高检测准确率

2. **按钮位置优化**
   - A/B 测试最佳位置
   - 移动端特殊处理

3. **进度显示增强**
   - 更直观的进度条
   - 预估剩余时间

### 长期（Phase 4+）

1. **自动触发选项**
   - 允许用户配置自动研究
   - 高级用户可跳过按钮

2. **研究历史管理**
   - 保存研究历史
   - 快速重新运行

3. **并发研究支持**
   - 支持多个研究同时进行
   - 任务队列管理

---

## 总结

### 核心成果

✅ **解决架构问题**: 彻底解决 SSE 连接生命周期问题
✅ **零后端改动**: 完全适配 Phase 2 现有 API
✅ **简化实现**: 减少 12 小时开发时间
✅ **提升可维护性**: 清晰的数据流和责任划分

### 权衡取舍

✅ **获得**:
- 架构简洁性
- 后端兼容性
- 开发效率

❌ **失去**:
- AI 主动触发研究能力
- 流畅的对话体验（需额外点击）

### 建议

**立即执行**: 采用新架构，按 tasks.md 执行实现

**持续改进**: 收集用户反馈，优化按钮 UX

**未来考虑**: 如果 AI SDK 支持长时间异步工具，可重新评估

---

**文档版本**: 1.0
**最后更新**: 2025-10-31
**状态**: 已批准实施
