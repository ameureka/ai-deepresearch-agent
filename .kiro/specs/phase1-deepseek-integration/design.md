# Phase 1: DeepSeek API 集成 - 设计文档

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 1 - DeepSeek API 集成
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **状态**: 待实施

---

## 概述

### 设计目标

Phase 1 的设计目标是在现有 FastAPI 研究系统中集成 DeepSeek API，通过以下方式实现成本优化：

1. **最小化代码修改**: 只修改配置和模型调用，不改变核心逻辑
2. **保持兼容性**: 与现有 OpenAI 代码完全兼容
3. **灵活配置**: 支持动态切换模型
4. **成本可控**: 实现 30-40% 的成本降低
5. **质量保证**: 保持 85%+ 的输出质量

### 核心原则

- **MVP 原则**: 只做核心功能，避免过度设计
- **渐进式集成**: 先集成研究和编辑代理，保留写作和规划代理使用 OpenAI
- **降级优先**: 失败时自动降级到 OpenAI
- **成本透明**: 实时追踪和报告成本

---

## 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Planner    │  │  Researcher  │  │    Writer    │  │
│  │    Agent     │  │    Agent     │  │    Agent     │  │
│  │              │  │              │  │              │  │
│  │ OpenAI       │  │ DeepSeek ✓   │  │ OpenAI       │  │
│  │ o1-mini      │  │ deepseek-    │  │ gpt-4o-mini  │  │
│  │              │  │ chat         │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│                  ┌────────▼────────┐                    │
│                  │  ModelConfig    │                    │
│                  │  - get_model()  │                    │
│                  │  - validate()   │                    │
│                  └────────┬────────┘                    │
│                           │                             │
│         ┌─────────────────┼─────────────────┐           │
│         │                 │                 │           │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐  │
│  │   aisuite    │  │ CostTracker  │  │   Fallback   │  │
│  │   Provider   │  │              │  │   Handler    │  │
│  └──────┬───────┘  └──────────────┘  └──────────────┘  │
│         │                                               │
├─────────┼───────────────────────────────────────────────┤
│         │                                               │
│  ┌──────▼───────┐         ┌──────────────┐             │
│  │   DeepSeek   │         │    OpenAI    │             │
│  │     API      │         │     API      │             │
│  └──────────────┘         └──────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 组件职责

1. **ModelConfig**: 统一的模型配置管理
2. **aisuite Provider**: 多模型调用的统一接口
3. **CostTracker**: 成本追踪和报告
4. **Fallback Handler**: 降级机制处理
5. **Agent**: 各个代理（Planner, Researcher, Writer, Editor）

---

## 组件设计

### 1. ModelConfig 类

**职责**: 统一管理所有代理的模型配置

**接口设计**:

```python
class ModelConfig:
    """统一的模型配置管理"""
    
    # 类属性 - 从环境变量读取
    PLANNER_MODEL: str
    RESEARCHER_MODEL: str
    WRITER_MODEL: str
    EDITOR_MODEL: str
    FALLBACK_MODEL: str
    REQUEST_TIMEOUT: int
    
    @classmethod
    def get_model(cls, agent_type: str) -> str:
        """获取指定代理的模型"""
        pass
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置"""
        pass
```

**实现细节**:

- 从环境变量读取配置，提供默认值
- 支持运行时验证
- 提供清晰的错误提示
- 不在日志中输出完整 API Key

**配置示例**:
```bash
# .env
PLANNER_MODEL=openai:o1-mini
RESEARCHER_MODEL=deepseek:deepseek-chat
WRITER_MODEL=openai:gpt-4o-mini
EDITOR_MODEL=deepseek:deepseek-chat
FALLBACK_MODEL=openai:gpt-4o-mini
REQUEST_TIMEOUT=90
```

### 2. CostTracker 类

**职责**: 追踪和报告 API 调用成本

**接口设计**:

```python
class CostTracker:
    """API 调用成本追踪"""
    
    # 价格表（每百万 token）
    PRICES: Dict[str, Dict[str, float]]
    
    def __init__(self):
        self.costs: Dict[str, float]
        self.calls: Dict[str, int]
        self.tokens: Dict[str, Dict[str, int]]
    
    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """记录一次 API 调用"""
        pass
    
    def summary(self) -> Dict[str, Any]:
        """打印成本摘要"""
        pass
    
    def compare(self, baseline: Dict[str, float]) -> Dict[str, Any]:
        """对比成本节省"""
        pass
```

**价格表**:
```python
PRICES = {
    "deepseek:deepseek-chat": {"input": 0.14, "output": 0.28},
    "deepseek:deepseek-reasoner": {"input": 0.55, "output": 2.19},
    "openai:gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "openai:o1-mini": {"input": 3.00, "output": 12.00},
}
```

### 3. Fallback Handler

**职责**: 处理 API 调用失败时的降级逻辑

**接口设计**:

```python
def with_fallback(primary_model: str, fallback_model: str = None):
    """模型降级装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs, model=primary_model)
            except Exception as e:
                logger.warning(f"{primary_model} 失败: {e}, 降级到 {fallback_model}")
                return func(*args, **kwargs, model=fallback_model)
        return wrapper
    return decorator
```

**使用示例**:
```python
@with_fallback("deepseek:deepseek-chat")
def research_agent(prompt: str, model: str = None):
    # 实现
    pass
```

### 4. Agent 更新

**Research Agent**:
```python
def research_agent(
    prompt: str, 
    model: str = None,
    return_messages: bool = False
):
    """研究代理 - 使用 DeepSeek"""
    if model is None:
        model = ModelConfig.RESEARCHER_MODEL
    
    # 调用 aisuite
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_turns=5,
        temperature=0.0,
    )
    
    # 追踪成本
    if hasattr(resp, 'usage'):
        tracker.track(model, resp.usage.prompt_tokens, resp.usage.completion_tokens)
    
    return content
```

**Editor Agent**:
```python
def editor_agent(
    prompt: str,
    model: str = None,
    target_min_words: int = 2400,
):
    """编辑代理 - 使用 DeepSeek"""
    if model is None:
        model = ModelConfig.EDITOR_MODEL
    
    # 类似实现
    pass
```

**Writer Agent** (保持 OpenAI):
```python
def writer_agent(
    prompt: str,
    model: str = None,
    min_words_total: int = 2400,
):
    """写作代理 - 保持 OpenAI"""
    if model is None:
        model = ModelConfig.WRITER_MODEL  # openai:gpt-4o-mini
    
    # 保持现有实现
    pass
```

**Planner Agent** (保持 OpenAI):
```python
def planner_agent(
    topic: str, 
    model: str = None
) -> List[str]:
    """规划代理 - 保持 OpenAI"""
    if model is None:
        model = ModelConfig.PLANNER_MODEL  # openai:o1-mini
    
    # 保持现有实现
    pass
```

---

## 数据模型

### 成本追踪数据结构

```python
# 单次调用记录
class CallRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: datetime

# 成本摘要
class CostSummary:
    total_cost: float
    total_calls: int
    by_model: Dict[str, ModelCost]
    
class ModelCost:
    model: str
    calls: int
    input_tokens: int
    output_tokens: int
    cost: float
```

### 配置数据结构

```python
class Config:
    # API Keys
    deepseek_api_key: str
    openai_api_key: str
    tavily_api_key: str
    
    # 模型配置
    planner_model: str
    researcher_model: str
    writer_model: str
    editor_model: str
    fallback_model: str
    
    # 其他配置
    request_timeout: int
```

---

## 错误处理

### 错误分类

1. **配置错误**
   - 缺少 API Key
   - 无效的模型名称
   - aisuite 版本过低

2. **API 错误**
   - 401: Invalid API Key
   - 429: Rate Limit Exceeded
   - 500: Server Error
   - Timeout: 请求超时

3. **工具调用错误**
   - 工具不可用
   - 工具返回格式错误
   - 工具超时

### 错误处理策略

```python
# 1. 配置错误 - 启动时验证
try:
    ModelConfig.validate()
except ValueError as e:
    logger.error(f"配置错误: {e}")
    sys.exit(1)

# 2. API 错误 - 降级处理
try:
    response = call_deepseek_api()
except APIError as e:
    if e.status_code == 401:
        logger.error("Invalid API Key")
        raise
    elif e.status_code == 429:
        logger.warning("Rate limit, 降级到 OpenAI")
        response = call_openai_api()
    elif e.status_code == 500:
        logger.warning("Server error, 降级到 OpenAI")
        response = call_openai_api()

# 3. 工具调用错误 - 记录并继续
try:
    result = call_tool(tool_name, params)
except ToolError as e:
    logger.warning(f"工具调用失败: {e}")
    result = {"error": str(e)}
```

---

## 测试策略

### 单元测试

**测试范围**:
1. ModelConfig 类
   - 配置读取
   - 默认值
   - 验证逻辑

2. CostTracker 类
   - 成本计算
   - 累计统计
   - 摘要生成

3. Fallback Handler
   - 降级触发
   - 日志记录
   - 异常处理

**测试工具**: pytest

**覆盖率目标**: >= 80%

### 集成测试

**测试场景**:
1. 完整研究流程
   - 规划 → 研究 → 写作 → 编辑
   - 验证 DeepSeek 调用
   - 验证工具调用
   - 验证成本追踪

2. 降级场景
   - DeepSeek 失败
   - 自动切换到 OpenAI
   - 任务继续执行

3. 成本对比
   - 同一任务使用不同模型
   - 对比成本和质量
   - 验证成本节省

### 性能测试

**测试指标**:
1. 响应时间
   - Research Agent: < 150s
   - Editor Agent: < 90s
   - 对比 OpenAI 版本

2. 并发能力
   - 5 个并发任务
   - 无明显性能下降

3. 内存使用
   - <= OpenAI 版本的 110%

### 质量测试

**测试方法**:
1. 人工评估
   - 10 个测试主题
   - 对比 DeepSeek 和 OpenAI 输出
   - 评分标准：结构、准确性、连贯性

2. 自动化指标
   - 报告长度
   - 引用数量
   - 结构完整性

**质量目标**: >= 85% (相比 OpenAI)

---

## 部署考虑

### 环境变量

**必需**:
- DEEPSEEK_API_KEY
- OPENAI_API_KEY
- TAVILY_API_KEY

**可选**:
- PLANNER_MODEL
- RESEARCHER_MODEL
- WRITER_MODEL
- EDITOR_MODEL
- FALLBACK_MODEL
- REQUEST_TIMEOUT

### 依赖管理

```txt
# requirements.txt
aisuite>=0.1.12
openai>=1.0.0
python-dotenv>=1.0.0
```

### 配置验证

```bash
# 启动前验证
python -c "from src.config import ModelConfig; ModelConfig.validate()"
```

---

## 性能优化

### 1. 连接池

使用 aisuite 的内置连接池管理

### 2. 超时控制

```python
REQUEST_TIMEOUT = 90  # 秒
```

### 3. 并发控制

使用 asyncio 支持并发请求（如需要）

### 4. 缓存策略

Phase 1 不实现缓存（延后到后续阶段）

---

## 安全考虑

### 1. API Key 管理

- 使用环境变量
- 不在代码中硬编码
- 不在日志中完整输出
- 使用 .gitignore 排除 .env 文件

### 2. 输入验证

- 验证模型名称格式
- 验证 API Key 格式
- 验证配置参数范围

### 3. 错误信息

- 不暴露敏感信息
- 提供友好的错误提示
- 记录详细日志供调试

---

## 监控和日志

### 日志级别

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### 关键日志点

1. **配置加载**
   ```python
   logger.info("配置加载完成")
   logger.info(f"Researcher Model: {ModelConfig.RESEARCHER_MODEL}")
   ```

2. **API 调用**
   ```python
   logger.info(f"调用 {model} API")
   logger.info(f"成本: ${cost:.4f}")
   ```

3. **降级事件**
   ```python
   logger.warning(f"{primary_model} 失败，降级到 {fallback_model}")
   ```

4. **成本摘要**
   ```python
   logger.info(f"总成本: ${total_cost:.4f}")
   logger.info(f"成本节省: {savings:.1f}%")
   ```

---

## 迁移策略

### 渐进式迁移

1. **Phase 1.1**: 只迁移 Research Agent
2. **Phase 1.2**: 迁移 Editor Agent
3. **Phase 1.3**: 测试和验证
4. **Phase 1.4**: 生产部署

### 回滚计划

如果出现问题，可以快速回滚：

```bash
# 回滚到 OpenAI
export RESEARCHER_MODEL=openai:gpt-4o-mini
export EDITOR_MODEL=openai:gpt-4o-mini

# 重启服务
systemctl restart research-api
```

---

## 文档和培训

### 开发文档

1. API 文档（自动生成）
2. 配置指南
3. 故障排查指南

### 用户文档

1. 成本优化说明
2. 质量对比报告
3. FAQ

---

## 附录

### A. 模型对比

| 模型 | Input ($/M) | Output ($/M) | 适用场景 |
|------|-------------|--------------|----------|
| deepseek-chat | $0.14 | $0.28 | 研究、编辑 |
| gpt-4o-mini | $0.15 | $0.60 | 写作 |
| o1-mini | $3.00 | $12.00 | 规划 |

### B. 成本计算示例

```python
# 研究任务
input_tokens = 5000
output_tokens = 3000

# DeepSeek
cost_deepseek = (5000/1M × $0.14) + (3000/1M × $0.28) = $0.00154

# OpenAI
cost_openai = (5000/1M × $0.15) + (3000/1M × $0.60) = $0.00255

# 节省
savings = ($0.00255 - $0.00154) / $0.00255 = 39.6%
```

### C. 工具调用格式

```python
# DeepSeek 工具格式（与 OpenAI 完全相同）
tools = [
    {
        "type": "function",
        "function": {
            "name": "tavily_search_tool",
            "description": "使用 Tavily API 执行网络搜索",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    }
]
```

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待实施
