"""
测试 DeepSeek 工具调用兼容性
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 测试 1: 使用 OpenAI SDK 直接测试 DeepSeek
def test_deepseek_with_openai_sdk():
    """使用 OpenAI SDK 测试 DeepSeek 的工具调用"""
    print("\n" + "="*60)
    print("测试 1: OpenAI SDK + DeepSeek")
    print("="*60)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "获取指定城市的天气信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "城市名称，例如：北京、上海"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "北京的天气怎么样？"}
            ],
            tools=tools
        )
        
        print("✅ OpenAI SDK 测试成功")
        print(f"响应: {response.choices[0].message}")
        
        if response.choices[0].message.tool_calls:
            print(f"工具调用: {response.choices[0].message.tool_calls[0].function.name}")
            print(f"参数: {response.choices[0].message.tool_calls[0].function.arguments}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI SDK 测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        return False


# 测试 2: 使用 aisuite 测试 DeepSeek
def test_deepseek_with_aisuite():
    """使用 aisuite 测试 DeepSeek 的工具调用"""
    print("\n" + "="*60)
    print("测试 2: aisuite + DeepSeek")
    print("="*60)
    
    try:
        from aisuite import Client
        
        # 定义一个简单的 Python 函数作为工具
        def get_weather(location: str) -> str:
            """获取天气信息"""
            return f"{location}的天气是晴天，温度25°C"
        
        client = Client()
        
        response = client.chat.completions.create(
            model="deepseek:deepseek-chat",
            messages=[
                {"role": "user", "content": "上海的天气怎么样？"}
            ],
            tools=[get_weather],
            tool_choice="auto",
        )
        
        print("✅ aisuite 测试成功")
        print(f"响应: {response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ aisuite 测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


# 测试 3: 测试当前项目的工具定义格式
def test_current_project_tools():
    """测试当前项目的工具定义格式"""
    print("\n" + "="*60)
    print("测试 3: 当前项目工具格式 + DeepSeek")
    print("="*60)
    
    try:
        from aisuite import Client
        from src.research_tools import (
            tavily_search_tool,
            arxiv_search_tool,
            wikipedia_search_tool
        )
        
        client = Client()
        
        response = client.chat.completions.create(
            model="deepseek:deepseek-chat",
            messages=[
                {"role": "user", "content": "搜索 GPT-4 的相关信息"}
            ],
            tools=[tavily_search_tool],
            tool_choice="auto",
            max_turns=2,
        )
        
        print("✅ 当前项目工具格式测试成功")
        print(f"响应: {response.choices[0].message.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 当前项目工具格式测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔍 DeepSeek 工具调用兼容性测试")
    print("="*60)
    
    # 检查 API Key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  警告: 未找到 DEEPSEEK_API_KEY 环境变量")
        print("请在 .env 文件中添加: DEEPSEEK_API_KEY=your-api-key")
        exit(1)
    
    results = []
    
    # 运行测试
    results.append(("OpenAI SDK", test_deepseek_with_openai_sdk()))
    results.append(("aisuite", test_deepseek_with_aisuite()))
    results.append(("当前项目工具", test_current_project_tools()))
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:20s} {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！DeepSeek 工具调用完全兼容")
    else:
        print("\n⚠️  部分测试失败，需要进一步调查")
