# 🎯 AI 研究助手项目实施路线图

## 项目概述

**目标**: 构建一个基于 Next.js + FastAPI 的智能研究助手平台

**核心价值**:
- 多代理协作的深度研究能力
- 优雅的对话式交互体验
- 实时进度可视化
- 研究报告自动生成

---

## 技术架构

### 前端层 (Next.js)
- React 19 + TypeScript
- 对话式界面
- Artifacts 报告展示
- 实时进度更新

### 后端层 (FastAPI)  
- Python 多代理系统
- aisuite 框架
- 工具调用（Tavily、arXiv、Wikipedia）
- DeepSeek API 集成

### 数据层
- PostgreSQL (Neon)
- 用户数据
- 研究历史
- 报告存储

---

## 四阶段实施计划

### 📍 阶段 1: DeepSeek API 集成（1-2 天）

**目标**: 在现有 FastAPI 系统中集成 DeepSeek，降低成本，验证功能

**核心任务**:

1. **修改模型配置** (5分钟)
```python
# src/agents.py
def research_agent(prompt: str, model: str = "deepseek:deepseek-chat"):
    ...

def writer_agent(prompt: str, model: str = "openai:gpt-4o-mini"):
    # 保持 OpenAI，写作质量好
    ...

def editor_agent(prompt: str, model: str = "deepseek:deepseek-chat"):
    ...
```

2. **配置环境变量** (2分钟)
```bash
DEEPSEEK_API_KEY=sk-your-key
OPENAI_API_KEY=sk-your-key
TAVILY_API_KEY=tvly-your-key
```

3. **测试验证** (30分钟)
- 启动服务测试
- 验证工具调用
- 检查报告质量
- 确认成本降低

**验收标准**:
- ✅ 研究任务正常完成
- ✅ 工具调用正常
- ✅ 报告质量满意
- ✅ 成本降低 44%
- ✅ 前端界面正常

**预计时间**: 1-2 天

---

### 📍 阶段 2: API 接口标准化（3-5 天）

**目标**: 设计面向 Next.js 的标准化 API 接口

**核心任务**:

1. **创建标准化响应格式** (1天)
```python
# main.py
class TaskResponse(BaseModel):
    task_id: str
    status: str
    prompt: str
    steps: List[StepResponse]
    result: Optional[dict]
    created_at: str
    updated_at: str

@app.get("/api/v1/task/{task_id}", response_model=TaskResponse)
def get_task_v1(task_id: str):
    ...
```

2. **添加 SSE 实时推送** (1-2天)
```python
@app.get("/api/v1/task/{task_id}/stream")
async def stream_task_progress(task_id: str):
    async def event_generator():
        while True:
            progress = task_progress.get(task_id)
            yield f"data: {json.dumps(progress)}\n\n"
            await asyncio.sleep(2)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

3. **添加辅助接口** (1天)
- `/api/v1/health` - 健康检查
- `/api/v1/models` - 可用模型列表
- 认证准备接口

**验收标准**:
- ✅ 标准化 API 返回格式
- ✅ SSE 实时推送正常
- ✅ 健康检查可用
- ✅ API 文档更新

**预计时间**: 3-5 天

---

### 📍 阶段 3: Next.js 前端改造（2-3 周）

**目标**: 改造 AI Chatbot 为研究助手，保留优秀交互

**核心任务**:

#### 3.1 功能评估与保留 (1天)

**保留的核心功能**:
- ✅ 聊天界面 → 改为"研究对话"
- ✅ Artifacts 系统 → 展示研究报告
- ✅ 文本编辑器 → 报告查看
- ✅ 代码编辑器 → 代码展示
- ✅ 认证系统
- ✅ 数据库
- ✅ UI 组件库

**删除的功能**:
- ❌ 天气工具
- ❌ 图片编辑器
- ❌ 表格编辑器
- ❌ 多模态输入（暂时）

#### 3.2 创建研究工具 (2-3天)
```typescript
// lib/ai/tools/start-research.ts
export const startResearch = tool({
  description: 'Start comprehensive research',
  inputSchema: z.object({
    topic: z.string(),
  }),
  execute: async ({ topic }) => {
    const res = await fetch(`${RESEARCH_API}/api/v1/research`, {
      method: 'POST',
      body: JSON.stringify({ prompt: topic }),
    });
    return res.json();
  },
});
```

#### 3.3 改造聊天流程 (3-4天)
```typescript
// app/(chat)/api/chat/route.ts
const result = streamText({
  model: myProvider('chat-model'),
  messages,
  tools: {
    createDocument,
    updateDocument,
    startResearch,  // 新增
    getResearchProgress,  // 新增
  },
  system: `你是AI研究助手。当用户要求研究时，
  使用 startResearch 启动任务，然后用 createDocument 
  创建 Artifact 展示报告。`,
});
```

#### 3.4 创建核心组件 (3-4天)
- `ResearchProgress` - 进度展示
- `ResearchReport` - 报告展示
- API 路由代理

#### 3.5 数据库整合 (1-2天)
```typescript
// lib/db/schema.ts
export const researchTask = pgTable('research_task', {
  id: uuid('id').primaryKey(),
  userId: uuid('user_id').references(() => user.id),
  taskId: varchar('task_id'),
  prompt: text('prompt'),
  status: varchar('status'),
  createdAt: timestamp('created_at'),
});
```

**验收标准**:
- ✅ 研究对话界面完成
- ✅ 实时进度显示
- ✅ Artifact 报告展示
- ✅ 用户认证正常
- ✅ 历史记录可查

**预计时间**: 2-3 周

---

### 📍 阶段 4: 整合部署（1-2 周）

**目标**: 合并项目，部署到 Vercel + Render + Neon

**核心任务**:

#### 4.1 项目结构整合 (1天)
```
agentic-ai-public-main/
├── frontend/  (Next.js)
├── backend/   (FastAPI)
├── docker-compose.yml
└── README.md
```

#### 4.2 本地联调测试 (2-3天)
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
  backend:
    build: ./backend
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
```

#### 4.3 部署到云端 (2-3天)

**Neon 数据库** (10分钟):
- 创建项目
- 获取连接字符串
- 运行迁移

**Render 后端** (30分钟):
- 连接 GitHub
- 配置环境变量
- 自动部署

**Vercel 前端** (10分钟):
```bash
cd frontend
vercel
vercel env add DATABASE_URL
vercel env add RESEARCH_API_URL
```

#### 4.4 配置防休眠 (10分钟)
- 使用 cron-job.org
- 每 10 分钟 ping 一次
- URL: `/api/v1/health`

#### 4.5 端到端测试 (1天)
- 用户注册/登录
- 提交研究任务
- 实时进度更新
- 报告生成
- 性能测试

**验收标准**:
- ✅ 生产环境可访问
- ✅ 所有功能正常
- ✅ 性能满足要求
- ✅ 成本在预算内

**预计时间**: 1-2 周

---

## 📊 总体时间表

| 阶段 | 任务 | 时间 | 累计 |
|------|------|------|------|
| 1 | DeepSeek 集成 | 1-2 天 | 1-2 天 |
| 2 | API 标准化 | 3-5 天 | 4-7 天 |
| 3 | Next.js 改造 | 2-3 周 | 3-4 周 |
| 4 | 整合部署 | 1-2 周 | 4-6 周 |

**总计**: 4-6 周（1人）或 2-3 周（2人并行）

---

## 🎯 关键里程碑

### Milestone 1: DeepSeek 可用 (Week 1)
- ✅ DeepSeek API 集成
- ✅ 本地测试通过
- ✅ 成本降低验证

### Milestone 2: API 就绪 (Week 2)
- ✅ 标准化 API 完成
- ✅ SSE 实时推送
- ✅ 文档更新

### Milestone 3: 前端完成 (Week 4-5)
- ✅ 研究界面开发
- ✅ 组件库完成
- ✅ 本地联调成功

### Milestone 4: 生产上线 (Week 6)
- ✅ 部署到云端
- ✅ 端到端测试
- ✅ 正式发布

---

## 💰 成本分析

### 开发成本
- **时间**: 4-6 周
- **人力**: 1-2 人
- **总成本**: $20,000 - $40,000

### 运营成本（月）
- Vercel: $0
- Render: $0（免费层）
- Neon: $0（免费层）
- DeepSeek API: $42
- OpenAI API: $20
- Tavily API: $10
- **总计**: $72/月

### 成本节省
- 使用 DeepSeek 节省 44%
- 免费部署平台
- 年度成本: $864

---

## 🎨 用户体验流程

### 完整交互流程

```
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
5. 研究完成后，AI："研究完成！让我为你创建报告..."
   [AI 调用 createDocument 工具]
    ↓
6. 右侧 Artifact 区域显示完整报告
   用户可以：
   - 阅读报告
   - 复制内容
   - 导出 PDF
   - 继续提问
    ↓
7. 用户追问："能加上成本分析吗？"
    ↓
8. AI 调用 updateDocument 更新报告
```

---

## 🔧 技术决策

### 为什么保留聊天界面？
- ✅ 对话式交互更自然
- ✅ 可以追问和补充
- ✅ 思考过程可视化
- ✅ 历史记录管理

### 为什么保留 Artifacts？
- ✅ 完美的报告展示方式
- ✅ 实时生成和编辑
- ✅ 支持多种格式
- ✅ 用户体验极佳

### 为什么使用 DeepSeek？
- ✅ 成本降低 44%
- ✅ 中文能力更强
- ✅ 推理能力优秀
- ✅ 完全兼容 aisuite

### 为什么选择 Vercel + Render？
- ✅ 完全免费
- ✅ 自动部署
- ✅ 零配置
- ✅ 全球 CDN

---

## 📋 检查清单

### 阶段 1 完成标准
- [ ] DeepSeek API 配置完成
- [ ] 环境变量设置正确
- [ ] 研究任务测试通过
- [ ] 工具调用正常
- [ ] 成本降低验证

### 阶段 2 完成标准
- [ ] 标准化 API 实现
- [ ] SSE 推送正常
- [ ] 健康检查可用
- [ ] API 文档更新
- [ ] 本地测试通过

### 阶段 3 完成标准
- [ ] 研究工具创建
- [ ] 聊天流程改造
- [ ] 核心组件完成
- [ ] 数据库整合
- [ ] 本地联调成功

### 阶段 4 完成标准
- [ ] 项目结构整合
- [ ] 数据库部署
- [ ] 后端部署
- [ ] 前端部署
- [ ] 防休眠配置
- [ ] 端到端测试
- [ ] 生产环境验证

---

## 💡 关键建议

1. **渐进式开发**: 每个阶段独立验收，不要跳步
2. **保持简单**: 删除不需要的功能，专注核心
3. **频繁测试**: 每天测试，及时发现问题
4. **文档同步**: 边开发边更新文档
5. **成本监控**: 每周检查 API 调用成本
6. **用户反馈**: 尽早获取用户反馈
7. **性能优化**: 关注响应时间和用户体验

---

## 🚀 下一步行动

### 立即开始（本周）
1. ✅ 配置 DeepSeek API Key
2. ✅ 修改模型配置
3. ✅ 本地测试验证
4. ✅ 确认成本降低

### 短期目标（2周内）
1. ✅ 完成 API 标准化
2. ✅ 实现 SSE 推送
3. ✅ 开始前端改造

### 中期目标（1月内）
1. ✅ 完成前端开发
2. ✅ 本地联调成功
3. ✅ 准备部署

### 长期目标（2月内）
1. ✅ 生产环境上线
2. ✅ 用户测试反馈
3. ✅ 持续优化迭代

---

**创建日期**: 2025-01-XX  
**版本**: 1.0  
**状态**: ✅ 已完成  
**维护者**: AI Research Team
