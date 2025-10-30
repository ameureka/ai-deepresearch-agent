# Phase 3: Next.js 前端改造 - 任务清单

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 3 - Next.js 前端改造
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **预计时间**: 3 周（120 小时）
- **状态**: 待执行
- **依赖**: Phase 1 + Phase 2 必须完成

---

## 任务概览

本阶段包含 **80+ 个任务**，分为 **3 周**：

**Week 1: 架构与工具桥接** (40 小时)
**Week 2: 聊天流程与组件** (40 小时)
**Week 3: 数据库与完善** (40 小时)

**标记说明**:
- `[ ]` 未完成
- `[x]` 已完成
- `*` 可选任务（仅文档编写）

---

## Week 1: 架构与工具桥接（40 小时）

### Day 1: 环境准备与工具创建（8 小时）

#### - [ ] 1.1 配置环境变量
- 在 `ai-chatbot-main` 目录创建 `.env.local` 文件
- 添加 `RESEARCH_API_URL=http://localhost:8000`
- 添加其他必需的环境变量（DATABASE_URL, AUTH_SECRET）
- 更新 `.env.example` 文件添加 RESEARCH_API_URL 说明
- 验证环境变量加载
- _需求: Requirement 11_
- _预计时间: 30 分钟_

#### - [ ] 1.2 创建 startResearch 工具文件
- 创建目录 `lib/ai/tools/`
- 创建文件 `lib/ai/tools/start-research.ts`
- 添加文件头部注释和导入
- 定义工具的基本结构
- 添加 TypeScript 类型定义
- _需求: Requirement 1_
- _预计时间: 30 分钟_

#### - [ ] 1.3 实现 startResearch 工具的 inputSchema
- 使用 zod 定义 inputSchema
- 定义 topic 字段（字符串类型，必需）
- 添加字段描述
- 添加验证规则
- 测试 schema 验证
- _需求: Requirement 1_
- _预计时间: 30 分钟_

#### - [ ] 1.4 实现 startResearch 工具的 execute 函数
- 实现 async execute 函数
- 从环境变量读取 RESEARCH_API_URL
- 验证 RESEARCH_API_URL 存在
- 构建 API 请求 URL
- 添加基础错误处理
- _需求: Requirement 1_
- _预计时间: 45 分钟_

#### - [ ] 1.5 实现 API 请求逻辑
- 使用 fetch 发送 POST 请求
- 设置请求头
- 构建请求体
- 处理响应状态码
- 添加超时处理
- _需求: Requirement 1_
- _预计时间: 1 小时_

#### - [ ] 1.6 实现 taskId 提取逻辑
- 获取响应 body 的 ReadableStream
- 使用 getReader() 读取首个数据块
- 使用 TextDecoder 解码数据
- 解析 SSE 格式提取首个事件
- 从事件数据中提取 taskId
- 如果没有 taskId，生成 UUID
- _需求: Requirement 1_
- _预计时间: 1.5 小时_

#### - [ ] 1.7 实现成功响应格式
- 返回对象包含 taskId 字段
- 返回对象包含 status: 'started'
- 返回对象包含 message 字段
- 添加 TypeScript 返回类型定义
- 验证返回格式符合规范
- _需求: Requirement 1_
- _预计时间: 30 分钟_

#### - [ ] 1.8 实现错误处理
- 捕获 fetch 错误
- 捕获 JSON 解析错误
- 捕获网络错误
- 返回错误格式
- 记录错误到控制台
- _需求: Requirement 1_
- _预计时间: 45 分钟_

#### - [ ] 1.9 实现 UUID 生成函数
- 创建 generateUUID() 辅助函数
- 使用 crypto.randomUUID()
- 添加类型定义
- 测试 UUID 生成
- _需求: Requirement 1_
- _预计时间: 15 分钟_

#### - [ ] 1.10 添加工具文档和类型
- 添加 JSDoc 注释
- 添加使用示例注释
- 导出工具
- 添加完整的 TypeScript 类型
- 验证类型检查通过
- _需求: Requirement 1_
- _预计时间: 30 分钟_

#### - [ ] 1.11 测试 startResearch 工具
- 创建测试文件
- 测试成功调用场景
- 测试 API 失败场景
- 测试网络错误场景
- 测试 taskId 生成
- 验证所有测试通过
- _需求: Requirement 1, 17_
- _预计时间: 1.5 小时_


### Day 2: API 代理路由（8 小时）

#### - [ ] 2.1 创建 API 路由目录结构
- 创建目录 `app/api/research/stream/`
- 创建文件 `app/api/research/stream/route.ts`
- 添加文件头部注释
- 设置 runtime 配置: `export const runtime = 'nodejs'`
- _需求: Requirement 3_
- _预计时间: 15 分钟_

#### - [ ] 2.2 实现 POST 方法处理器（框架）
- 定义 async POST 函数
- 接受 NextRequest 参数
- 添加 try-catch 错误处理
- 返回基础响应
- 添加类型定义
- _需求: Requirement 3_
- _预计时间: 30 分钟_

#### - [ ] 2.3 实现请求体解析
- 使用 request.json() 解析请求体
- 提取 prompt 字段
- 验证 prompt 存在
- 验证 prompt 非空
- 返回 400 错误（如果验证失败）
- _需求: Requirement 3_
- _预计时间: 30 分钟_

#### - [ ] 2.4 实现环境变量读取和验证
- 从 process.env 读取 RESEARCH_API_URL
- 验证 RESEARCH_API_URL 存在
- 返回 500 错误（如果未配置）
- 添加清晰的错误消息
- _需求: Requirement 3_
- _预计时间: 20 分钟_

#### - [ ] 2.5 实现后端 API 代理请求
- 构建完整的后端 API URL
- 使用 fetch 发送 POST 请求
- 设置请求头: Content-Type: application/json
- 传递请求体: {prompt}
- 处理请求超时
- _需求: Requirement 3_
- _预计时间: 45 分钟_

#### - [ ] 2.6 实现响应状态检查
- 检查 response.ok
- 如果失败，读取错误信息
- 返回对应的错误状态码
- 返回 JSON 错误响应
- 记录错误到控制台
- _需求: Requirement 3_
- _预计时间: 30 分钟_

#### - [ ] 2.7 实现 SSE 流代理
- 获取 response.body (ReadableStream)
- 创建新的 Response 对象
- 设置 body 为 response.body
- 不修改流内容（直接代理）
- _需求: Requirement 3_
- _预计时间: 30 分钟_

#### - [ ] 2.8 配置 SSE 响应头
- 设置 Content-Type: text/event-stream
- 设置 Cache-Control: no-cache, no-transform
- 设置 Connection: keep-alive
- 设置 X-Accel-Buffering: no
- 验证响应头正确
- _需求: Requirement 3_
- _预计时间: 30 分钟_

#### - [ ] 2.9 实现 GET 方法处理器
- 定义 async GET 函数
- 解析 URL 查询参数（taskId, prompt）
- 验证参数存在
- 调用 POST 处理器或实现独立逻辑
- _需求: Requirement 3_
- _预计时间: 45 分钟_

#### - [ ] 2.10 实现全局错误处理
- 捕获所有未处理的异常
- 返回 500 状态码
- 返回 JSON 错误响应
- 记录详细错误到控制台
- 不暴露敏感信息
- _需求: Requirement 3_
- _预计时间: 30 分钟_

#### - [ ] 2.11 添加请求日志
- 记录请求方法和 URL
- 记录请求参数（prompt）
- 记录响应状态
- 使用 console.log
- _需求: Requirement 3_
- _预计时间: 20 分钟_

#### - [ ] 2.12 测试 API 代理路由
- 启动 Next.js 开发服务器
- 使用 curl 测试 POST 请求
- 使用 curl 测试 GET 请求
- 验证 SSE 流正常
- 测试错误场景
- _需求: Requirement 3_
- _预计时间: 1.5 小时_

#### - [ ] 2.13 编写 API 路由集成测试
- 创建测试文件
- 测试 POST 请求成功场景
- 测试 GET 请求成功场景
- 测试验证错误场景
- 测试后端 API 失败场景
- 验证所有测试通过
- _需求: Requirement 3, 17_
- _预计时间: 2 小时_

### Day 3-4: useResearchProgress Hook（16 小时）

#### - [ ] 3.1 创建 Hook 文件
- 创建目录 `hooks/`
- 创建文件 `hooks/use-research-progress.ts`
- 添加文件头部注释
- 导入必需的 React hooks
- 定义基本结构
- _需求: Requirement 2_
- _预计时间: 20 分钟_

#### - [ ] 3.2 定义 TypeScript 类型
- 定义 ProgressEvent 类型
- 定义 ResearchStatus 类型
- 定义 Hook 返回类型
- 添加 JSDoc 注释
- _需求: Requirement 2_
- _预计时间: 30 分钟_

#### - [ ] 3.3 实现状态管理
- 使用 useState 定义 events 状态
- 使用 useState 定义 status 状态
- 使用 useState 定义 report 状态
- 使用 useState 定义 error 状态
- 初始化所有状态
- _需求: Requirement 2_
- _预计时间: 30 分钟_

#### - [ ] 3.4 实现 useEffect Hook 框架
- 创建 useEffect，依赖 taskId
- 添加 early return（taskId 为 null）
- 定义清理函数
- _需求: Requirement 2_
- _预计时间: 20 分钟_

#### - [ ] 3.5 实现重连状态管理
- 定义 retries 变量
- 定义 MAX_RETRIES 常量（3）
- 定义 eventSource 变量
- _需求: Requirement 2, 10_
- _预计时间: 15 分钟_

#### - [ ] 3.6 实现 connect 函数框架
- 定义 connect 函数
- 构建 SSE URL（/api/research/stream?taskId=xxx）
- 创建 EventSource 实例
- _需求: Requirement 2_
- _预计时间: 30 分钟_

#### - [ ] 3.7 实现 onopen 事件处理
- 定义 eventSource.onopen 处理器
- 记录连接成功日志
- 设置 status 为 'running'
- 重置 retries 计数
- _需求: Requirement 2_
- _预计时间: 20 分钟_

#### - [ ] 3.8 实现 onmessage 事件处理框架
- 定义 eventSource.onmessage 处理器
- 添加 try-catch 错误处理
- 解析事件数据（JSON.parse）
- 添加事件到 events 列表
- _需求: Requirement 2_
- _预计时间: 30 分钟_

#### - [ ] 3.9 实现 start 事件处理
- 检测 event.type === 'start'
- 设置 status 为 'running'
- 记录日志
- _需求: Requirement 2_
- _预计时间: 15 分钟_

#### - [ ] 3.10 实现 plan 事件处理
- 检测 event.type === 'plan'
- 提取 steps 数据
- 可选：保存 steps 到状态
- 记录日志
- _需求: Requirement 2_
- _预计时间: 20 分钟_

#### - [ ] 3.11 实现 progress 事件处理
- 检测 event.type === 'progress'
- 提取 step, total, message 数据
- 可选：更新进度百分比
- 记录日志
- _需求: Requirement 2_
- _预计时间: 20 分钟_

#### - [ ] 3.12 实现 done 事件处理
- 检测 event.type === 'done'
- 设置 status 为 'completed'
- 提取并保存 report
- 关闭 EventSource 连接
- 记录日志
- _需求: Requirement 2_
- _预计时间: 30 分钟_

#### - [ ] 3.13 实现 error 事件处理
- 检测 event.type === 'error'
- 设置 status 为 'failed'
- 提取并保存 error 消息
- 关闭 EventSource 连接
- 记录日志
- _需求: Requirement 2_
- _预计时间: 30 分钟_

#### - [ ] 3.14 实现 onerror 事件处理框架
- 定义 eventSource.onerror 处理器
- 记录错误日志
- 关闭当前连接
- _需求: Requirement 2, 10_
- _预计时间: 20 分钟_

#### - [ ] 3.15 实现重连逻辑
- 检查 retries < MAX_RETRIES
- 增加 retries 计数
- 计算延迟时间（指数退避）
- 使用 setTimeout 延迟重连
- 调用 connect 函数
- _需求: Requirement 10_
- _预计时间: 45 分钟_

#### - [ ] 3.16 实现最大重试处理
- 检查 retries >= MAX_RETRIES
- 设置 status 为 'failed'
- 设置 error 消息
- 记录日志
- _需求: Requirement 10_
- _预计时间: 20 分钟_

#### - [ ] 3.17 实现指数退避策略
- 计算延迟: 500 * Math.pow(2, retries - 1)
- 第 1 次: 500ms
- 第 2 次: 1000ms
- 第 3 次: 2000ms
- 记录重连尝试日志
- _需求: Requirement 10_
- _预计时间: 30 分钟_

#### - [ ] 3.18 实现清理函数
- 在 useEffect 返回清理函数
- 关闭 EventSource 连接
- 重置 status 为 'idle'
- 清理定时器（如果有）
- _需求: Requirement 2_
- _预计时间: 30 分钟_

#### - [ ] 3.19 实现 Hook 返回值
- 返回对象包含 events
- 返回对象包含 status
- 返回对象包含 report
- 返回对象包含 error
- 添加返回类型定义
- _需求: Requirement 2_
- _预计时间: 15 分钟_

#### - [ ] 3.20 优化性能
- 使用 useCallback 优化 connect 函数（可选）
- 使用 useMemo 缓存计算结果（可选）
- 避免不必要的重渲染
- _需求: Requirement 13_
- _预计时间: 45 分钟_

#### - [ ] 3.21 添加 Hook 文档
- 添加 JSDoc 注释
- 添加使用示例
- 添加参数说明
- 添加返回值说明
- _需求: Requirement 2_
- _预计时间: 30 分钟_

#### - [ ] 3.22 编写 Hook 单元测试
- 创建测试文件
- 测试基础功能
- 测试事件处理
- 测试重连逻辑
- 测试清理函数
- 使用 @testing-library/react-hooks
- _需求: Requirement 2, 17_
- _预计时间: 3 小时_

#### - [ ] 3.23 测试 Hook 在组件中的使用
- 创建测试组件
- 测试 Hook 返回值
- 测试状态更新
- 测试错误处理
- 验证所有测试通过
- _需求: Requirement 2, 17_
- _预计时间: 2 小时_

### Day 5: Week 1 集成测试（8 小时）

#### - [ ] 4.1 创建集成测试环境
- 启动 FastAPI 后端（Phase 2）
- 启动 Next.js 前端
- 验证两者可以通信
- _需求: All Week 1 Requirements_
- _预计时间: 30 分钟_

#### - [ ] 4.2 测试完整工具调用流程
- 在测试环境中调用 startResearch 工具
- 验证返回 taskId
- 验证 API 请求成功
- 验证错误处理
- _需求: Requirement 1, 3_
- _预计时间: 1 小时_

#### - [ ] 4.3 测试 SSE 连接建立
- 使用 useResearchProgress Hook
- 验证 EventSource 连接建立
- 验证 onopen 事件触发
- 验证状态更新
- _需求: Requirement 2, 3_
- _预计时间: 1 小时_

#### - [ ] 4.4 测试事件接收
- 发起研究任务
- 验证接收 start 事件
- 验证接收 plan 事件
- 验证接收 progress 事件
- 验证接收 done 事件
- _需求: Requirement 2_
- _预计时间: 1.5 小时_

#### - [ ] 4.5 测试重连机制
- 模拟连接中断
- 验证自动重连
- 验证指数退避
- 验证最大重试次数
- _需求: Requirement 10_
- _预计时间: 1.5 小时_

#### - [ ] 4.6 测试错误场景
- 测试后端 API 不可用
- 测试网络错误
- 测试超时
- 验证错误处理正确
- _需求: Requirement 9_
- _预计时间: 1 小时_

#### - [ ] 4.7 性能测试
- 测试工具调用响应时间 < 1s
- 测试 SSE 连接建立 < 2s
- 测试内存使用
- 验证无内存泄漏
- _需求: Requirement 13_
- _预计时间: 1 小时_

#### - [ ] 4.8 生成 Week 1 测试报告
- 汇总所有测试结果
- 记录通过/失败的测试
- 记录性能指标
- 创建测试报告文档
- _需求: All Week 1 Requirements_
- _预计时间: 30 分钟_


---

## Week 2: 聊天流程与组件（40 小时）

### Day 6-7: 聊天流程改造（16 小时）

#### - [ ] 5.1 备份现有聊天代码
- 备份 `app/(chat)/api/chat/route.ts`
- 创建 git 分支
- 记录当前功能状态
- _需求: Requirement 5_
- _预计时间: 15 分钟_

#### - [ ] 5.2 导入 startResearch 工具
- 在 chat route 中导入 startResearch
- 验证导入路径正确
- 验证类型定义正确
- _需求: Requirement 5_
- _预计时间: 10 分钟_

#### - [ ] 5.3 集成 startResearch 到 tools 对象
- 找到 streamText 的 tools 配置
- 添加 startResearch 到 tools 对象
- 保持现有工具（createDocument, updateDocument）
- 验证工具注册成功
- _需求: Requirement 5_
- _预计时间: 20 分钟_

#### - [ ] 5.4 更新 System Prompt（准备）
- 找到 System Prompt 配置位置
- 备份现有 System Prompt
- 准备研究相关的提示词
- _需求: Requirement 6_
- _预计时间: 30 分钟_

#### - [ ] 5.5 编写研究工具使用说明
- 编写何时使用 startResearch 的说明
- 编写工具调用顺序说明
- 编写追问处理说明
- 添加示例对话流程
- _需求: Requirement 6_
- _预计时间: 1 小时_

#### - [ ] 5.6 更新 System Prompt 文件
- 打开 `lib/ai/prompts.ts`
- 添加 researchPrompt 常量
- 集成到 systemPrompt 函数
- 验证 Prompt 格式正确
- _需求: Requirement 6_
- _预计时间: 45 分钟_

#### - [ ] 5.7 测试 AI 工具调用
- 启动开发服务器
- 在聊天中输入研究请求
- 验证 AI 调用 startResearch 工具
- 验证工具返回 taskId
- 记录测试结果
- _需求: Requirement 5_
- _预计时间: 1 小时_

#### - [ ] 5.8 优化 System Prompt
- 根据测试结果调整 Prompt
- 确保 AI 按预期行为
- 避免 AI 自由发挥
- 测试多个场景
- _需求: Requirement 6_
- _预计时间: 1.5 小时_

#### - [ ] 5.9 实现 taskId 传递机制
- 从工具返回值中提取 taskId
- 将 taskId 传递给前端组件
- 使用 dataStream 或其他机制
- 验证 taskId 正确传递
- _需求: Requirement 5_
- _预计时间: 2 小时_

#### - [ ] 5.10 处理工具调用失败
- 捕获 startResearch 失败
- 向用户显示友好错误消息
- 记录错误日志
- 允许用户重试
- _需求: Requirement 9_
- _预计时间: 1 hour_

#### - [ ] 5.11 实现研究完成后的文档创建
- 监听研究完成事件
- 自动调用 createDocument 工具
- 传递研究报告内容
- 设置文档类型为 "text"
- 设置文档标题
- _需求: Requirement 8_
- _预计时间: 2 小时_

#### - [ ] 5.12 实现追问处理
- 检测用户追问
- 调用 updateDocument 工具
- 更新现有报告
- 保持版本历史
- _需求: Requirement 8_
- _预计时间: 1.5 小时_

#### - [ ] 5.13 测试完整聊天流程
- 测试发起研究
- 测试查看进度
- 测试报告生成
- 测试追问更新
- 测试错误处理
- _需求: Requirement 5, 8_
- _预计时间: 2 小时_

#### - [ ] 5.14 优化用户体验
- 添加加载状态提示
- 优化错误消息
- 改进进度显示
- 测试用户流程
- _需求: Requirement 14_
- _预计时间: 1.5 小时_

### Day 8: ResearchProgress 组件（8 小时）

#### - [ ] 6.1 创建组件文件
- 创建目录 `components/`
- 创建文件 `components/research-progress.tsx`
- 添加 'use client' 指令
- 添加文件头部注释
- _需求: Requirement 4_
- _预计时间: 15 分钟_

#### - [ ] 6.2 定义组件 Props
- 定义 Props 接口
- 添加 taskId 属性（string | null）
- 添加 TypeScript 类型
- 添加 JSDoc 注释
- _需求: Requirement 4_
- _预计时间: 15 分钟_

#### - [ ] 6.3 导入依赖
- 导入 useResearchProgress Hook
- 导入 Lucide 图标（Loader2, CheckCircle2, XCircle）
- 导入必需的 React hooks
- _需求: Requirement 4_
- _预计时间: 10 分钟_

#### - [ ] 6.4 实现组件基础结构
- 定义函数组件
- 使用 useResearchProgress Hook
- 解构返回值（events, status, report, error）
- 添加 early return（taskId 为 null）
- _需求: Requirement 4_
- _预计时间: 30 分钟_

#### - [ ] 6.5 实现状态头部
- 创建状态显示区域
- 根据 status 显示不同图标
- running: Loader2 + 动画
- completed: CheckCircle2 + 绿色
- failed: XCircle + 红色
- 添加状态文本
- _需求: Requirement 4_
- _预计时间: 1 小时_

#### - [ ] 6.6 实现进度列表
- 遍历 events 数组
- 过滤 progress 事件
- 显示步骤信息（step/total: message）
- 添加进度指示器（圆点）
- 添加适当的样式
- _需求: Requirement 4_
- _预计时间: 1.5 小时_

#### - [ ] 6.7 实现错误显示
- 检查 error 状态
- 显示错误消息
- 使用红色背景
- 添加错误图标
- 提供友好的错误文本
- _需求: Requirement 4_
- _预计时间: 45 分钟_

#### - [ ] 6.8 添加组件样式
- 使用 Tailwind CSS
- 添加边框和圆角
- 添加内边距和间距
- 添加响应式设计
- 确保移动端适配
- _需求: Requirement 4, 15_
- _预计时间: 1 hour_

#### - [ ] 6.9 添加动画效果
- 添加 Loader 旋转动画
- 添加进度项淡入动画
- 添加状态切换过渡
- 使用 CSS transitions
- _需求: Requirement 4_
- _预计时间: 1 hour_

#### - [ ] 6.10 优化组件性能
- 使用 React.memo 包装组件
- 使用 useMemo 缓存计算
- 避免不必要的重渲染
- _需求: Requirement 13_
- _预计时间: 30 分钟_

#### - [ ] 6.11 添加组件文档
- 添加 JSDoc 注释
- 添加使用示例
- 添加 Props 说明
- _需求: Requirement 4_
- _预计时间: 20 分钟_

#### - [ ] 6.12 编写组件测试
- 创建测试文件
- 测试不同状态显示
- 测试进度更新
- 测试错误显示
- 使用 @testing-library/react
- _需求: Requirement 4, 17_
- _预计时间: 1.5 小时_

### Day 9: Artifact 集成（8 小时）

#### - [ ] 7.1 研究现有 Artifact 系统
- 阅读 Artifact 相关代码
- 理解 createDocument 工具
- 理解 updateDocument 工具
- 理解 Artifact 显示逻辑
- _需求: Requirement 8_
- _预计时间: 1 hour_

#### - [ ] 7.2 测试 createDocument 工具
- 在聊天中测试 createDocument
- 验证 Artifact 创建
- 验证内容显示
- 验证 Markdown 渲染
- _需求: Requirement 8_
- _预计时间: 45 分钟_

#### - [ ] 7.3 实现研究报告自动创建
- 在研究完成后调用 createDocument
- 设置 title 为研究主题
- 设置 kind 为 "text"
- 设置 content 为研究报告
- 验证 Artifact 正确创建
- _需求: Requirement 8_
- _预计时间: 1.5 小时_

#### - [ ] 7.4 优化报告格式
- 确保报告是 Markdown 格式
- 添加标题和章节
- 添加引用和链接
- 验证 Markdown 渲染正确
- _需求: Requirement 8_
- _预计时间: 1 hour_

#### - [ ] 7.5 实现报告更新
- 在用户追问后调用 updateDocument
- 传递更新的内容
- 保持 Artifact ID
- 验证更新成功
- _需求: Requirement 8_
- _预计时间: 1 hour_

#### - [ ] 7.6 测试 Artifact 版本历史
- 创建初始报告
- 多次更新报告
- 验证版本历史保存
- 测试版本切换
- _需求: Requirement 8_
- _预计时间: 1 hour_

#### - [ ] 7.7 实现报告导出功能
- 测试现有导出功能
- 验证支持复制
- 验证支持下载
- 优化导出格式
- _需求: Requirement 8_
- _预计时间: 45 分钟_

#### - [ ] 7.8 优化 Artifact 显示
- 调整 Artifact 样式
- 优化 Markdown 渲染
- 添加代码高亮（如果需要）
- 确保移动端适配
- _需求: Requirement 8, 15_
- _预计时间: 1 hour_

#### - [ ] 7.9 测试完整 Artifact 流程
- 发起研究
- 等待完成
- 验证 Artifact 创建
- 测试追问更新
- 测试导出功能
- _需求: Requirement 8_
- _预计时间: 1 hour_

### Day 10: Week 2 集成测试（8 小时）

#### - [ ] 8.1 测试完整用户流程
- 用户登录
- 发起研究请求
- 查看实时进度
- 查看生成的报告
- 追问和更新
- _需求: All Week 2 Requirements_
- _预计时间: 2 小时_

#### - [ ] 8.2 测试多个研究任务
- 连续发起多个研究
- 验证每个任务独立
- 验证进度显示正确
- 验证报告生成正确
- _需求: Requirement 5, 8_
- _预计时间: 1.5 小时_

#### - [ ] 8.3 测试错误恢复
- 模拟研究失败
- 验证错误显示
- 测试重新发起研究
- 验证恢复正常
- _需求: Requirement 9_
- _预计时间: 1 hour_

#### - [ ] 8.4 测试用户体验
- 评估响应速度
- 评估进度显示清晰度
- 评估错误提示友好度
- 收集改进建议
- _需求: Requirement 14_
- _预计时间: 1 hour_

#### - [ ] 8.5 性能测试
- 测试页面加载时间
- 测试工具调用响应时间
- 测试 SSE 连接建立时间
- 测试内存使用
- _需求: Requirement 13_
- _预计时间: 1 hour_

#### - [ ] 8.6 移动端测试
- 在移动设备上测试
- 验证布局适配
- 验证触摸操作
- 验证进度显示
- 验证 Artifact 显示
- _需求: Requirement 15_
- _预计时间: 1 hour_

#### - [ ] 8.7 修复发现的问题
- 记录所有问题
- 按优先级排序
- 修复关键问题
- 验证修复效果
- _需求: All Week 2 Requirements_
- _预计时间: 1.5 小时_

#### - [ ] 8.8 生成 Week 2 测试报告
- 汇总所有测试结果
- 记录性能指标
- 记录用户体验评估
- 创建测试报告文档
- _需求: All Week 2 Requirements_
- _预计时间: 30 分钟_


---

## Week 3: 数据库与完善（40 小时）

### Day 11-12: 数据库扩展（16 小时）

#### - [ ] 9.1 备份现有数据库 Schema
- 导出当前 Schema
- 创建备份
- 记录现有表结构
- _需求: Requirement 7_
- _预计时间: 20 分钟_

#### - [ ] 9.2 设计 researchTask 表结构
- 定义所有字段
- 定义字段类型
- 定义关系（外键）
- 定义索引
- 编写 Schema 文档
- _需求: Requirement 7_
- _预计时间: 1 hour_

#### - [ ] 9.3 在 schema.ts 中添加 researchTask 表
- 打开 `lib/db/schema.ts`
- 使用 pgTable 定义表
- 添加所有字段定义
- 添加外键关系
- 添加类型定义
- _需求: Requirement 7_
- _预计时间: 1.5 小时_

#### - [ ] 9.4 定义基础字段
- id: uuid, primaryKey
- chatId: uuid, references chat.id
- userId: uuid, references user.id
- prompt: text, notNull
- status: varchar(20), notNull
- _需求: Requirement 7_
- _预计时间: 30 分钟_

#### - [ ] 9.5 定义关联字段
- artifactId: uuid (关联 Artifact)
- 添加可选的外键约束
- _需求: Requirement 7_
- _预计时间: 20 分钟_

#### - [ ] 9.6 定义进度和结果字段
- progress: json (进度数据)
- result: text (最终报告)
- error: text (错误信息)
- 定义 JSON 类型结构
- _需求: Requirement 7_
- _预计时间: 45 分钟_

#### - [ ] 9.7 定义时间戳字段
- createdAt: timestamp, defaultNow
- updatedAt: timestamp, defaultNow
- completedAt: timestamp (可选)
- _需求: Requirement 7_
- _预计时间: 20 分钟_

#### - [ ] 9.8 实现 saveResearchTask 函数
- 创建函数定义
- 接受任务参数
- 使用 db.insert() 插入数据
- 返回插入的记录
- 添加错误处理
- _需求: Requirement 7_
- _预计时间: 1 hour_

#### - [ ] 9.9 实现 updateResearchTaskStatus 函数
- 创建函数定义
- 接受 id 和 status 参数
- 接受可选的 data 参数
- 使用 db.update() 更新数据
- 更新 updatedAt 时间戳
- 处理 completedAt 时间戳
- _需求: Requirement 7_
- _预计时间: 1 hour_

#### - [ ] 9.10 实现 getResearchTasksByChatId 函数
- 创建函数定义
- 接受 chatId 参数
- 使用 db.select() 查询数据
- 按创建时间排序
- 返回任务列表
- _需求: Requirement 7_
- _预计时间: 45 分钟_

#### - [ ] 9.11 生成数据库迁移
- 运行 `npm run db:generate`
- 检查生成的迁移文件
- 验证迁移 SQL 正确
- _需求: Requirement 7_
- _预计时间: 30 分钟_

#### - [ ] 9.12 在开发环境运行迁移
- 运行 `npm run db:migrate`
- 验证表创建成功
- 使用 `npm run db:studio` 检查
- _需求: Requirement 7_
- _预计时间: 30 分钟_

#### - [ ] 9.13 测试数据库函数
- 测试 saveResearchTask
- 测试 updateResearchTaskStatus
- 测试 getResearchTasksByChatId
- 验证数据正确保存和查询
- _需求: Requirement 7_
- _预计时间: 2 小时_

#### - [ ] 9.14 集成数据库到聊天流程
- 在研究开始时保存任务
- 在研究进行中更新状态
- 在研究完成时更新结果
- 关联 Artifact ID
- _需求: Requirement 7, 16_
- _预计时间: 2 小时_

#### - [ ] 9.15 实现历史记录查询
- 创建历史记录查询接口
- 在聊天界面显示历史研究
- 支持查看历史报告
- _需求: Requirement 16_
- _预计时间: 2 hours_

#### - [ ] 9.16 测试数据持久化
- 发起研究任务
- 刷新页面
- 验证数据仍然存在
- 验证可以查看历史
- _需求: Requirement 7, 16_
- _预计时间: 1 hour_

### Day 13: 错误处理与重连（8 小时）

#### - [ ] 10.1 审查现有错误处理
- 检查所有错误处理点
- 识别遗漏的错误场景
- 记录需要改进的地方
- _需求: Requirement 9_
- _预计时间: 1 hour_

#### - [ ] 10.2 完善工具调用错误处理
- 改进 startResearch 错误处理
- 添加更详细的错误消息
- 添加错误分类
- 记录错误日志
- _需求: Requirement 9_
- _预计时间: 1 hour_

#### - [ ] 10.3 完善 SSE 连接错误处理
- 改进 EventSource 错误处理
- 区分不同类型的错误
- 添加错误恢复策略
- _需求: Requirement 9_
- _预计时间: 1 hour_

#### - [ ] 10.4 优化重连机制
- 审查重连逻辑
- 优化指数退避策略
- 添加重连状态提示
- 改进用户体验
- _需求: Requirement 10_
- _预计时间: 1.5 小时_

#### - [ ] 10.5 实现错误边界
- 创建 React Error Boundary
- 包装关键组件
- 提供错误回退 UI
- 记录错误信息
- _需求: Requirement 9_
- _预计时间: 1 hour_

#### - [ ] 10.6 添加错误提示组件
- 创建 Toast 或 Alert 组件
- 显示友好的错误消息
- 提供重试选项
- 自动消失或手动关闭
- _需求: Requirement 9_
- _预计时间: 1.5 小时_

#### - [ ] 10.7 测试所有错误场景
- 测试网络错误
- 测试 API 错误
- 测试超时
- 测试重连
- 验证错误处理正确
- _需求: Requirement 9, 10_
- _预计时间: 1.5 小时_

### Day 14: 端到端测试（8 小时）

#### - [ ] 11.1 设置 E2E 测试环境
- 安装 Playwright（如果需要）
- 配置测试环境
- 创建测试目录
- _需求: Requirement 17_
- _预计时间: 30 分钟_

#### - [ ] 11.2 编写用户注册/登录测试
- 测试用户注册流程
- 测试用户登录流程
- 验证认证状态
- _需求: Requirement 17_
- _预计时间: 1 hour_

#### - [ ] 11.3 编写研究发起测试
- 测试输入研究主题
- 测试 AI 响应
- 测试工具调用
- 验证 taskId 返回
- _需求: Requirement 17_
- _预计时间: 1.5 小时_

#### - [ ] 11.4 编写进度显示测试
- 测试进度组件显示
- 测试进度更新
- 测试状态变化
- 验证 UI 正确
- _需求: Requirement 17_
- _预计时间: 1 hour_

#### - [ ] 11.5 编写报告生成测试
- 测试研究完成
- 测试 Artifact 创建
- 测试报告显示
- 验证内容正确
- _需求: Requirement 17_
- _预计时间: 1 hour_

#### - [ ] 11.6 编写追问更新测试
- 测试用户追问
- 测试报告更新
- 测试版本历史
- 验证更新正确
- _需求: Requirement 17_
- _预计时间: 1 hour_

#### - [ ] 11.7 编写历史记录测试
- 测试历史查询
- 测试历史显示
- 测试历史报告查看
- _需求: Requirement 16, 17_
- _预计时间: 1 hour_

#### - [ ] 11.8 编写错误场景测试
- 测试网络错误
- 测试 API 失败
- 测试重连
- 验证错误处理
- _需求: Requirement 9, 17_
- _预计时间: 1 hour_

#### - [ ] 11.9 运行所有 E2E 测试
- 执行完整测试套件
- 记录测试结果
- 修复失败的测试
- 验证所有测试通过
- _需求: Requirement 17_
- _预计时间: 1 hour_

### Day 15: 文档与部署（8 小时）

#### - [ ]* 12.1 更新 README
- 添加 Phase 3 功能说明
- 添加研究功能使用指南
- 添加环境变量配置说明
- 添加开发指南
- _需求: Requirement 20_
- _预计时间: 1.5 小时_

#### - [ ]* 12.2 创建开发文档
- 编写组件使用文档
- 编写 Hook 使用文档
- 编写工具使用文档
- 添加代码示例
- _需求: Requirement 20_
- _预计时间: 1.5 小时_

#### - [ ]* 12.3 创建部署文档
- 编写 Vercel 部署指南
- 编写环境变量配置指南
- 编写数据库迁移指南
- 添加故障排查指南
- _需求: Requirement 20_
- _预计时间: 1 hour_

#### - [ ] 12.4 准备生产环境配置
- 配置生产环境变量
- 验证所有配置正确
- 准备数据库迁移
- _需求: Requirement 19_
- _预计时间: 1 hour_

#### - [ ] 12.5 在 Neon 运行数据库迁移
- 连接到 Neon 数据库
- 运行迁移脚本
- 验证表创建成功
- 测试数据库连接
- _需求: Requirement 19_
- _预计时间: 45 分钟_

#### - [ ] 12.6 部署到 Vercel
- 推送代码到 GitHub
- 在 Vercel 配置项目
- 配置环境变量
- 触发部署
- _需求: Requirement 19_
- _预计时间: 1 hour_

#### - [ ] 12.7 验证生产环境
- 访问生产 URL
- 测试用户注册/登录
- 测试研究功能
- 测试完整流程
- _需求: Requirement 19_
- _预计时间: 1 hour_

#### - [ ] 12.8 性能优化（可选）
- 分析性能瓶颈
- 优化加载时间
- 优化渲染性能
- 验证改进效果
- _需求: Requirement 13_
- _预计时间: 1 hour_

#### - [ ] 12.9 生成 Phase 3 最终报告
- 汇总所有功能
- 记录所有测试结果
- 记录性能指标
- 记录已知问题
- 创建完整报告
- _需求: All Requirements_
- _预计时间: 1 hour_

---

## 验收标准

### 核心功能验收

- [ ] startResearch 工具正常工作
- [ ] useResearchProgress Hook 正常工作
- [ ] API 代理路由正常工作
- [ ] ResearchProgress 组件正常显示
- [ ] 聊天流程改造完成
- [ ] Artifact 集成完成
- [ ] 数据库 Schema 扩展完成
- [ ] 错误处理和重连机制完善

### 用户体验验收

- [ ] 用户可以发起研究
- [ ] 实时显示研究进度
- [ ] 自动生成研究报告
- [ ] 支持追问和更新
- [ ] 支持查看历史记录
- [ ] 错误提示友好
- [ ] 移动端适配良好

### 性能验收

- [ ] 工具调用响应 < 1 秒
- [ ] SSE 连接建立 < 2 秒
- [ ] 页面加载 < 3 秒
- [ ] 无内存泄漏
- [ ] 支持多标签页

### 测试验收

- [ ] 单元测试覆盖核心功能
- [ ] 集成测试通过
- [ ] E2E 测试通过
- [ ] 所有测试通过

### 部署验收

- [ ] 可以部署到 Vercel
- [ ] 生产环境正常工作
- [ ] 数据库迁移成功
- [ ] 环境变量配置正确

### 文档验收

- [ ] README 更新完整（可选）
- [ ] 开发文档完整（可选）
- [ ] 部署文档完整（可选）
- [ ] 代码注释清晰

---

## 时间估算总结

| Week | 模块 | 任务数 | 预计时间 |
|------|------|--------|----------|
| **Week 1** | 架构与工具桥接 | 30+ | 40 小时 |
| - Day 1 | 环境准备与工具创建 | 11 | 8 小时 |
| - Day 2 | API 代理路由 | 13 | 8 小时 |
| - Day 3-4 | useResearchProgress Hook | 23 | 16 小时 |
| - Day 5 | Week 1 集成测试 | 8 | 8 小时 |
| **Week 2** | 聊天流程与组件 | 30+ | 40 小时 |
| - Day 6-7 | 聊天流程改造 | 14 | 16 小时 |
| - Day 8 | ResearchProgress 组件 | 12 | 8 小时 |
| - Day 9 | Artifact 集成 | 9 | 8 小时 |
| - Day 10 | Week 2 集成测试 | 8 | 8 小时 |
| **Week 3** | 数据库与完善 | 30+ | 40 小时 |
| - Day 11-12 | 数据库扩展 | 16 | 16 小时 |
| - Day 13 | 错误处理与重连 | 7 | 8 小时 |
| - Day 14 | 端到端测试 | 9 | 8 小时 |
| - Day 15 | 文档与部署 | 9 | 8 小时 |
| **总计** | **全部** | **90+** | **120 小时** |

**实际工作日**: 15 天（3 周，每天 8 小时）

---

## 依赖关系

```
Phase 1 + Phase 2 完成
    ↓
Week 1: 架构与工具桥接
    ↓
Week 2: 聊天流程与组件
    ↓
Week 3: 数据库与完善
    ↓
Phase 3 完成
```

---

## 风险和缓解

### 高风险

1. **SSE 在生产环境不稳定**
   - 缓解: 配置正确的响应头
   - 缓解: 实现完善的重连机制
   - 缓解: 在部署前充分测试

2. **AI 不按预期调用工具**
   - 缓解: 优化 System Prompt
   - 缓解: 添加工具调用示例
   - 缓解: 多次测试和调整

### 中风险

3. **性能不满足要求**
   - 缓解: 使用 React.memo 优化
   - 缓解: 使用 useMemo 缓存
   - 缓解: 优化组件渲染

4. **移动端适配问题**
   - 缓解: 使用响应式设计
   - 缓解: 在移动设备上测试
   - 缓解: 使用 Tailwind 断点

---

## 下一步行动

### 立即开始（Week 1 Day 1）

1. ✅ 配置环境变量 (任务 1.1)
2. ✅ 创建 startResearch 工具 (任务 1.2-1.11)

### Week 1 目标

- ✅ 完成工具和 API 代理
- ✅ 完成 useResearchProgress Hook
- ✅ 通过 Week 1 集成测试

### Week 2 目标

- ✅ 完成聊天流程改造
- ✅ 完成 ResearchProgress 组件
- ✅ 完成 Artifact 集成
- ✅ 通过 Week 2 集成测试

### Week 3 目标

- ✅ 完成数据库扩展
- ✅ 完善错误处理
- ✅ 通过 E2E 测试
- ✅ 部署到生产环境

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待执行
