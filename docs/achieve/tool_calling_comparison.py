"""
工具调用实现对比：OpenAI vs Anthropic vs aisuite
实际可运行的代码示例
"""

import json
import os
from typing import List, Dict

# ============================================================
# 实际工具函数（所有实现共用）
# ============================================================

def mock_search_tool(query: str, max_results: int = 5) -> List[Dict]:
    """模拟搜索工具"""
    return [
        {"title": f"Result {i+1} for '{query}'", "url": f"https://example.com/{i}"}
        for i in range(max_results)
    ]


# ============================================================
# 方案 1: OpenAI 原生实现（手动多轮）
# ============================================================

def openai_native_implementation():
    """
    OpenAI 原生 SDK 实现
    需要手动处理多轮工具调用
    """
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 工具定义（OpenAI 格式）
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_tool",
                "description": "搜索网络信息",
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
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    messages = [
        {"role": "user", "content": "搜索 GPT-4 的信息"}
    ]
    
    print("=" * 80)
    print("OpenAI 原生实现")
    print("=" * 80)
    
    # 手动实现多轮循环
    max_iterations = 5
    
    for iteration in range(max_iterations):
        print(f"\n--- 第 {iteration + 1} 轮 ---")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # 检查是否有工具调用
        if response_message.tool_calls:
            print(f"✅ 检测到 {len(response_message.tool_calls)} 个工具调用")
            
            # 添加 assistant 消息
            messages.append(response_message)
            
            # 执行每个工具
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"  📞 {function_name}({json.dumps(function_args, ensure_ascii=False)})")
                
                # 执行实际函数
                if function_name == "search_tool":
                    result = mock_search_tool(**function_args)
                else:
                    result = {"error": "Unknown function"}
                
                print(f"  ✅ 返回 {len(result)} 条结果")
                
                # 添加工具结果
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
        
        else:
            # 没有工具调用，获取最终回复
            print(f"✅ 生成最终回复")
            final_answer = response_message.content
            print(f"\n最终回复:\n{final_answer}")
            return final_answer
    
    print("⚠️ 达到最大迭代次数")
    return None


# ============================================================
# 方案 2: Anthropic 原生实现（手动多轮）
# ============================================================

def anthropic_native_implementation():
    """
    Anthropic Claude 原生 SDK 实现
    格式与 OpenAI 不同，也需要手动处理多轮
    """
    from anthropic import Anthropic
    
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # 工具定义（Anthropic 格式 - 注意差异）
    tools = [
        {
            "name": "search_tool",  # 没有 type 字段
            "description": "搜索网络信息",
            "input_schema": {  # 不是 parameters，是 input_schema
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大结果数",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    ]
    
    messages = [
        {"role": "user", "content": "搜索 GPT-4 的信息"}
    ]
    
    print("=" * 80)
    print("Anthropic 原生实现")
    print("=" * 80)
    
    # 手动实现多轮循环
    max_iterations = 5
    
    for iteration in range(max_iterations):
        print(f"\n--- 第 {iteration + 1} 轮 ---")
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        print(f"Stop reason: {response.stop_reason}")
        
        # 检查停止原因
        if response.stop_reason == "tool_use":
            print(f"✅ 检测到工具调用")
            
            # 添加 assistant 消息
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # 处理工具调用
            tool_results = []
            
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    
                    print(f"  📞 {tool_name}({json.dumps(tool_input, ensure_ascii=False)})")
                    
                    # 执行实际函数
                    if tool_name == "search_tool":
                        result = mock_search_tool(**tool_input)
                    else:
                        result = {"error": "Unknown function"}
                    
                    print(f"  ✅ 返回 {len(result)} 条结果")
                    
                    # 构造工具结果（注意格式）
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
            
            # 添加工具结果
            messages.append({
                "role": "user",
                "content": tool_results
            })
        
        elif response.stop_reason == "end_turn":
            # 获取最终文本
            print(f"✅ 生成最终回复")
            final_text = ""
            for content_block in response.content:
                if hasattr(content_block, "text"):
                    final_text += content_block.text
            
            print(f"\n最终回复:\n{final_text}")
            return final_text
        
        else:
            print(f"⚠️ 未预期的停止原因: {response.stop_reason}")
            break
    
    print("⚠️ 达到最大迭代次数")
    return None


# ============================================================
# 方案 3: aisuite 统一实现（自动多轮）
# ============================================================

def aisuite_unified_implementation(model="openai:gpt-4o-mini"):
    """
    aisuite 统一接口
    自动处理多轮工具调用，支持多个模型
    """
    from aisuite import Client
    
    client = Client()
    
    # 工具定义（使用 OpenAI 格式，aisuite 会自动转换）
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_tool",
                "description": "搜索网络信息",
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
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    print("=" * 80)
    print(f"aisuite 统一实现 (模型: {model})")
    print("=" * 80)
    
    # 🔥 一次调用，自动处理多轮
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "搜索 GPT-4 的信息"}
        ],
        tools=tools,
        tool_choice="auto",
        max_turns=5,  # 自动处理最多 5 轮
        temperature=0
    )
    
    # 直接获取最终结果
    final_answer = response.choices[0].message.content
    
    print(f"✅ 完成（自动处理了多轮工具调用）")
    print(f"\n最终回复:\n{final_answer}")
    
    # 查看工具调用历史
    if hasattr(response.choices[0].message, 'intermediate_messages'):
        print("\n" + "=" * 80)
        print("工具调用历史:")
        print("=" * 80)
        
        for i, msg in enumerate(response.choices[0].message.intermediate_messages, 1):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"  {i}. {tc.function.name}({tc.function.arguments})")
    
    return final_answer


# ============================================================
# 对比总结
# ============================================================

def print_comparison_summary():
    """
    打印三种实现方式的对比
    """
    print("\n" + "=" * 80)
    print("三种实现方式对比")
    print("=" * 80)
    
    comparison = """
┌─────────────────┬──────────────────┬──────────────────┬──────────────────┐
│     特性        │   OpenAI 原生    │  Anthropic 原生  │     aisuite      │
├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 多轮处理        │ ❌ 手动循环      │ ❌ 手动循环      │ ✅ 自动处理      │
│ 代码复杂度      │ 高（50+ 行）     │ 高（60+ 行）     │ 低（10 行）      │
│ 工具定义格式    │ parameters       │ input_schema     │ parameters       │
│ 模型切换        │ ❌ 需要重写      │ ❌ 需要重写      │ ✅ 改一个参数    │
│ 错误处理        │ 需要自己实现     │ 需要自己实现     │ 内置处理         │
│ 调试信息        │ 需要自己记录     │ 需要自己记录     │ 提供历史记录     │
│ 学习曲线        │ 中等             │ 中等             │ 低               │
│ 灵活性          │ 高               │ 高               │ 中               │
└─────────────────┴──────────────────┴──────────────────┴──────────────────┘

代码行数对比（实现相同功能）:
  - OpenAI 原生:    ~50 行
  - Anthropic 原生: ~60 行
  - aisuite:        ~10 行

推荐使用场景:
  - OpenAI 原生:    需要精细控制每一步，或使用 OpenAI 独有特性
  - Anthropic 原生: 需要 Claude 的特定功能，或精细控制
  - aisuite:        快速开发，需要多模型支持，推荐用于生产环境 ✅
"""
    
    print(comparison)


# ============================================================
# 工具定义格式对比
# ============================================================

def print_format_comparison():
    """
    打印工具定义格式的详细对比
    """
    print("\n" + "=" * 80)
    print("工具定义格式对比")
    print("=" * 80)
    
    print("\n【OpenAI 格式】")
    print("-" * 80)
    openai_format = {
        "type": "function",  # ← 需要这个字段
        "function": {
            "name": "search_tool",
            "description": "搜索工具",
            "parameters": {  # ← 关键字: parameters
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    }
    print(json.dumps(openai_format, indent=2, ensure_ascii=False))
    
    print("\n【Anthropic 格式】")
    print("-" * 80)
    anthropic_format = {
        # 没有 type 字段
        "name": "search_tool",
        "description": "搜索工具",
        "input_schema": {  # ← 关键字: input_schema（不是 parameters）
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
    print(json.dumps(anthropic_format, indent=2, ensure_ascii=False))
    
    print("\n【aisuite 格式】")
    print("-" * 80)
    print("使用 OpenAI 格式，会自动转换为目标模型的格式")
    print(json.dumps(openai_format, indent=2, ensure_ascii=False))


# ============================================================
# 主函数
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("工具调用实现对比演示")
    print("=" * 80)
    
    # 1. 格式对比
    print_format_comparison()
    
    # 2. 实现对比总结
    print_comparison_summary()
    
    # 3. 实际运行示例（取消注释以运行）
    # print("\n\n" + "=" * 80)
    # print("实际运行示例")
    # print("=" * 80)
    
    # # OpenAI 原生
    # openai_native_implementation()
    
    # # Anthropic 原生
    # anthropic_native_implementation()
    
    # # aisuite 统一（OpenAI）
    # aisuite_unified_implementation("openai:gpt-4o-mini")
    
    # # aisuite 统一（Claude）
    # aisuite_unified_implementation("anthropic:claude-3-5-sonnet-20241022")
