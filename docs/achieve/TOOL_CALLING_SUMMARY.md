# 工具调用（Function Calling）完整指南

## 📚 文档索引

本指南包含以下文件：

1. **tool_calling_deep_dive.md** - 理论深度解析
2. **tool_calling_examples.py** - 完整代码示例
3. **tool_calling_flow.py** - 流程可视化演示
4. **tool_calling_comparison.py** - 三种实现方式对比
5. **TOOL_CALLING_SUMMARY.md** - 本文档（快速参考）

---

## 🎯 核心概念

### 工具调用的本质

**工具调用不是真正的"函数调用"，而是：**

1. LLM 生成结构化的 JSON 输出
2. 你的代码解析 JSON 并执行实际的 Python 函数
3. 将结果返回给 LLM
4. LLM 基于结果生成最终回复

```
用户输入 → LLM 推理 → 生成工具调用 JSON → 执行 Python 函数 → 返回结果 → LLM 合成回复
```

---

## 📋 工具定义的一级参数

### 完整结构

```json
{
  "type": "function",                    // 【一级】固定值
  "function": {                          // 【一级】函数定义对象
    "name": "tool_name",                 // 【二级】函数名称（必需）
    "description": "工具描述",            // 【二级】函数描述（必需）
    "parameters": {                      // 【二级】参数定义（必需）
      "type": "object",                  // 【三级】固定为 object
      "properties": {                    // 【三级】参数详情（必需）
        "param1": {                      // 【四级】具体参数
          "type": "string",              // 【五级】参数类型
          "description": "参数描述",      // 【五级】参数说明
          "default": "默认值"             // 【五级】可选
        }
      },
      "required": ["param1"]             // 【三级】必需参数列表（可选）
    }
  }
}
```

### 参数层级表

| 层级 | 参数路径 | 类型 | 必需 | 说明 |
|------|---------|------|------|------|
| 1 | `type` | string | ✅ | 固定值 "function" |
| 1 | `function` | object | ✅ | 函数定义对象 |
| 2 | `function.name` | string | ✅ | 函数名称 |
| 2 | `function.description` | string | ✅ | 函数描述 |
| 2 | `function.parameters` | object | ✅ | 参数定义（JSON Schema） |
| 3 | `parameters.type` | string | ✅ | 固定值 "object" |
| 3 | `parameters.properties` | object | ✅ | 参数详情 |
| 3 | `parameters.required` | array | ❌ | 必需参数列表 |
| 4 | `properties.{param_name}` | object | ✅ | 具体参数定义 |
| 5 | `{param_name}.type` | string | ✅ | 参数类型 |
| 5 | `{param_name}.description` | string | ✅ | 参数描述 |
| 5 | `{param_name}.default` | any | ❌ | 默认值 |
| 5 | `{param_name}.enum` | array | ❌ | 枚举值 |

---

## 🔧 参数类型详解

### 基础类型

```python
# string - 字符串
{
    "type": "string",
    "description": "搜索关键词",
    "minLength": 1,
    "maxLength": 500,
    "pattern": "^[a-zA-Z0-9\\s]+$",
    "enum": ["option1", "option2"],
    "default": "默认值"
}

# integer - 整数
{
    "type": "integer",
    "description": "最大结果数",
    "minimum": 1,
    "maximum": 100,
    "default": 10
}

# number - 浮点数
{
    "type": "number",
    "description": "温度参数",
    "minimum": 0.0,
    "maximum": 2.0,
    "default": 0.7
}

# boolean - 布尔值
{
    "type": "boolean",
    "description": "是否包含图片",
    "default": false
}
```

### 复杂类型

```python
# array - 数组
{
    "type": "array",
    "description": "标签列表",
    "items": {
        "type": "string"
    },
    "minItems": 1,
    "maxItems": 10
}

# object - 嵌套对象
{
    "type": "object",
    "description": "过滤条件",
    "properties": {
        "date_from": {"type": "string"},
        "date_to": {"type": "string"}
    },
    "required": ["date_from"]
}
```

---

## 🆚 OpenAI vs Anthropic 格式对比

### OpenAI 格式

```python
{
    "type": "function",           # ← 需要
    "function": {
        "name": "search_tool",
        "description": "搜索工具",
        "parameters": {           # ← 关键字: parameters
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
}
```

### Anthropic 格式

```python
{
    # 没有 type 字段
    "name": "search_tool",
    "description": "搜索工具",
    "input_schema": {             # ← 关键字: input_schema
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
```

### 主要差异

| 特性 | OpenAI | Anthropic |
|------|--------|-----------|
| 顶层 `type` 字段 | ✅ 必需 | ❌ 不需要 |
| 参数对象名称 | `parameters` | `input_schema` |
| 嵌套结构 | `type.function.*` | 扁平结构 |

---

## 🚀 三种实现方式对比

### 1. OpenAI 原生（手动多轮）

```python
from openai import OpenAI

client = OpenAI()
messages = [{"role": "user", "content": "搜索 GPT-4"}]

# 需要手动循环
for turn in range(5):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )
    
    if response.choices[0].message.tool_calls:
        # 执行工具
        # 添加结果到 messages
        # 继续循环
    else:
        break
```

**优点：** 精细控制  
**缺点：** 代码复杂（~50 行）

### 2. Anthropic 原生（手动多轮）

```python
from anthropic import Anthropic

client = Anthropic()
messages = [{"role": "user", "content": "搜索 GPT-4"}]

# 需要手动循环
for turn in range(5):
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=tools,
        messages=messages
    )
    
    if response.stop_reason == "tool_use":
        # 执行工具
        # 添加结果到 messages
        # 继续循环
    else:
        break
```

**优点：** Claude 的强大工具调用能力  
**缺点：** 代码复杂（~60 行），格式不同

### 3. aisuite 统一（自动多轮）✅ 推荐

```python
from aisuite import Client

client = Client()

response = client.chat.completions.create(
    model="openai:gpt-4o-mini",  # 或 "anthropic:claude-3-5-sonnet"
    messages=[{"role": "user", "content": "搜索 GPT-4"}],
    tools=tools,
    max_turns=5,  # 🔥 自动处理多轮
    temperature=0
)

final_answer = response.choices[0].message.content
```

**优点：** 
- ✅ 代码简洁（~10 行）
- ✅ 自动多轮处理
- ✅ 统一接口
- ✅ 多模型支持

**缺点：** 
- ❌ 灵活性略低

---

## 📊 对比总结表

| 特性 | OpenAI 原生 | Anthropic 原生 | aisuite |
|------|------------|---------------|---------|
| 多轮处理 | ❌ 手动 | ❌ 手动 | ✅ 自动 |
| 代码行数 | ~50 行 | ~60 行 | ~10 行 |
| 工具格式 | parameters | input_schema | parameters |
| 模型切换 | ❌ 需重写 | ❌ 需重写 | ✅ 改参数 |
| 学习曲线 | 中 | 中 | 低 |
| 推荐场景 | 精细控制 | Claude 特性 | 快速开发 ✅ |

---

## 💡 最佳实践

### 1. 工具描述要清晰

❌ **不好**
```python
"description": "搜索工具"
```

✅ **好**
```python
"description": "使用 Tavily API 搜索网络，获取最新的新闻、博客、网站内容。适用于需要实时信息的场景。"
```

### 2. 参数命名要合理

❌ **不好**
```python
"q": {"type": "string"}  # 太简短
```

✅ **好**
```python
"query": {
    "type": "string",
    "description": "搜索关键词"
}
```

### 3. 只标记真正必需的参数

```python
"required": ["query"]  # query 必需
# max_results 有默认值，不必需
```

### 4. 使用工具映射表

```python
TOOL_MAPPING = {
    "tavily_search_tool": tavily_search_tool,
    "arxiv_search_tool": arxiv_search_tool,
}

# 动态调用
function_to_call = TOOL_MAPPING[function_name]
result = function_to_call(**function_args)
```

---

## 🔍 实际项目示例

### 当前项目的工具定义

```python
# src/research_tools.py

# Tavily 搜索工具
tavily_tool_def = {
    "type": "function",
    "function": {
        "name": "tavily_search_tool",
        "description": "Performs a general-purpose web search using the Tavily API.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for retrieving information from the web.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "default": 5,
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Whether to include image results.",
                    "default": False,
                },
            },
            "required": ["query"],
        },
    },
}

# 实际函数
def tavily_search_tool(query: str, max_results: int = 5, include_images: bool = False):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(query=query, max_results=max_results, include_images=include_images)
    return response.get("results", [])
```

### 在 aisuite 中使用

```python
# src/agents.py

from aisuite import Client

client = Client()

response = client.chat.completions.create(
    model="openai:gpt-4.1-mini",
    messages=[{"role": "user", "content": prompt}],
    tools=[tavily_search_tool, arxiv_search_tool, wikipedia_search_tool],
    tool_choice="auto",
    max_turns=5,  # 自动处理多轮工具调用
    temperature=0.0
)
```

---

## 🎓 学习路径

### 初级：理解基础概念
1. 阅读 `tool_calling_deep_dive.md`
2. 运行 `tool_calling_flow.py` 查看完整流程
3. 理解工具定义的参数结构

### 中级：实践不同实现
1. 运行 `tool_calling_examples.py` 对比三种方式
2. 修改工具定义，测试不同参数类型
3. 实现自己的工具函数

### 高级：优化生产应用
1. 研究 `tool_calling_comparison.py` 的性能对比
2. 实现智能模型路由（根据任务选择最佳模型）
3. 添加缓存、监控、错误处理

---

## 🐛 常见问题

### Q1: LLM 不调用我的工具？

**原因：**
- 工具描述不清晰
- 用户输入与工具功能不匹配

**解决：**
```python
# 强制调用
tool_choice={"type": "function", "function": {"name": "my_tool"}}
```

### Q2: 工具调用参数格式错误？

**解决：**
```python
try:
    args = json.loads(tool_call.function.arguments)
except json.JSONDecodeError:
    args = {}
```

### Q3: 如何限制工具调用次数？

**解决：**
```python
# aisuite
max_turns=3

# 手动实现
for turn in range(3):
    ...
```

---

## 📖 推荐阅读顺序

1. **快速入门** → 本文档（TOOL_CALLING_SUMMARY.md）
2. **理论深入** → tool_calling_deep_dive.md
3. **流程演示** → tool_calling_flow.py
4. **代码示例** → tool_calling_examples.py
5. **实现对比** → tool_calling_comparison.py

---

## 🎯 关键要点

1. **工具调用本质**：LLM 生成 JSON，你执行函数
2. **一级参数**：`type`, `function.name`, `function.description`, `function.parameters`
3. **格式差异**：OpenAI 用 `parameters`，Anthropic 用 `input_schema`
4. **aisuite 优势**：统一接口 + 自动多轮（`max_turns`）
5. **最佳实践**：清晰描述 + 合理参数 + 完善错误处理

---

## 📞 联系与反馈

如有问题或建议，请参考项目文档或提交 Issue。

**Happy Coding! 🚀**
