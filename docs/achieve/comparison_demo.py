"""
aisuite vs 原生 SDK 对比示例
"""

# ========== 方案 1: aisuite（当前项目使用）==========
from aisuite import Client

client = Client()

# 优势1: 统一接口，轻松切换模型
def research_with_aisuite(prompt, model="openai:gpt-4.1-mini"):
    response = client.chat.completions.create(
        model=model,  # 可以是 "anthropic:claude-3-5-sonnet-20241022"
        messages=[{"role": "user", "content": prompt}],
        tools=[tavily_tool, arxiv_tool, wikipedia_tool],
        tool_choice="auto",
        max_turns=5,  # 自动处理多轮工具调用！
        temperature=0.0
    )
    return response.choices[0].message.content

# 切换到 Claude 只需改一个参数
result_gpt = research_with_aisuite("研究 LLM", model="openai:gpt-4.1-mini")
result_claude = research_with_aisuite("研究 LLM", model="anthropic:claude-3-5-sonnet-20241022")


# ========== 方案 2: 原生 Anthropic SDK ==========
from anthropic import Anthropic

anthropic_client = Anthropic()

def research_with_claude_native(prompt):
    messages = [{"role": "user", "content": prompt}]
    
    # 需要手动实现多轮工具调用循环
    for turn in range(5):
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=[
                {
                    "name": "tavily_search",
                    "description": "...",
                    "input_schema": {  # 注意：格式不同
                        "type": "object",
                        "properties": {...}
                    }
                }
            ],
            messages=messages
        )
        
        # 手动处理工具调用
        if response.stop_reason == "tool_use":
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    
                    # 执行工具
                    tool_result = execute_tool(tool_name, tool_input)
                    
                    # 构造下一轮消息
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": tool_result
                        }]
                    })
        else:
            break
    
    return response.content[0].text


# ========== 方案 3: 混合方案（推荐）==========
class MultiModelAgent:
    """使用 aisuite 但针对不同任务选择最佳模型"""
    
    def __init__(self):
        self.client = Client()
    
    def plan(self, topic):
        """规划任务 - 使用 OpenAI o1-mini（推理能力强）"""
        return self.client.chat.completions.create(
            model="openai:o1-mini",
            messages=[{"role": "user", "content": f"制定研究计划: {topic}"}],
            temperature=1
        )
    
    def research(self, task):
        """研究任务 - 使用 Claude 3.5 Sonnet（工具调用强）"""
        return self.client.chat.completions.create(
            model="anthropic:claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": task}],
            tools=[tavily_tool, arxiv_tool, wikipedia_tool],
            max_turns=5,
            temperature=0
        )
    
    def write(self, research_data):
        """写作任务 - 使用 GPT-4（写作质量高）"""
        return self.client.chat.completions.create(
            model="openai:gpt-4",
            messages=[{"role": "user", "content": f"基于以下研究撰写报告:\n{research_data}"}],
            temperature=0.7
        )
