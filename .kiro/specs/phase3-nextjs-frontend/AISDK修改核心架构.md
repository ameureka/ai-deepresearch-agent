非常好！我现在看到了核心问题。让我深入分析 AI SDK 工具调用方案的严重架构问题：

  🚨 Phase 3 任务方案的核心问题分析

  问题 1: startResearch 工具的设计存在根本性矛盾 🔴

  当前方案 (tasks.md + design.md):

  export const startResearch = tool({
    execute: async ({ topic }) => {
      // 调用 POST /api/research/stream
      const res = await fetch(`${RESEARCH_API}/api/research/stream`, {
        method: 'POST',
        body: JSON.stringify({ prompt: topic }),
      });

      // 问题：这里尝试从 SSE 流中读取 taskId
      const reader = res.body?.getReader();
      const { value } = await reader!.read();
      const taskId = parseTaskIdFromSSE(value);

      return { taskId, status: 'started' };
    },
  });

  致命问题:

  1. SSE 连接会被提前关闭 🔴
    - startResearch 工具的 execute 函数执行完毕后会返回
    - 返回后，res.body 的 ReadableStream 会被垃圾回收
    - SSE 连接会断开，后续的 plan, progress, done 事件全部丢失
  2. 违反 AI SDK 工具调用的设计原则 🔴
    - AI SDK 的 tool 应该是同步操作或短异步操作
    - 不应该返回一个需要长时间监听的流连接
    - 工具应该返回最终结果，而不是中间状态
  3. taskId 无法正确提取 🔴
    - Phase 2 的 SSE 接口没有在首个事件返回 taskId
    - start 事件只包含 {prompt: str}，没有 taskId
    - tasks.md 中的逻辑（Task 1.6）假设可以提取 taskId，但实际上不存在

  实际运行结果:

  用户: "Research quantum computing"
    ↓
  AI: 调用 startResearch({ topic: "quantum computing" })
    ↓
  startResearch 发起 POST /api/research/stream
    ↓
  读取首个 SSE 事件: event: start, data: {prompt: "quantum computing"}
    ↓
  提取 taskId: UNDEFINED (因为 start 事件没有 taskId)
    ↓
  返回: { taskId: <生成的UUID>, status: 'started' }
    ↓
  execute 函数结束 → SSE 连接关闭 ❌
    ↓
  后续所有事件丢失 (plan, progress, done) ❌

  ---
  问题 2: useResearchProgress Hook 无法获取数据 🔴

  当前方案:

  export function useResearchProgress(taskId: string | null) {
    useEffect(() => {
      if (!taskId) return;

      // 尝试通过 taskId 订阅 SSE
      const eventSource = new EventSource(
        `/api/research/stream?taskId=${taskId}`
      );

      eventSource.addEventListener('progress', (e) => {
        // 处理事件
      });
    }, [taskId]);
  }

  致命问题:

  1. Phase 2 的 SSE 接口不支持 GET 请求 🔴
    - Phase 2 只实现了 POST /api/research/stream
    - 没有实现 GET /api/research/stream?taskId=xxx
    - EventSource 只能发送 GET 请求
  2. 无法通过 taskId 恢复 SSE 连接 🔴
    - Phase 2 的 SSE 是一次性流，执行完就结束
    - 没有"任务状态存储"，无法通过 taskId 重新获取进度
    - 即使实现 GET 接口，后端也无法知道该任务的进度
  3. 时序问题 🔴
  时间轴:
  T0: startResearch 调用 POST /api/research/stream
  T1: 研究任务开始执行
  T2: startResearch 返回 taskId
  T3: useResearchProgress 用 taskId 发起 GET 请求
  T4: 后端收到 GET 请求，但研究任务已经在 T1 开始了

  问题：T3 发起的新 SSE 连接会启动一个**新的研究任务**
       而不是订阅 T1 已经开始的任务

  ---
  问题 3: API 代理路由的设计不合理 🔴

  tasks.md 中的设计 (Day 2):

  // Task 2.9: 实现 GET 方法处理器
  export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const taskId = searchParams.get('taskId');

    // 调用后端 GET 接口？
    // 但是 Phase 2 没有 GET 接口！
  }

  问题:

  1. Phase 2 API 不支持这个设计 🔴
    - Phase 2 只有 POST /api/research/stream
    - 需要 prompt 参数，不支持 taskId 查询
  2. 即使实现 GET 接口也无意义 🔴
    - 后端没有"任务状态管理"
    - 无法通过 taskId 恢复或查询任务进度
    - 会导致重复执行研究任务

  ---
  🤔 核心问题的根源

  架构不匹配:

  AI SDK 工具调用模式:
    工具 → 快速执行 → 返回结果 → 结束
    ✅ 适合: getWeather, createDocument
    ❌ 不适合: 长时间运行的研究任务

  Phase 2 SSE 接口设计:
    发起请求 → 保持连接 → 流式推送事件 → 任务完成 → 关闭连接
    ✅ 适合: 需要实时反馈的长任务
    ❌ 不适合: 工具调用（工具会提前返回，导致连接关闭）

  设计文档的错误假设:

  tasks.md 和 design.md 假设：
  1. ❌ 可以从 SSE 首个事件提取 taskId（实际不存在）
  2. ❌ 可以通过 taskId 订阅已启动的任务（后端不支持）
  3. ❌ AI SDK 工具可以持有 SSE 连接（工具会提前返回）

  ---
  ✅ 正确的解决方案

  方案 A: 完全绕过工具调用 ⭐ 推荐

  不使用 startResearch 工具，直接在前端处理：

  // 用户点击"开始研究"按钮
  function handleStartResearch(topic: string) {
    // 1. 生成 taskId
    const taskId = crypto.randomUUID();

    // 2. 直接订阅 SSE
    const eventSource = new EventSource(
      `/api/research/stream?prompt=${encodeURIComponent(topic)}`
    );

    // 3. 处理事件
    eventSource.addEventListener('start', ...);
    eventSource.addEventListener('plan', ...);
    eventSource.addEventListener('done', (e) => {
      const { report } = JSON.parse(e.data);

      // 4. 使用 AI SDK 的 createDocument 工具
      // 将报告保存为 Artifact
      aiClient.tool('createDocument', {
        title: `Research: ${topic}`,
        content: report,
        kind: 'text',
      });
    });
  }

  优点:
  - ✅ SSE 连接完整保持
  - ✅ 不依赖工具调用
  - ✅ 无需修改 Phase 2 后端
  - ✅ 实现简单清晰

  缺点:
  - ❌ AI 无法主动发起研究（需要用户手动触发）

  ---
  方案 B: 修改 Phase 2 后端支持任务状态管理

  添加任务状态存储 + GET 接口：

  # 后端新增
  tasks_in_progress = {}  # {taskId: SSE generator}

  @app.post("/api/research/stream")
  async def research_stream(request: ResearchRequest):
      task_id = str(uuid.uuid4())

      async def event_generator():
          # 首个事件包含 taskId
          yield create_start_event(request.prompt, task_id)  # 修改
          # ... 其余代码

      # 存储生成器
      tasks_in_progress[task_id] = event_generator()

      return StreamingResponse(
          tasks_in_progress[task_id],
          headers={'X-Task-ID': task_id}  # 新增响应头
      )

  @app.get("/api/research/stream")
  async def research_stream_subscribe(task_id: str):
      if task_id not in tasks_in_progress:
          raise HTTPException(404, "Task not found")

      # 返回已存在的流（需要支持多订阅者）
      return StreamingResponse(tasks_in_progress[task_id])

  前端工具：
  export const startResearch = tool({
    execute: async ({ topic }) => {
      const res = await fetch(`${API}/api/research/stream`, {
        method: 'POST',
        body: JSON.stringify({ prompt: topic }),
      });

      // 从响应头获取 taskId
      const taskId = res.headers.get('X-Task-ID');

      // 立即关闭这个连接
      await res.body?.cancel();

      return { taskId, status: 'started' };
    },
  });

  优点:
  - ✅ 支持 AI 主动发起研究
  - ✅ 支持多客户端订阅同一任务

  缺点:
  - ❌ 需要大幅修改 Phase 2 后端
  - ❌ 需要实现任务状态管理（内存或数据库）
  - ❌ 增加系统复杂度

  ---
  方案 C: 工具调用返回完整报告（阻塞式）

  export const startResearch = tool({
    execute: async ({ topic }) => {
      const res = await fetch(`${API}/api/research/stream`, {
        method: 'POST',
        body: JSON.stringify({ prompt: topic }),
      });

      const reader = res.body.getReader();
      let report = '';

      // 阻塞式读取所有事件，直到 done
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const text = new TextDecoder().decode(value);
        const event = parseSSEEvent(text);

        if (event.type === 'done') {
          report = event.data.report;
          break;
        }
      }

      return { report };  // 直接返回最终报告
    },
  });

  优点:
  - ✅ 无需修改后端
  - ✅ 符合工具调用模式
  - ✅ AI 可主动发起

  缺点:
  - ❌ 无实时进度显示（用户体验差）
  - ❌ 工具执行时间长（3-5分钟），可能超时
  - ❌ 失去 SSE 的核心价值

  ---
  📊 方案对比

  | 方案        | Phase 2修改 | 实时进度 | AI主动发起 | 实现复杂度   | 推荐度   |
  |-----------|-----------|------|--------|---------|-------|
  | A: 绕过工具调用 | 不需要       | ✅ 完整 | ❌ 否    | ⭐ 简单    | ⭐⭐⭐⭐⭐ |
  | B: 任务状态管理 | 大幅修改      | ✅ 完整 | ✅ 是    | ⭐⭐⭐⭐ 复杂 | ⭐⭐⭐   |
  | C: 阻塞式工具  | 不需要       | ❌ 无  | ✅ 是    | ⭐⭐ 中等   | ⭐⭐    |

  ---
  🎯 我的建议

  基于深度分析，我强烈建议采用方案 A，理由：

  1. MVP 原则: 最快实现核心功能
  2. 用户体验: 实时进度显示是核心价值
  3. 风险最低: 不需要修改已验证的 Phase 2 后端
  4. 实现简单: 3 周时间充裕

  实施思路:
  - Week 1: 实现前端 SSE 订阅 + 进度显示组件
  - Week 2: 集成到聊天界面 + Artifact 显示
  - Week 3: 数据库持久化 + 部署

  放弃的功能（可在 Phase 4 实现）:
  - AI 主动发起研究（改为用户点击按钮）
  - startResearch 工具（不需要）
