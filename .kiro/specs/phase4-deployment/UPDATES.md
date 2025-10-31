# Phase 4 部署阶段 - 更新说明

## 文档信息

- **更新日期**: 2025-10-31
- **版本**: 1.1
- **更新原因**: 适配 Phase 3 新架构（用户触发式研究）
- **影响范围**: 测试用例和端到端测试场景

---

## 更新摘要

Phase 4 的测试相关文档已更新，以匹配 Phase 3 中的重大架构调整。Phase 3 从 **AI SDK 工具调用模式** 改为 **用户触发式研究模式**，这要求 Phase 4 的所有测试用例都需要相应更新。

---

## 主要架构变更回顾

### Phase 3 旧架构 (已废弃)
```
用户输入 → AI 调用 startResearch 工具 → 返回 taskId
  → Hook 订阅 GET /api/research/stream?taskId=xxx
  → 显示进度 → 报告生成
```

### Phase 3 新架构 (当前)
```
用户看到 AI 消息包含研究关键词 → ResearchButton 显示（sticky 定位）
  → 用户点击按钮 → useResearchProgress Hook 直接 POST SSE
  → 显示进度 → onComplete 回调 → sendMessage 发送报告给 AI
  → AI 调用 createDocument → Artifact 显示
```

---

## 文件更新详情

### 1. tasks.md 更新

#### 新增任务

**任务 10.2.5: 编写 ResearchPanel 组件测试** (Phase 3 新增)
- 测试 sticky 定位（bottom-[72px]）
- 测试 isActive 状态切换
- 测试 Framer Motion 动画
- 测试响应式布局
- **预计时间**: 1.5 小时

**任务 10.2.6: 编写辅助函数测试** (Phase 3 新增)
- 测试 detectResearchKeywords 函数（中英文关键词）
- 测试 extractResearchQuery 函数（提取研究主题）
- 测试 validateResearchQuery 函数（验证查询有效性）
- **预计时间**: 1 小时

#### 更新的任务

**任务 10.3: 编写研究任务测试** (已更新)

**旧内容**:
```markdown
- 测试发起研究任务
- 测试 AI 调用 startResearch 工具  ❌
- 测试 taskId 返回  ❌
```

**新内容**:
```markdown
- 测试与 AI 对话，让 AI 回复包含研究关键词
- 测试 ResearchButton 在聊天输入框上方显示（sticky 定位）
- 测试用户点击 ResearchButton 按钮
- 测试 useResearchProgress Hook 直接发起 POST SSE 连接
- 测试 SSE 事件接收（start, plan, progress, done）
- 验证研究 prompt 正确传递
```

**任务 10.4: 编写进度显示测试** (已更新)

**新内容新增**:
```markdown
- 测试 ResearchPanel 组件在 Chat 组件中正确渲染
- 测试 ResearchProgress 组件在 ResearchPanel 中显示
- 测试 SSE 连接建立（通过 fetch-event-source 库，支持 POST）
- 测试进度事件接收并更新 events 数组
- 测试 status 状态变化（idle → researching → completed/failed）
- 测试 Framer Motion 动画
```

**任务 10.5: 编写报告生成测试** (已更新)

**新内容新增**:
```markdown
- 测试接收 done 事件（包含完整报告）
- 测试 onComplete 回调被正确触发
- 测试 sendMessage 函数将报告发送给 AI
- 测试 AI 收到报告后调用 createDocument 工具
- 测试 ResearchPanel 在研究完成后正确关闭
```

#### 时间估算更新

| 项目 | 旧估算 | 新估算 | 变化 |
|------|--------|--------|------|
| 任务 10.3 | 2 小时 | 2.5 小时 | +0.5h |
| 任务 10.4 | 2 小时 | 2.5 小时 | +0.5h |
| 任务 10.5 | 2 小时 | 2.5 小时 | +0.5h |
| 任务 10.2.5 | - | 1.5 小时 | +1.5h (新增) |
| 任务 10.2.6 | - | 1 小时 | +1h (新增) |
| **Week 2 总计** | 48 小时 | 52 小时 | +4h |
| **总计** | 96 小时 | 100 小时 | +4h |
| **总任务数** | 60 个 | 62 个 | +2 个 |

---

### 2. design.md 更新

#### 端到端测试场景更新

**场景 2: AI 建议研究** (已更新)

**旧内容**:
```markdown
2. **发起研究任务**
   - 输入研究主题
   - AI 调用 startResearch 工具  ❌
   - 返回 taskId  ❌
```

**新内容**:
```markdown
2. **AI 建议研究** ⚠️ (已更新以匹配 Phase 3 新架构)
   - 与 AI 对话（如 "Tell me about quantum computing"）
   - AI 回复包含研究关键词（如 "I can research quantum computing for you"）
   - ResearchButton 在聊天输入框上方显示（sticky 定位在 bottom-[72px]）
   - 验证关键词检测逻辑（detectResearchKeywords 函数）
```

**场景 3: 用户发起研究** (新增)

```markdown
3. **用户发起研究** ⚠️ (已更新)
   - 用户点击 ResearchButton
   - useResearchProgress Hook 发起 POST SSE 连接
   - 验证 API 路由代理 (/api/research/stream)
   - 验证 prompt 正确传递到后端
```

**场景 4: 实时进度显示** (已更新)

**新增内容**:
```markdown
- ResearchProgress 组件在 ResearchPanel 中显示
- events 数组实时更新
- 验证进度信息正确渲染（根据 events 动态显示步骤）
- 验证 status 状态变化（idle → researching → completed）
```

**场景 5: 报告生成** (已更新)

**新增内容**:
```markdown
- 接收 done 事件（包含完整报告）
- onComplete 回调被触发
- sendMessage 将报告发送给 AI（格式: "Research completed:\n\n{report}"）
- AI 收到报告后调用 createDocument 工具
- ResearchPanel 自动关闭
```

**场景 9: 断线重连** (已更新)

**新增内容**:
```markdown
- 验证 fetch-event-source 自动重连（指数退避: 500ms, 1s, 2s）
- 验证最大重试次数限制（3 次）
```

#### E2E 测试脚本更新

**完整测试流程已重写**，从 9 个步骤增加到 14 个步骤，包含：

1. 访问首页
2. 登录
3. **与 AI 对话，让 AI 建议研究** (新)
4. **等待 AI 响应（包含研究关键词）** (新)
5. **验证 ResearchButton 显示** (新)
6. **点击 ResearchButton 发起研究** (更新)
7. **验证 ResearchPanel 切换到 ResearchProgress** (新)
8. **验证进度更新（检查 events 数组渲染）** (更新)
9. **等待研究完成（status 变为 completed）** (更新)
10. **验证 ResearchPanel 关闭** (新)
11. **验证 Artifact 自动创建** (更新)
12. 验证报告内容
13. 追问更新报告
14. 验证报告更新

---

## Phase 3 新增组件测试覆盖

### 1. ResearchPanel 组件
- **组件位置**: `components/research-panel.tsx`
- **测试位置**: 任务 10.2.5
- **测试内容**:
  - Sticky 定位验证
  - isActive 状态切换
  - Framer Motion 动画
  - 响应式布局
  - 最大高度和滚动

### 2. ResearchButton 组件
- **组件位置**: `components/research-button.tsx`
- **测试位置**: 任务 10.3（作为研究任务测试的一部分）
- **测试内容**:
  - 按钮显示条件（检测到研究关键词）
  - 点击事件处理
  - 禁用状态
  - Sticky 定位

### 3. ResearchProgress 组件
- **组件位置**: `components/research-progress.tsx`
- **测试位置**: 任务 10.4
- **测试内容**:
  - Props 接收（events + status）
  - 进度步骤渲染
  - 状态图标显示
  - 动画效果

### 4. 辅助函数
- **文件位置**: `lib/research-utils.ts`
- **测试位置**: 任务 10.2.6
- **测试内容**:
  - detectResearchKeywords（中英文关键词检测）
  - extractResearchQuery（提取研究主题）
  - validateResearchQuery（验证查询有效性）

### 5. useResearchProgress Hook
- **文件位置**: `hooks/use-research-progress.ts`
- **测试位置**: 任务 10.3, 10.4, 10.5
- **测试内容**:
  - POST SSE 连接（使用 fetch-event-source）
  - 事件接收和状态更新
  - onComplete 回调
  - 重连机制
  - AbortController 清理

---

## 关键 API 变更

### 1. useResearchProgress Hook

**旧接口**:
```typescript
interface UseResearchProgressProps {
  taskId: string | null;  // ❌ 已废弃
}
```

**新接口**:
```typescript
interface UseResearchProgressProps {
  prompt: string | null;  // ✅ 直接接受研究问题
  onComplete?: (report: string) => void;  // ✅ 完成回调
}
```

### 2. ResearchProgress 组件

**旧 Props**:
```typescript
interface ResearchProgressProps {
  taskId: string | null;  // ❌ 已废弃
}
```

**新 Props**:
```typescript
interface ResearchProgressProps {
  events: ProgressEvent[];  // ✅ SSE 事件数组
  status: ResearchStatus;  // ✅ 研究状态
}
```

### 3. 组件集成位置

**旧位置**: Message 组件（components/message.tsx）❌

**新位置**: Chat 组件（components/chat.tsx）✅
- 原因: Messages 组件不接收 sendMessage prop
- 优点: 数据流更清晰，支持 sticky 定位

### 4. SSE 连接方式

**旧方式**:
```typescript
// GET /api/research/stream?taskId=xxx
const eventSource = new EventSource(`/api/research/stream?taskId=${taskId}`);
```

**新方式**:
```typescript
// POST /api/research/stream (使用 fetch-event-source)
await fetchEventSource('/api/research/stream', {
  method: 'POST',
  body: JSON.stringify({ prompt }),
  // ...
});
```

---

## 验证清单

在执行 Phase 4 之前，请确认以下内容：

### Phase 3 实现验证
- [ ] ResearchPanel 组件已实现并使用 sticky 定位
- [ ] ResearchButton 组件已实现
- [ ] ResearchProgress 组件接受 events + status Props
- [ ] useResearchProgress Hook 接受 prompt + onComplete
- [ ] lib/research-utils.ts 已创建并包含三个辅助函数
- [ ] Chat 组件已集成 ResearchPanel
- [ ] 使用 sendMessage 而非 appendMessage
- [ ] 使用 fetch-event-source 进行 POST SSE 连接

### Phase 4 测试准备
- [ ] 已安装 Playwright (`npm i -D @playwright/test`)
- [ ] 已安装 fetch-event-source (`npm i @microsoft/fetch-event-source`)
- [ ] 测试用例已更新以匹配新架构
- [ ] 测试环境变量已配置
- [ ] 测试数据 testid 属性已添加到组件

---

## 后续行动

### 立即行动
1. ✅ 审阅 Phase 4 更新内容
2. ✅ 确认 Phase 3 设计与 Phase 4 测试一致
3. ⏳ 开始执行 Phase 3 实现（108 小时 / 3 周）

### Phase 3 完成后
1. 执行 Phase 4 Week 1: 准备与配置（32 小时）
2. 执行 Phase 4 Week 2: 部署与测试（52 小时，含新增测试）
3. 执行 Phase 4 Week 3: 完善和文档（16 小时）

---

## 相关文档

- **Phase 3 Requirements**: `/Users/ameureka/Desktop/agentic-ai-public-main/.kiro/specs/phase3-nextjs-frontend/requirements.md`
- **Phase 3 Design**: `/Users/ameureka/Desktop/agentic-ai-public-main/.kiro/specs/phase3-nextjs-frontend/design.md`
- **Phase 3 Tasks**: `/Users/ameureka/Desktop/agentic-ai-public-main/.kiro/specs/phase3-nextjs-frontend/tasks.md`
- **Phase 3 UI Design Report**: `/Users/ameureka/Desktop/agentic-ai-public-main/.kiro/specs/phase3-nextjs-frontend/UI_DESIGN_REPORT.md`
- **Phase 4 Requirements**: `/Users/ameureka/Desktop/agentic-ai-public-main/.kiro/specs/phase4-deployment/requirements.md`
- **Phase 4 Design**: `/Users/ameureka/Desktop/agentic-ai-public-main/.kiro/specs/phase4-deployment/design.md`
- **Phase 4 Tasks**: `/Users/ameureka/Desktop/agentic-ai-public-main/.kiro/specs/phase4-deployment/tasks.md`

---

**更新版本**: 1.1
**最后更新**: 2025-10-31
**状态**: 已完成
