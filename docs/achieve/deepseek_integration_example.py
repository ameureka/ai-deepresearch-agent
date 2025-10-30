"""
DeepSeek 集成示例代码
演示如何将 DeepSeek 集成到现有项目中
"""

from aisuite import Client
import os
from dotenv import load_dotenv

load_dotenv()

# 初始化客户端
client = Client()

# ============================================
# 示例 1: 基础使用
# ============================================

def example_basic():
    """基础使用示例"""
    print("=" * 50)
    print("示例 1: 基础使用")
    print("=" * 50)
    
    response = client.chat.completions.create(
        model="deepseek:deepseek-chat",
        messages=[
            {"role": "user", "content": "什么是大语言模型？"}
        ],
        temperature=0.7
    )
    
    print(response.choices[0].message.content)
    print()


# ============================================
# 示例 2: 工具调用
# ============================================

def example_function_calling():
    """工具调用示例"""
    print("=" * 50)
    print("示例 2: 工具调用")
    print("=" * 50)
    
    # 定义工具
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "搜索网络获取信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    response = client.chat.completions.create(
        model="deepseek:deepseek-chat",
        messages=[
            {"role": "user", "content": "搜索最新的 AI 新闻"}
        ],
        tools=tools,
        tool_choice="auto"
    )
    
    # 检查是否调用了工具
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            print(f"调用工具: {tool_call.function.name}")
            print(f"参数: {tool_call.function.arguments}")
    else:
        print(response.choices[0].message.content)
    print()


# ============================================
# 示例 3: 多轮对话
# ============================================

def example_multi_turn():
    """多轮对话示例"""
    print("=" * 50)
    print("示例 3: 多轮对话")
    print("=" * 50)
    
    messages = [
        {"role": "user", "content": "什么是 Transformer？"}
    ]
    
    # 第一轮
    response1 = client.chat.completions.create(
        model="deepseek:deepseek-chat",
        messages=messages,
        temperature=0.7
    )
    
    print("第一轮回答:")
    print(response1.choices[0].message.content)
    print()
    
    # 添加助手回复
    messages.append({
        "role": "assistant",
        "content": response1.choices[0].message.content
    })
    
    # 第二轮
    messages.append({
        "role": "user",
        "content": "它有什么优势？"
    })
    
    response2 = client.chat.completions.create(
        model="deepseek:deepseek-chat",
        messages=messages,
        temperature=0.7
    )
    
    print("第二轮回答:")
    print(response2.choices[0].message.content)
    print()


# ============================================
# 示例 4: 模型对比
# ============================================

def example_model_comparison():
    """模型对比示例"""
    print("=" * 50)
    print("示例 4: 模型对比")
    print("=" * 50)
    
    prompt = "解释量子计算的基本原理"
    
    models = [
        "openai:gpt-4o-mini",
        "deepseek:deepseek-chat",
        "deepseek:deepseek-reasoner"
    ]
    
    for model in models:
        print(f"\n使用模型: {model}")
        print("-" * 40)
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            print(response.choices[0].message.content[:200] + "...")
        except Exception as e:
            print(f"错误: {e}")
    print()


# ============================================
# 示例 5: 混合使用策略
# ============================================

def example_hybrid_strategy():
    """混合使用策略示例"""
    print("=" * 50)
    print("示例 5: 混合使用策略")
    print("=" * 50)
    
    def select_model(task_type: str) -> str:
        """根据任务类型选择最佳模型"""
        model_map = {
            "planning": "deepseek:deepseek-reasoner",  # 推理强
            "research": "deepseek:deepseek-chat",      # 快速便宜
            "writing": "openai:gpt-4o-mini",           # 写作好
            "editing": "deepseek:deepseek-chat"        # 编辑够用
        }
        return model_map.get(task_type, "deepseek:deepseek-chat")
    
    tasks = [
        ("planning", "制定一个研究计划"),
        ("research", "搜索相关文献"),
        ("writing", "撰写研究报告"),
        ("editing", "审阅并改进报告")
    ]
    
    for task_type, task_desc in tasks:
        model = select_model(task_type)
        print(f"\n任务: {task_desc}")
        print(f"选择模型: {model}")
        print("-" * 40)
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": task_desc}],
                temperature=0.7,
                max_tokens=100
            )
            
            print(response.choices[0].message.content[:150] + "...")
        except Exception as e:
            print(f"错误: {e}")
    print()


# ============================================
# 示例 6: 错误处理和降级
# ============================================

def example_error_handling():
    """错误处理和降级示例"""
    print("=" * 50)
    print("示例 6: 错误处理和降级")
    print("=" * 50)
    
    def call_with_fallback(primary_model: str, fallback_model: str, messages: list):
        """带降级的调用"""
        try:
            print(f"尝试使用: {primary_model}")
            response = client.chat.completions.create(
                model=primary_model,
                messages=messages,
                timeout=10
            )
            print("✅ 成功")
            return response
        except Exception as e:
            print(f"❌ 失败: {e}")
            print(f"降级到: {fallback_model}")
            
            response = client.chat.completions.create(
                model=fallback_model,
                messages=messages
            )
            print("✅ 降级成功")
            return response
    
    messages = [{"role": "user", "content": "你好"}]
    
    response = call_with_fallback(
        primary_model="deepseek:deepseek-chat",
        fallback_model="openai:gpt-4o-mini",
        messages=messages
    )
    
    print(f"\n最终回答: {response.choices[0].message.content}")
    print()


# ============================================
# 示例 7: 成本计算
# ============================================

def example_cost_calculation():
    """成本计算示例"""
    print("=" * 50)
    print("示例 7: 成本计算")
    print("=" * 50)
    
    # 价格表（每百万 tokens）
    prices = {
        "openai:gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "deepseek:deepseek-chat": {"input": 0.14, "output": 0.28},
        "deepseek:deepseek-v3": {"input": 0.27, "output": 1.10}
    }
    
    # 假设使用量
    usage = {
        "input_tokens": 50000,
        "output_tokens": 50000
    }
    
    print(f"使用量: {usage['input_tokens']:,} 输入 + {usage['output_tokens']:,} 输出\n")
    
    for model, price in prices.items():
        input_cost = (usage["input_tokens"] / 1_000_000) * price["input"]
        output_cost = (usage["output_tokens"] / 1_000_000) * price["output"]
        total_cost = input_cost + output_cost
        
        print(f"{model}:")
        print(f"  输入成本: ${input_cost:.4f}")
        print(f"  输出成本: ${output_cost:.4f}")
        print(f"  总成本: ${total_cost:.4f}")
        print()
    
    # 计算节省
    gpt_cost = (usage["input_tokens"] / 1_000_000) * prices["openai:gpt-4o-mini"]["input"] + \
               (usage["output_tokens"] / 1_000_000) * prices["openai:gpt-4o-mini"]["output"]
    
    deepseek_cost = (usage["input_tokens"] / 1_000_000) * prices["deepseek:deepseek-chat"]["input"] + \
                    (usage["output_tokens"] / 1_000_000) * prices["deepseek:deepseek-chat"]["output"]
    
    savings = gpt_cost - deepseek_cost
    savings_pct = (savings / gpt_cost) * 100
    
    print(f"使用 DeepSeek-Chat 节省: ${savings:.4f} ({savings_pct:.1f}%)")
    print()


# ============================================
# 主函数
# ============================================

def main():
    """运行所有示例"""
    print("\n" + "=" * 50)
    print("DeepSeek 集成示例")
    print("=" * 50 + "\n")
    
    # 检查 API Key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  警告: 未设置 DEEPSEEK_API_KEY")
        print("请在 .env 文件中添加: DEEPSEEK_API_KEY=your-key")
        return
    
    try:
        # 运行示例
        example_basic()
        example_function_calling()
        example_multi_turn()
        example_model_comparison()
        example_hybrid_strategy()
        example_error_handling()
        example_cost_calculation()
        
        print("=" * 50)
        print("所有示例运行完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请检查:")
        print("1. DEEPSEEK_API_KEY 是否正确")
        print("2. 网络连接是否正常")
        print("3. aisuite 是否已安装")


if __name__ == "__main__":
    main()
