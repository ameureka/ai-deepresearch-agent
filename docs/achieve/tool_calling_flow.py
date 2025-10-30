"""
工具调用完整流程可视化
展示从用户输入到最终输出的每一步
"""

import json

# ============================================================
# 完整的工具调用流程示例
# ============================================================

def complete_tool_calling_flow():
    """
    完整展示一次工具调用的所有步骤
    """
    
    print("=" * 80)
    print("工具调用完整流程演示")
    print("=" * 80)
    
    # ===== 步骤 1: 用户输入 =====
    print("\n【步骤 1】用户输入")
    print("-" * 80)
    user_input = "搜索关于 GPT-4 的最新研究论文"
    print(f"用户: {user_input}")
    
    # ===== 步骤 2: 构造初始消息 =====
    print("\n【步骤 2】构造消息历史")
    print("-" * 80)
    messages = [
        {
            "role": "user",
            "content": user_input
        }
    ]
    print(json.dumps(messages, indent=2, ensure_ascii=False))
    
    # ===== 步骤 3: 定义可用工具 =====
    print("\n【步骤 3】定义可用工具")
    print("-" * 80)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "arxiv_search_tool",
                "description": "搜索 arXiv 学术论文数据库",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "最大结果数",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    print(f"可用工具: {tools[0]['function']['name']}")
    print(f"工具描述: {tools[0]['function']['description']}")
    
    # ===== 步骤 4: 第一次 LLM 调用 =====
    print("\n【步骤 4】第一次调用 LLM（决策阶段）")
    print("-" * 80)
    print("发送给 LLM 的内容:")
    print(f"  - 消息历史: {len(messages)} 条")
    print(f"  - 可用工具: {len(tools)} 个")
    print(f"  - tool_choice: auto (让模型自己决定)")
    
    # ===== 步骤 5: LLM 返回工具调用 =====
    print("\n【步骤 5】LLM 决定调用工具")
    print("-" * 80)
    
    # 模拟 LLM 的响应
    llm_response = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,  # 当调用工具时，content 为 None
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "arxiv_search_tool",
                                "arguments": '{"query": "GPT-4", "max_results": 5}'
                            }
                        }
                    ]
                },
                "finish_reason": "tool_calls"
            }
        ]
    }
    
    print("LLM 响应:")
    print(json.dumps(llm_response["choices"][0]["message"], indent=2, ensure_ascii=False))
    
    # ===== 步骤 6: 解析工具调用 =====
    print("\n【步骤 6】解析工具调用参数")
    print("-" * 80)
    
    tool_call = llm_response["choices"][0]["message"]["tool_calls"][0]
    function_name = tool_call["function"]["name"]
    function_args = json.loads(tool_call["function"]["arguments"])
    
    print(f"工具名称: {function_name}")
    print(f"工具参数: {json.dumps(function_args, indent=2, ensure_ascii=False)}")
    print(f"调用 ID: {tool_call['id']}")
    
    # ===== 步骤 7: 执行实际的 Python 函数 =====
    print("\n【步骤 7】执行实际的 Python 函数")
    print("-" * 80)
    
    # 模拟函数执行
    def arxiv_search_tool(query: str, max_results: int = 3):
        """实际的搜索函数"""
        print(f"  → 正在搜索 arXiv: query='{query}', max_results={max_results}")
        # 模拟返回结果
        return [
            {
                "title": "GPT-4 Technical Report",
                "authors": ["OpenAI"],
                "published": "2023-03-15",
                "url": "https://arxiv.org/abs/2303.08774",
                "summary": "We report the development of GPT-4..."
            },
            {
                "title": "Sparks of Artificial General Intelligence",
                "authors": ["Bubeck et al."],
                "published": "2023-03-22",
                "url": "https://arxiv.org/abs/2303.12712",
                "summary": "Early experiments with GPT-4..."
            }
        ]
    
    # 执行函数
    function_result = arxiv_search_tool(**function_args)
    
    print(f"  ✅ 找到 {len(function_result)} 条结果")
    print(f"\n工具返回结果:")
    print(json.dumps(function_result, indent=2, ensure_ascii=False))
    
    # ===== 步骤 8: 构造工具结果消息 =====
    print("\n【步骤 8】构造工具结果消息")
    print("-" * 80)
    
    # 将 LLM 的工具调用添加到历史
    messages.append(llm_response["choices"][0]["message"])
    
    # 添加工具执行结果
    tool_message = {
        "tool_call_id": tool_call["id"],
        "role": "tool",
        "name": function_name,
        "content": json.dumps(function_result, ensure_ascii=False)
    }
    messages.append(tool_message)
    
    print("更新后的消息历史:")
    print(f"  1. user: {messages[0]['content'][:50]}...")
    print(f"  2. assistant: [调用工具 {function_name}]")
    print(f"  3. tool: [返回 {len(function_result)} 条结果]")
    
    # ===== 步骤 9: 第二次 LLM 调用 =====
    print("\n【步骤 9】第二次调用 LLM（合成阶段）")
    print("-" * 80)
    print("发送给 LLM 的内容:")
    print(f"  - 消息历史: {len(messages)} 条（包含工具结果）")
    print(f"  - 不再提供 tools 参数")
    
    # ===== 步骤 10: LLM 生成最终回复 =====
    print("\n【步骤 10】LLM 基于工具结果生成回复")
    print("-" * 80)
    
    final_response = {
        "id": "chatcmpl-456",
        "object": "chat.completion",
        "created": 1677652290,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": """我找到了关于 GPT-4 的最新研究论文：

1. **GPT-4 Technical Report** (OpenAI, 2023-03-15)
   - 链接: https://arxiv.org/abs/2303.08774
   - 摘要: 这是 OpenAI 发布的 GPT-4 技术报告...

2. **Sparks of Artificial General Intelligence** (Bubeck et al., 2023-03-22)
   - 链接: https://arxiv.org/abs/2303.12712
   - 摘要: 这篇论文探讨了 GPT-4 在早期实验中展现的 AGI 特征...

这些是 arXiv 上关于 GPT-4 的重要研究论文。"""
                },
                "finish_reason": "stop"
            }
        ]
    }
    
    final_answer = final_response["choices"][0]["message"]["content"]
    print(f"最终回复:\n{final_answer}")
    
    # ===== 步骤 11: 返回给用户 =====
    print("\n【步骤 11】返回给用户")
    print("-" * 80)
    print("✅ 工具调用流程完成")
    
    return final_answer


# ============================================================
# 工具参数的一级结构详解
# ============================================================

def explain_tool_parameters():
    """
    详细解释工具定义中的每个参数
    """
    
    print("\n" + "=" * 80)
    print("工具定义参数详解")
    print("=" * 80)
    
    tool_structure = {
        # ===== 顶层结构 =====
        "type": {
            "value": "function",
            "required": True,
            "description": "固定值，表示这是一个函数工具"
        },
        
        # ===== function 对象（核心）=====
        "function": {
            "required": True,
            "description": "函数定义对象",
            "fields": {
                # --- 一级参数 ---
                "name": {
                    "type": "string",
                    "required": True,
                    "description": "函数名称，必须与实际 Python 函数名匹配",
                    "example": "tavily_search_tool",
                    "rules": [
                        "只能包含字母、数字、下划线",
                        "不能以数字开头",
                        "建议使用 snake_case 命名"
                    ]
                },
                
                "description": {
                    "type": "string",
                    "required": True,
                    "description": "函数的详细描述，帮助 LLM 理解何时使用这个工具",
                    "example": "Search the web using Tavily API for current information",
                    "best_practices": [
                        "清晰描述工具的功能",
                        "说明适用场景",
                        "提及数据来源",
                        "避免模糊表述"
                    ]
                },
                
                "parameters": {
                    "type": "object",
                    "required": True,
                    "description": "参数定义对象（JSON Schema 格式）",
                    "fields": {
                        # --- 二级参数 ---
                        "type": {
                            "value": "object",
                            "required": True,
                            "description": "固定为 'object'，表示参数是一个对象"
                        },
                        
                        "properties": {
                            "type": "object",
                            "required": True,
                            "description": "定义每个参数的详细信息",
                            "structure": {
                                "param_name": {
                                    "type": "string/integer/boolean/array/object",
                                    "description": "参数描述",
                                    "enum": ["可选：枚举值"],
                                    "default": "可选：默认值",
                                    "minimum": "可选：最小值（数值类型）",
                                    "maximum": "可选：最大值（数值类型）",
                                    "minLength": "可选：最小长度（字符串）",
                                    "maxLength": "可选：最大长度（字符串）",
                                    "pattern": "可选：正则表达式（字符串）",
                                    "items": "可选：数组元素类型（array 类型）",
                                }
                            }
                        },
                        
                        "required": {
                            "type": "array",
                            "required": False,
                            "description": "必需参数列表",
                            "example": ["query", "api_key"]
                        },
                        
                        "additionalProperties": {
                            "type": "boolean",
                            "required": False,
                            "description": "是否允许额外的未定义参数",
                            "default": False
                        }
                    }
                }
            }
        }
    }
    
    print("\n一级参数结构:")
    print("-" * 80)
    print("""
    {
        "type": "function",           # 固定值
        "function": {                 # 函数定义对象
            "name": "...",            # 【必需】函数名称
            "description": "...",     # 【必需】函数描述
            "parameters": {           # 【必需】参数定义
                "type": "object",     # 固定值
                "properties": {...},  # 【必需】参数详情
                "required": [...]     # 【可选】必需参数
            }
        }
    }
    """)
    
    print("\nparameters.properties 中的参数类型:")
    print("-" * 80)
    
    parameter_types = {
        "string": {
            "description": "字符串类型",
            "example": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词",
                    "minLength": 1,
                    "maxLength": 500,
                    "pattern": "^[a-zA-Z0-9\\s]+$"
                }
            }
        },
        "integer": {
            "description": "整数类型",
            "example": {
                "max_results": {
                    "type": "integer",
                    "description": "最大结果数",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10
                }
            }
        },
        "number": {
            "description": "浮点数类型",
            "example": {
                "temperature": {
                    "type": "number",
                    "description": "温度参数",
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "default": 0.7
                }
            }
        },
        "boolean": {
            "description": "布尔类型",
            "example": {
                "include_images": {
                    "type": "boolean",
                    "description": "是否包含图片",
                    "default": False
                }
            }
        },
        "array": {
            "description": "数组类型",
            "example": {
                "tags": {
                    "type": "array",
                    "description": "标签列表",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 1,
                    "maxItems": 10
                }
            }
        },
        "object": {
            "description": "嵌套对象类型",
            "example": {
                "filters": {
                    "type": "object",
                    "description": "过滤条件",
                    "properties": {
                        "date_from": {"type": "string"},
                        "date_to": {"type": "string"}
                    }
                }
            }
        },
        "enum": {
            "description": "枚举类型（限制可选值）",
            "example": {
                "sort_by": {
                    "type": "string",
                    "description": "排序方式",
                    "enum": ["relevance", "date", "citations"]
                }
            }
        }
    }
    
    for param_type, info in parameter_types.items():
        print(f"\n{param_type.upper()}:")
        print(f"  描述: {info['description']}")
        print(f"  示例:")
        print(json.dumps(info['example'], indent=4, ensure_ascii=False))


# ============================================================
# 实际项目中的工具定义对比
# ============================================================

def compare_tool_definitions():
    """
    对比不同工具的定义方式
    """
    
    print("\n" + "=" * 80)
    print("实际项目工具定义对比")
    print("=" * 80)
    
    # 简单工具：Wikipedia
    simple_tool = {
        "type": "function",
        "function": {
            "name": "wikipedia_search_tool",
            "description": "Searches for a Wikipedia article summary by query string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keywords for the Wikipedia article.",
                    },
                    "sentences": {
                        "type": "integer",
                        "description": "Number of sentences in the summary.",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    }
    
    print("\n【简单工具】Wikipedia 搜索")
    print("-" * 80)
    print(f"参数数量: {len(simple_tool['function']['parameters']['properties'])}")
    print(f"必需参数: {simple_tool['function']['parameters']['required']}")
    print(json.dumps(simple_tool, indent=2, ensure_ascii=False))
    
    # 复杂工具：Tavily
    complex_tool = {
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
    
    print("\n【复杂工具】Tavily 搜索")
    print("-" * 80)
    print(f"参数数量: {len(complex_tool['function']['parameters']['properties'])}")
    print(f"必需参数: {complex_tool['function']['parameters']['required']}")
    print(json.dumps(complex_tool, indent=2, ensure_ascii=False))


# ============================================================
# 运行演示
# ============================================================

if __name__ == "__main__":
    # 1. 完整流程演示
    complete_tool_calling_flow()
    
    # 2. 参数详解
    explain_tool_parameters()
    
    # 3. 工具定义对比
    compare_tool_definitions()
