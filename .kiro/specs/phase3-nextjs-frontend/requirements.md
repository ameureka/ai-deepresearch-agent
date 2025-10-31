# Phase 3: Next.js 前端改造 - 需求文档

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 3 - Next.js 前端改造
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **状态**: 待实施
- **依赖**: Phase 1 (DeepSeek 集成) + Phase 2 (API 标准化) 必须完成

---

## 简介

本文档定义了 Phase 3（Next.js 前端改造）的功能需求。该阶段的目标是改造 AI Chatbot 为研究助手，保留优秀的对话和 Artifacts 体验，采用工具调用 + SSE 订阅的混合架构，预计 3 周完成。

---

## 术语表

- **System**: Next.js 前端应用
- **AI Chatbot**: 现有的 Next.js 聊天应用（基础）
- **Research Assistant**: 改造后的研究助手应用
- **startResearch Tool**: 启动研究任务的 AI 工具
- **SSE**: Server-Sent Events，服务器推送事件
- **useResearchProgress Hook**: 订阅研究进度的 React Hook
- **ResearchProgress Component**: 显示研究进度的 React 组件
- **Artifact**: 右侧展示区域，用于显示生成的文档
- **API Proxy**: Next.js API 路由代理
- **EventSource**: 浏览器原生 SSE 客户端
- **Research Task**: 研究任务数据模型
- **System Prompt**: AI 系统提示词

---

## 需求

### ~~Requirement 1: startResearch 工具创建~~ (已删除 - 架构调整)

**变更说明**:
- **原设计问题**: AI SDK 工具调用模式不适合长时间 SSE 连接，execute 函数返回后会导致 SSE 流关闭
- **解决方案**: 采用用户手动触发 + 直接 SSE 订阅的架构，见 Requirement 21

### Requirement 2: useResearchProgress Hook 实现

**用户故事**: 作为前端开发者，我希望有一个 Hook 直接发起研究并订阅进度，以便实时显示进度

**架构变更**: 不再接受 taskId，改为接受 prompt 参数直接发起 POST SSE 连接

**关键 API 说明**:
- 该应用使用 `useChat` Hook (from `ai/react`)，NOT `useUIState`/`useActions`
- 使用 `sendMessage` 函数发送消息给 AI，NOT `appendMessage`
- 使用 `fetch-event-source` 库（支持 POST 方法的 SSE）

#### 验收标准

1. THE System SHALL 创建 useResearchProgress Hook 文件 `hooks/use-research-progress.ts`
2. THE Hook SHALL 接受以下参数:
   - `prompt: string | null` - 研究问题
   - `onComplete: (report: string) => void` - 研究完成回调
3. WHEN prompt 存在时，THE Hook SHALL 使用 fetch-event-source 库发起 POST SSE 连接
4. THE Hook SHALL 调用 POST /api/research/stream 接口并传递 prompt
5. THE Hook SHALL 监听 SSE 事件: start, plan, progress, done, error
6. THE Hook SHALL 维护状态: events, status, report, error
7. THE Hook SHALL 实现自动重连机制（fetch-event-source 内置，最多 3 次）
8. THE Hook SHALL 使用指数退避策略（500ms, 1s, 2s）
9. WHEN 组件卸载时，THE Hook SHALL 中止连接（AbortController）
10. WHEN 接收到 done 事件后，THE Hook SHALL 调用 onComplete 回调传递完整报告
11. THE Hook SHALL 在接收到 done 或 error 事件后自动关闭连接

### Requirement 3: API 代理路由实现

**用户故事**: 作为前端开发者，我希望通过 Next.js API 路由代理后端请求，以便处理 CORS 和认证

**架构简化**: 仅需简单的 POST 代理，无需 GET 接口（fetch-event-source 支持 POST SSE）

#### 验收标准

1. THE System SHALL 创建 API 路由 `app/api/research/stream/route.ts`
2. THE System SHALL 仅支持 POST 方法（简化实现）
3. THE System SHALL 从请求体中提取 prompt 参数
4. THE System SHALL 从环境变量读取 RESEARCH_API_URL
5. THE System SHALL 代理 POST 请求到 FastAPI 后端 /api/research/stream
6. THE System SHALL 直接返回后端的 SSE 流（text/event-stream）
7. THE System SHALL 设置正确的响应头（Cache-Control, X-Accel-Buffering, Connection）
8. THE System SHALL 处理代理错误并返回友好提示
9. THE System SHALL 验证 RESEARCH_API_URL 已配置，否则返回 500 错误

### Requirement 4: ResearchProgress 组件创建

**用户故事**: 作为用户，我希望看到研究进度的可视化展示，以便了解研究状态

**Props 说明**: ResearchProgress 组件接受 events（SSE 事件数组）和 status（研究状态）作为 Props，而非 taskId

#### 验收标准

1. THE System SHALL 创建 ResearchProgress 组件 `components/research-progress.tsx`
2. THE Component SHALL 接受 events 属性（SSE 事件数组）
3. THE Component SHALL 接受 status 属性（'idle' | 'researching' | 'completed' | 'failed'）
4. WHEN status 为 'idle' 时，THE Component SHALL 不显示任何内容
5. THE Component SHALL 显示当前状态图标（运行中、完成、失败）
6. THE Component SHALL 显示进度列表（每个步骤，从 events 数组读取）
7. THE Component SHALL 显示错误信息（从 events 中的 error 事件读取）
8. THE Component SHALL 根据 events 数组动态渲染进度步骤
9. THE Component SHALL 有清晰的视觉设计（图标、颜色、动画）

### Requirement 5: 聊天流程改造

**用户故事**: 作为用户，我希望能够在聊天中发起研究，以便获得研究报告

**架构变更**:
- **旧**: AI 调用 startResearch 工具 → 返回 taskId → Hook 订阅
- **新**: 用户点击 ResearchButton → Hook 直接 SSE → 通过 sendMessage 发送报告给 AI

**集成位置**: ResearchPanel（包含 ResearchButton 和 ResearchProgress）应集成在 Chat 组件中（components/chat.tsx），使用 sticky 定位在聊天输入框上方

#### 验收标准

1. THE System SHALL 在 Chat 组件中集成 ResearchPanel（包含 ResearchButton 和 ResearchProgress）
2. WHEN AI 消息包含研究关键词时，THE System SHALL 在聊天输入框上方（sticky 定位）显示 ResearchButton
3. WHEN 用户点击按钮时，THE System SHALL 使用 useResearchProgress Hook 发起研究
4. THE System SHALL 在聊天界面显示 ResearchProgress 组件实时显示进度
5. WHEN 研究完成时，THE System SHALL 通过 `sendMessage` 函数（from `useChat` Hook）将报告发送给 AI
6. THE sendMessage 调用 SHALL 格式化为:
   ```typescript
   sendMessage({
     role: 'user',
     parts: [{ type: 'text', text: `Research completed:\n\n${report}` }]
   });
   ```
7. THE AI SHALL 调用 createDocument 工具创建 Artifact
8. THE System SHALL 在 Artifact 中显示研究报告
9. WHEN 用户追问时，THE AI SHALL 调用 updateDocument 更新报告

### Requirement 6: System Prompt 更新

**用户故事**: 作为开发者，我希望 System Prompt 能够指导 AI 正确处理研究报告

**架构变更**: AI 不再需要调用 startResearch 工具，仅需处理接收到的研究报告

**API 说明**: 研究报告通过 `sendMessage` 函数发送给 AI，格式为 `Research completed:\n\n${report}`

#### 验收标准

1. THE System SHALL 更新 System Prompt 文件 `lib/ai/prompts.ts`
2. THE System Prompt SHALL 说明 AI 会接收到以 "Research completed:" 开头的用户消息
3. THE System Prompt SHALL 指导 AI 识别这类消息并使用 createDocument 工具创建 Artifact
4. THE System Prompt SHALL 说明如何处理追问: updateDocument
5. THE System Prompt SHALL 避免 AI 自由发挥，确保流程一致
6. THE System Prompt SHALL 包含示例对话流程:
   ```
   User: [研究关键词]
   [用户点击 ResearchButton]
   [系统显示进度]
   User: Research completed: [完整报告]
   AI: [调用 createDocument 创建 Artifact]
   User: [追问]
   AI: [调用 updateDocument 更新 Artifact]
   ```

### Requirement 7: 数据库 Schema 扩展

**用户故事**: 作为开发者，我希望扩展数据库 Schema 以支持研究任务存储

#### 验收标准

1. THE System SHALL 在 `lib/db/schema.ts` 中添加 researchTask 表
2. THE researchTask 表 SHALL 包含字段: id, chatId, userId, prompt, status, artifactId
3. THE researchTask 表 SHALL 包含进度字段: progress (JSON)
4. THE researchTask 表 SHALL 包含结果字段: result, error
5. THE researchTask 表 SHALL 包含时间戳: createdAt, updatedAt, completedAt
6. THE System SHALL 提供查询函数: saveResearchTask, updateResearchTaskStatus, getResearchTasksByChatId
7. THE System SHALL 运行数据库迁移创建新表

### Requirement 8: Artifact 集成

**用户故事**: 作为用户，我希望研究报告自动显示在 Artifact 中，以便阅读和导出

#### 验收标准

1. WHEN 研究完成时，THE AI SHALL 自动调用 createDocument 工具
2. THE createDocument 工具 SHALL 创建类型为 "text" 的 Artifact
3. THE Artifact SHALL 包含完整的研究报告
4. THE Artifact SHALL 支持 Markdown 渲染
5. THE Artifact SHALL 支持复制和导出功能
6. WHEN 用户追问时，THE AI SHALL 调用 updateDocument 更新 Artifact
7. THE System SHALL 保持 Artifact 版本历史

### Requirement 9: 错误处理

**用户故事**: 作为用户，我希望在研究失败时看到友好的错误提示

#### 验收标准

1. WHEN startResearch 工具调用失败时，THE System SHALL 显示错误消息
2. WHEN SSE 连接失败时，THE System SHALL 尝试重连（最多 3 次）
3. WHEN 重连失败时，THE System SHALL 显示 "连接失败" 错误
4. WHEN 研究过程中出错时，THE System SHALL 显示错误事件中的消息
5. THE System SHALL 记录所有错误到浏览器控制台
6. THE System SHALL 不因错误导致应用崩溃

### Requirement 10: 重连机制

**用户故事**: 作为用户，我希望在网络中断时系统能够自动重连

#### 验收标准

1. THE useResearchProgress Hook SHALL 实现重连逻辑
2. WHEN EventSource 触发 onerror 时，THE Hook SHALL 尝试重连
3. THE Hook SHALL 使用指数退避策略: 500ms, 1s, 2s
4. THE Hook SHALL 最多重连 3 次
5. WHEN 重连成功时，THE Hook SHALL 重置重试计数
6. WHEN 达到最大重试次数时，THE Hook SHALL 设置状态为 'failed'
7. THE Hook SHALL 记录重连尝试到控制台

### Requirement 11: 环境变量配置

**用户故事**: 作为开发者，我希望能够配置后端 API URL

#### 验收标准

1. THE System SHALL 从环境变量读取 RESEARCH_API_URL
2. THE System SHALL 在开发环境默认使用 http://localhost:8000
3. THE System SHALL 在生产环境使用配置的 URL
4. THE System SHALL 提供 .env.example 文件
5. WHEN RESEARCH_API_URL 未配置时，THE System SHALL 返回清晰的错误信息

### Requirement 12: 功能清理

**用户故事**: 作为开发者，我希望删除不需要的功能，以便简化代码

#### 验收标准

1. THE System SHALL 删除天气工具 `lib/ai/tools/get-weather.ts`
2. THE System SHALL 删除图片编辑器组件（如果存在）
3. THE System SHALL 删除表格编辑器组件（如果存在）
4. THE System SHALL 保留核心组件: chat, artifact, text-editor, code-editor
5. THE System SHALL 保留认证系统
6. THE System SHALL 保留数据库功能
7. THE System SHALL 更新工具导入，移除已删除的工具

### Requirement 13: 性能要求

**用户故事**: 作为用户，我希望应用响应快速，以便获得良好体验

#### 验收标准

1. THE System SHALL 在 1 秒内调用 startResearch 工具
2. THE System SHALL 在 2 秒内建立 SSE 连接
3. THE System SHALL 实时显示进度更新（延迟 < 1 秒）
4. THE System SHALL 不因长时间运行导致内存泄漏
5. THE System SHALL 支持多个标签页同时使用

### Requirement 14: 用户体验

**用户故事**: 作为用户，我希望有流畅的研究体验

#### 验收标准

1. WHEN 用户发起研究时，THE System SHALL 立即显示 "研究已开始" 消息
2. THE System SHALL 实时显示研究进度
3. THE System SHALL 在进度组件中显示当前步骤
4. WHEN 研究完成时，THE System SHALL 自动显示报告
5. THE System SHALL 支持用户追问和补充
6. THE System SHALL 保持对话历史
7. THE System SHALL 支持查看历史研究

### Requirement 15: 移动端适配

**用户故事**: 作为移动端用户，我希望能够在手机上使用研究功能

#### 验收标准

1. THE System SHALL 在移动端正确显示聊天界面
2. THE System SHALL 在移动端正确显示进度组件
3. THE System SHALL 在移动端正确显示 Artifact
4. THE System SHALL 支持移动端的触摸操作
5. THE System SHALL 在小屏幕上自适应布局

### Requirement 16: 历史记录

**用户故事**: 作为用户，我希望能够查看历史研究记录

#### 验收标准

1. THE System SHALL 保存所有研究任务到数据库
2. THE System SHALL 关联研究任务到对话
3. THE System SHALL 提供查询历史研究的接口
4. THE System SHALL 在聊天历史中显示研究任务
5. THE System SHALL 支持重新查看历史报告

### Requirement 17: 测试覆盖

**用户故事**: 作为开发者，我希望核心功能有测试覆盖

#### 验收标准

1. THE System SHALL 为 startResearch 工具编写单元测试
2. THE System SHALL 为 useResearchProgress Hook 编写单元测试
3. THE System SHALL 为 API 代理路由编写集成测试
4. THE System SHALL 为 ResearchProgress 组件编写组件测试
5. THE System SHALL 执行端到端测试验证完整流程

### Requirement 18: 简化设计原则

**用户故事**: 作为开发者，我希望实现简化，以便快速上线

#### 验收标准

1. THE System SHALL 不实现 traceId 追踪（延后）
2. THE System SHALL 不实现复杂的心跳机制（使用浏览器自动重连）
3. THE System SHALL 不实现回退机制（直接显示错误）
4. THE System SHALL 使用 1 个 API 代理路由（不分离 POST 和 GET）
5. THE System SHALL 不实现性能优化（懒加载、虚拟滚动）延后

### Requirement 19: 部署准备

**用户故事**: 作为运维人员，我希望前端可以部署到 Vercel

#### 验收标准

1. THE System SHALL 配置所有必需的环境变量
2. THE System SHALL 在 Vercel 部署成功
3. THE System SHALL 连接到 Render 后端
4. THE System SHALL 连接到 Neon 数据库
5. THE System SHALL 在生产环境正常工作

### Requirement 20: 文档完整性

**用户故事**: 作为开发者，我希望有完整的文档

#### 验收标准

1. THE System SHALL 更新 README 说明研究功能
2. THE System SHALL 提供环境变量配置说明
3. THE System SHALL 提供开发指南
4. THE System SHALL 提供部署指南
5. THE System SHALL 提供故障排查指南

### Requirement 21: ResearchButton 组件创建 ⭐ (新增)

**用户故事**: 作为用户，我希望有一个明确的按钮来发起研究任务，以便清楚地触发研究功能

**设计原因**: 由于 AI SDK 工具调用模式不适合长时间 SSE 连接，改为用户手动触发研究

#### 验收标准

1. THE System SHALL 创建 ResearchButton 组件 `components/research-button.tsx`
2. THE Component SHALL 接受 prompt 属性（研究问题文本）
3. THE Component SHALL 接受 isActive 属性（是否显示按钮）
4. THE Component SHALL 接受 onStart 回调函数
5. WHEN isActive 为 true 时，THE Component SHALL 显示按钮
6. WHEN isActive 为 false 时，THE Component SHALL 不显示（返回 null）
7. WHEN 用户点击按钮时，THE Component SHALL 调用 onStart 回调并传递 prompt
8. THE Component SHALL 有三种状态: idle, researching, completed
9. THE Component SHALL 在 researching 状态下禁用按钮防止重复点击
10. THE Component SHALL 显示清晰的图标（如 Sparkles）和文本
11. THE Component SHALL 有适当的样式（Tailwind CSS）
12. THE Component SHALL 支持移动端显示

### Requirement 22: ResearchPanel 组件创建 ⭐ (新增)

**用户故事**: 作为用户，我希望研究 UI 有统一的展示面板，以便获得一致的体验

**设计原因**: ResearchPanel 是 ResearchButton 和 ResearchProgress 的容器组件，负责统一布局、动画和 sticky 定位

#### 验收标准

1. THE System SHALL 创建 ResearchPanel 组件 `components/research-panel.tsx`
2. THE Component SHALL 接受 prompt 属性（研究问题文本）
3. THE Component SHALL 接受 isActive 属性（是否激活研究状态）
4. THE Component SHALL 接受 events 属性（SSE 事件数组）
5. THE Component SHALL 接受 status 属性（研究状态）
6. THE Component SHALL 接受 onStart 回调函数
7. THE Component SHALL 使用 sticky 定位（bottom-[72px]，在聊天输入框上方）
8. WHEN isActive 为 false 时，THE Component SHALL 显示 ResearchButton
9. WHEN isActive 为 true 时，THE Component SHALL 显示 ResearchProgress
10. THE Component SHALL 实现滑入/滑出动画（使用 Framer Motion）
11. THE Component SHALL 有白色背景、圆角、阴影（与聊天消息样式一致）
12. THE Component SHALL 支持响应式布局（移动端/桌面端）
13. THE Component SHALL 防止内容溢出（max-h-[400px] overflow-y-auto）

---

## 非功能需求

### NFR 1: 可维护性

- 代码应遵循 TypeScript 最佳实践
- 所有组件应有清晰的类型定义
- 所有函数应有 JSDoc 注释
- 应使用一致的代码风格

### NFR 2: 可测试性

- 核心功能应有单元测试
- 关键流程应有集成测试
- 应有端到端测试
- 测试覆盖核心功能

### NFR 3: 性能

- 页面加载时间 < 3 秒
- 工具调用响应 < 1 秒
- SSE 连接建立 < 2 秒
- 无明显内存泄漏

### NFR 4: 兼容性

- 支持 Chrome、Safari、Firefox
- 支持桌面和移动端
- 支持不同网络环境
- 与 Phase 2 API 完全兼容

---

## 依赖关系

### 外部依赖

- Next.js 14 (App Router)
- AI SDK
- Drizzle ORM
- React 19
- Phase 2 的 API 接口

### 内部依赖

- Phase 1 (DeepSeek 集成) 必须完成
- Phase 2 (API 标准化) 必须完成

---

## 验收标准总结

Phase 3 完成的标准：

1. ✅ 所有 20 个需求的验收标准都已满足
2. ✅ startResearch 工具正常工作
3. ✅ useResearchProgress Hook 正常工作
4. ✅ API 代理路由正常工作
5. ✅ ResearchProgress 组件正常显示
6. ✅ 聊天流程改造完成
7. ✅ Artifact 集成完成
8. ✅ 数据库 Schema 扩展完成
9. ✅ 错误处理和重连机制完善
10. ✅ 核心功能有测试覆盖
11. ✅ 可以部署到 Vercel
12. ✅ 文档完整

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待实施
