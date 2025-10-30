# 大模型工具调用（Function Calling）深度解析

## 目录
1. 工具调用的本质原理
2. OpenAI Function Calling 实现
3. Anthropic Claude Tool Use 实现
4. aisuite 的统一抽象
5. 工具定义的标准格式
6. 实际执行流程


---

## 1. 工具调用的本质原理

### 核心概念

**工具调用不是真正的"调用"，而是 LLM 生成的结构化输出**

```
用户输入 → LLM 推理 → 生成工具调用 JSON → 你的代码执行工具 → 结果返回 LLM → 最终回复
```

### 底层机制

1. **训练阶段**：模型被训练成能够生成特定格式的 JSON
2. **推理阶段**：模型根据工具定义，决定是否需要调用工具
3. **执行阶段**：你的代码解析 JSON，执行实际函数，返回结果
4. **合成阶段**：LLM 基于工具结果生成最终回复


---

## 2. 工具定义的一级参数结构

### 完整的参数层级

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
          "default": "默认值",            // 【五级】可选
          "enum": ["选项1", "选项2"]      // 【五级】可选
        }
      },
      "required": ["param1"]             // 【三级】必需参数列表（可选）
    }
  }
}
```

### 一级参数详解

| 参数名 | 层级 | 类型 | 必需 | 说明 |
|--------|------|------|------|------|
| `type` | 1 | string | ✅ | 固定值 "function" |
| `function` | 1 | object | ✅ | 函数定义对象 |
| `function.name` | 2 | string | ✅ | 函数名称，必须与 Python 函数名匹配 |
| `function.description` | 2 | string | ✅ | 函数描述，帮助 LLM 理解何时使用 |
| `function.parameters` | 2 | object | ✅ | 参数定义对象（JSON Schema） |
| `parameters.type` | 3 | string | ✅ | 固定值 "object" |
| `parameters.properties` | 3 | object | ✅ | 每个参数的详细定义 |
| `parameters.required` | 3 | array | ❌ | 必需参数名称列表 |

---

## 3. OpenAI vs Anthropic 格式对比

### OpenAI 格式

```python
openai_tool = {
    "type": "function",
    "function": {
        "name": "search_tool",
        "description": "搜索工具",
        "parameters": {              # ← 关键字: parameters
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}
```

### Anthropic 格式

```python
anthropic_tool = {
    "name": "search_tool",           # ← 没有 type 字段
    "description": "搜索工具",
    "input_schema": {                # ← 关键字: input_schema（不是 parameters）
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
}
```

### 主要差异

| 特性 | OpenAI | Anthropic |
|------|--------|-----------|
| 顶层 type 字段 | ✅ 需要 | ❌ 不需要 |
| 参数对象名称 | `parameters` | `input_schema` |
| 嵌套结构 | `type.function.*` | 扁平结构 |

---

## 4. 参数类型完整说明

### 4.1 基础类型

```python
# string - 字符串
{
    "param_name": {
        "type": "string",
        "description": "参数描述",
        "minLength": 1,           # 最小长度
        "maxLength": 500,         # 最大长度
        "pattern": "^[a-z]+$",    # 正则表达式
        "enum": ["opt1", "opt2"], # 枚举值
        "default": "默认值"
    }
}

# integer - 整数
{
    "param_name": {
        "type": "integer",
        "description": "参数描述",
        "minimum": 1,             # 最小值
        "maximum": 100,           # 最大值
        "default": 10
    }
}

# number - 浮点数
{
    "param_name": {
        "type": "number",
        "description": "参数描述",
        "minimum": 0.0,
        "maximum": 1.0,
        "default": 0.5
    }
}

# boolean - 布尔值
{
    "param_name": {
        "type": "boolean",
        "description": "参数描述",
        "default": False
    }
}
```

### 4.2 复杂类型

```python
# array - 数组
{
    "tags": {
        "type": "array",
        "description": "标签列表",
        "items": {
            "type": "string"      # 数组元素类型
        },
        "minItems": 1,            # 最少元素数
        "maxItems": 10            # 最多元素数
    }
}

# object - 嵌套对象
{
    "filters": {
        "type": "object",
        "description": "过滤条件",
        "properties": {
            "date_from": {"type": "string"},
            "date_to": {"type": "string"}
        },
        "required": ["date_from"]
    }
}
```

---

## 5. 实际工具调用流程

### 5.1 单轮工具调用

```
用户: "搜索 GPT-4"
  ↓
LLM 第一次调用
  ↓
返回: tool_calls = [{name: "search", args: {query: "GPT-4"}}]
  ↓
执行 Python 函数: search(query="GPT-4")
  ↓
返回结果: [{title: "...", url: "..."}]
  ↓
LLM 第二次调用（带结果）
  ↓
返回: "我找到了关于 GPT-4 的信息..."
```

### 5.2 多轮工具调用

```
用户: "搜索 GPT-4 并总结"
  ↓
【第 1 轮】
LLM: 调用 search(query="GPT-4")
执行: 返回搜索结果
  ↓
【第 2 轮】
LLM: 调用 summarize(text="搜索结果...")
执行: 返回摘要
  ↓
【第 3 轮】
LLM: 生成最终回复
```

---

## 6. aisuite 的 max_turns 参数

### 工作原理

```python
response = client.chat.completions.create(
    model="openai:gpt-4o-mini",
    messages=[...],
    tools=[...],
    max_turns=5  # 🔥 最多自动执行 5 轮工具调用
)
```

### 执行流程

```
max_turns=5 的执行过程:

Turn 1: LLM 决定调用 tool_A → 执行 → 返回结果
Turn 2: LLM 基于结果决定调用 tool_B → 执行 → 返回结果
Turn 3: LLM 基于结果决定调用 tool_C → 执行 → 返回结果
Turn 4: LLM 决定不再调用工具 → 生成最终回复 → 结束

（实际只用了 4 轮，因为第 4 轮就完成了）
```

### 优势

- ✅ 自动处理多轮工具调用
- ✅ 无需手动循环
- ✅ 统一的 API 接口
- ✅ 支持多个模型提供商

---

## 7. 工具执行的关键代码

### 7.1 工具映射表

```python
# 关键：建立工具名称到实际函数的映射
TOOL_MAPPING = {
    "tavily_search_tool": tavily_search_tool,
    "arxiv_search_tool": arxiv_search_tool,
    "wikipedia_search_tool": wikipedia_search_tool,
}

# 执行工具
function_name = "tavily_search_tool"
function_args = {"query": "GPT-4", "max_results": 5}

# 动态调用
function_to_call = TOOL_MAPPING[function_name]
result = function_to_call(**function_args)
```

### 7.2 手动实现多轮调用

```python
messages = [{"role": "user", "content": "搜索 GPT-4"}]

for turn in range(5):  # 最多 5 轮
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )
    
    if response.choices[0].message.tool_calls:
        # 有工具调用
        messages.append(response.choices[0].message)
        
        for tool_call in response.choices[0].message.tool_calls:
            # 执行工具
            result = execute_tool(tool_call)
            
            # 添加结果
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
    else:
        # 没有工具调用，结束
        break
```

---

## 8. 最佳实践

### 8.1 工具描述的写法

❌ **不好的描述**
```python
"description": "搜索工具"
```

✅ **好的描述**
```python
"description": "使用 Tavily API 搜索网络，获取最新的新闻、博客、网站内容。适用于需要实时信息的场景。"
```

### 8.2 参数命名

❌ **不好的命名**
```python
"q": {"type": "string"}  # 太简短
"search_query_string": {"type": "string"}  # 太冗长
```

✅ **好的命名**
```python
"query": {"type": "string", "description": "搜索关键词"}
```

### 8.3 必需参数的选择

```python
# 原则：只将真正必需的参数标记为 required
"required": ["query"]  # query 必需
# max_results 有默认值，不必需
```

---

## 9. 调试技巧

### 9.1 查看工具调用历史

```python
# aisuite 提供的调试信息
response = client.chat.completions.create(...)

# 查看中间消息
for msg in response.choices[0].message.intermediate_messages:
    if hasattr(msg, 'tool_calls'):
        for tc in msg.tool_calls:
            print(f"调用: {tc.function.name}")
            print(f"参数: {tc.function.arguments}")
```

### 9.2 日志记录

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# 记录每次工具调用
def execute_tool_with_logging(name, args):
    logging.info(f"执行工具: {name}")
    logging.debug(f"参数: {args}")
    
    result = TOOL_MAPPING[name](**args)
    
    logging.info(f"结果: {len(result)} 条")
    return result
```

---

## 10. 常见问题

### Q1: 为什么 LLM 不调用我的工具？

**可能原因：**
1. 工具描述不清晰
2. 用户输入与工具功能不匹配
3. `tool_choice` 设置为 "none"

**解决方案：**
```python
# 强制调用特定工具
tool_choice={"type": "function", "function": {"name": "my_tool"}}
```

### Q2: 工具调用参数格式错误怎么办？

**解决方案：**
```python
try:
    args = json.loads(tool_call.function.arguments)
except json.JSONDecodeError:
    # 处理解析错误
    args = {}
```

### Q3: 如何限制工具调用次数？

**解决方案：**
```python
# 使用 max_turns 参数
response = client.chat.completions.create(
    max_turns=3  # 最多 3 轮
)
```

---

## 总结

### 核心要点

1. **工具调用本质**：LLM 生成结构化 JSON，你的代码执行实际函数
2. **一级参数**：`type`, `function.name`, `function.description`, `function.parameters`
3. **格式差异**：OpenAI 用 `parameters`，Anthropic 用 `input_schema`
4. **aisuite 优势**：统一接口 + 自动多轮调用（`max_turns`）
5. **最佳实践**：清晰的描述 + 合理的参数设计 + 完善的错误处理
