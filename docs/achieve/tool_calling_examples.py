"""
工具调用（Function Calling）完整实现示例
展示 OpenAI、Anthropic、aisuite 三种方式
"""

import json
import requests
from typing import List, Dict, Any

# ============================================================
# Part 1: 工具定义的标准格式
# ============================================================

# OpenAI 格式（JSON Schema）
openai_tool_definition = {
    "type": "function",
    "function": {
        "name": "tavily_search_tool",
        "description": "Search the web using Tavily API for current information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Whether to include image results",
                    "default": False
                }
            },
            "required": ["query"]
        }
    }
}

# Anthropic 格式（略有不同）
anthropic_tool_definition = {
    "name": "tavily_search_tool",
    "description": "Search the web using Tavily API for current information",
    "input_schema": {  # 注意：这里是 input_schema 而不是 parameters
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 5
            },
            "include_images": {
                "type": "boolean",
                "description": "Whether to include image results",
                "default": False
            }
        },
        "required": ["query"]
    }
}


# ============================================================
# Part 2: 实际工具函数实现
# ============================================================

def tavily_search_tool(query: str, max_results: int = 5, include_images: bool = False) -> List[Dict]:
    """
    实际执行搜索的函数
    这是真正被调用的 Python 函数
    """
    import os
    from tavily import TavilyClient
    
    api_key = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(api_key)
    
    try:
        response = client.search(
            query=query,
            max_results=max_results,
            include_images=include_images
        )
        
        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", "")
            })
        
        return results
    
    except Exception as e:
        return [{"error": str(e)}]


def arxiv_search_tool(query: str, max_results: int = 3) -> List[Dict]:
    """arXiv 搜索工具"""
    # 实现细节见 src/research_tools.py
    pass


def wikipedia_search_tool(query: str, sentences: int = 5) -> List[Dict]:
    """Wikipedia 搜索工具"""
    # 实现细节见 src/research_tools.py
    pass


# 工具映射表（关键！）
TOOL_MAPPING = {
    "tavily_search_tool": tavily_search_tool,
    "arxiv_search_tool": arxiv_search_tool,
    "wikipedia_search_tool": wikipedia_search_tool,
}


# ============================================================
# Part 3: OpenAI 原生实现（手动处理）
# ============================================================

from openai import OpenAI

def openai_manual_tool_calling():
    """
    OpenAI 手动实现工具调用
    展示底层工作原理
    """
    client = OpenAI()
    
    # 1. 定义工具
    tools = [
        openai_tool_definition,
        # 可以添加更多工具...
    ]
    
    # 2. 初始消息
    messages = [
        {"role": "user", "content": "搜索关于 Large Language Models 的最新信息"}
    ]
    
    print("=" * 60)
    print("第一轮：LLM 决定是否调用工具")
    print("=" * 60)
    
    # 3. 第一次调用 LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"  # 让模型自己决定
    )
    
    response_message = response.choices[0].message
    
    # 4. 检查是否有工具调用
    if response_message.tool_calls:
        print(f"✅ LLM 决定调用 {len(response_message.tool_calls)} 个工具\n")
        
        # 将 LLM 的响应添加到消息历史
        messages.append(response_message)
        
        # 5. 执行每个工具调用
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"📞 调用工具: {function_name}")
            print(f"📝 参数: {json.dumps(function_args, indent=2, ensure_ascii=False)}")
            
            # 6. 执行实际的 Python 函数
            function_to_call = TOOL_MAPPING[function_name]
            function_response = function_to_call(**function_args)
            
            print(f"✅ 工具返回: {len(function_response)} 条结果\n")
            
            # 7. 将工具结果添加到消息历史
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response, ensure_ascii=False)
            })
        
        print("=" * 60)
        print("第二轮：LLM 基于工具结果生成回复")
        print("=" * 60)
        
        # 8. 第二次调用 LLM（带工具结果）
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        final_answer = second_response.choices[0].message.content
        print(f"🎯 最终回复:\n{final_answer}\n")
        
        return final_answer
    
    else:
        print("❌ LLM 决定不调用工具，直接回复")
        return response_message.content


# ============================================================
# Part 4: Anthropic Claude 原生实现
# ============================================================

from anthropic import Anthropic

def anthropic_manual_tool_calling():
    """
    Anthropic Claude 手动实现工具调用
    格式与 OpenAI 略有不同
    """
    client = Anthropic()
    
    # 1. 定义工具（注意格式差异）
    tools = [
        anthropic_tool_definition,
        # 可以添加更多工具...
    ]
    
    # 2. 初始消息
    messages = [
        {"role": "user", "content": "搜索关于 Large Language Models 的最新信息"}
    ]
    
    print("=" * 60)
    print("Claude 工具调用流程")
    print("=" * 60)
    
    # 3. 多轮对话循环（Claude 需要手动实现）
    max_turns = 5
    
    for turn in range(max_turns):
        print(f"\n--- 第 {turn + 1} 轮 ---")
        
        # 4. 调用 Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        print(f"Stop reason: {response.stop_reason}")
        
        # 5. 检查停止原因
        if response.stop_reason == "tool_use":
            # 将 Claude 的响应添加到历史
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # 6. 处理工具调用
            tool_results = []
            
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    
                    print(f"📞 调用工具: {tool_name}")
                    print(f"📝 参数: {json.dumps(tool_input, indent=2, ensure_ascii=False)}")
                    
                    # 7. 执行实际函数
                    function_to_call = TOOL_MAPPING[tool_name]
                    function_response = function_to_call(**tool_input)
                    
                    print(f"✅ 工具返回: {len(function_response)} 条结果")
                    
                    # 8. 构造工具结果（注意格式）
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": json.dumps(function_response, ensure_ascii=False)
                    })
            
            # 9. 将工具结果添加到消息历史
            messages.append({
                "role": "user",
                "content": tool_results
            })
        
        elif response.stop_reason == "end_turn":
            # 10. 获取最终文本回复
            final_text = ""
            for content_block in response.content:
                if hasattr(content_block, "text"):
                    final_text += content_block.text
            
            print(f"\n🎯 最终回复:\n{final_text}")
            return final_text
        
        else:
            print(f"⚠️ 未预期的停止原因: {response.stop_reason}")
            break
    
    return "达到最大轮次限制"


# ============================================================
# Part 5: aisuite 统一实现（推荐）
# ============================================================

from aisuite import Client

def aisuite_unified_tool_calling(model="openai:gpt-4o-mini"):
    """
    aisuite 统一接口
    自动处理多轮工具调用
    """
    client = Client()
    
    # 1. 定义工具（使用 OpenAI 格式）
    tools = [
        openai_tool_definition,
        # aisuite 会自动转换为目标模型的格式
    ]
    
    print("=" * 60)
    print(f"aisuite 统一接口 (模型: {model})")
    print("=" * 60)
    
    # 2. 一次调用，自动处理多轮
    response = client.chat.completions.create(
        model=model,  # 可以是 "openai:gpt-4o-mini" 或 "anthropic:claude-3-5-sonnet"
        messages=[
            {"role": "user", "content": "搜索关于 Large Language Models 的最新信息"}
        ],
        tools=tools,
        tool_choice="auto",
        max_turns=5,  # 🔥 关键参数：自动处理最多 5 轮工具调用
        temperature=0
    )
    
    # 3. 直接获取最终结果
    final_answer = response.choices[0].message.content
    
    print(f"🎯 最终回复:\n{final_answer}\n")
    
    # 4. 查看工具调用历史（如果需要）
    if hasattr(response.choices[0].message, 'intermediate_messages'):
        print("=" * 60)
        print("工具调用历史:")
        print("=" * 60)
        
        for msg in response.choices[0].message.intermediate_messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"📞 {tc.function.name}({tc.function.arguments})")
    
    return final_answer


# ============================================================
# Part 6: 工具参数的详细解析
# ============================================================

def analyze_tool_parameters():
    """
    分析工具定义中的参数结构
    """
    print("=" * 60)
    print("工具参数结构详解")
    print("=" * 60)
    
    tool_def = {
        "type": "function",  # 固定值
        "function": {
            # ===== 一级参数 =====
            "name": "tool_name",  # 工具名称（必需）
            "description": "工具的详细描述，帮助 LLM 理解何时使用",  # 描述（必需）
            
            # ===== parameters 对象（核心）=====
            "parameters": {
                "type": "object",  # 固定为 object
                
                # ===== properties：定义每个参数 =====
                "properties": {
                    "param1": {
                        "type": "string",  # 类型：string, integer, boolean, array, object
                        "description": "参数1的描述",
                        "enum": ["option1", "option2"],  # 可选：枚举值
                    },
                    "param2": {
                        "type": "integer",
                        "description": "参数2的描述",
                        "minimum": 1,  # 可选：最小值
                        "maximum": 100,  # 可选：最大值
                        "default": 10  # 可选：默认值
                    },
                    "param3": {
                        "type": "array",
                        "description": "参数3是数组",
                        "items": {
                            "type": "string"  # 数组元素类型
                        }
                    },
                    "param4": {
                        "type": "object",
                        "description": "参数4是嵌套对象",
                        "properties": {
                            "nested_field": {
                                "type": "string"
                            }
                        }
                    }
                },
                
                # ===== required：必需参数列表 =====
                "required": ["param1", "param2"]
            }
        }
    }
    
    print(json.dumps(tool_def, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("参数类型说明:")
    print("=" * 60)
    print("""
    1. string   - 字符串
    2. integer  - 整数
    3. number   - 浮点数
    4. boolean  - 布尔值
    5. array    - 数组（需要定义 items）
    6. object   - 对象（需要定义 properties）
    7. null     - 空值
    
    常用约束:
    - enum: 限制可选值
    - minimum/maximum: 数值范围
    - minLength/maxLength: 字符串长度
    - pattern: 正则表达式
    - default: 默认值
    """)


# ============================================================
# Part 7: 实际项目中的工具定义示例
# ============================================================

# 从当前项目提取的实际工具定义
ACTUAL_TOOLS = [
    # Tavily 搜索
    {
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
    },
    
    # arXiv 搜索
    {
        "type": "function",
        "function": {
            "name": "arxiv_search_tool",
            "description": "Searches arXiv and (internally) fetches PDFs to memory and extracts text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keywords."
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 3
                    },
                },
                "required": ["query"],
            },
        },
    },
    
    # Wikipedia 搜索
    {
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
    },
]


# ============================================================
# 测试运行
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("工具调用实现对比")
    print("=" * 60)
    
    # 1. 分析参数结构
    analyze_tool_parameters()
    
    # 2. OpenAI 手动实现
    # openai_manual_tool_calling()
    
    # 3. Anthropic 手动实现
    # anthropic_manual_tool_calling()
    
    # 4. aisuite 统一实现（推荐）
    # aisuite_unified_tool_calling("openai:gpt-4o-mini")
    # aisuite_unified_tool_calling("anthropic:claude-3-5-sonnet-20241022")
