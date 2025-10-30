"""
规划代理模块 - 负责组织和执行多代理研究工作流
本模块包含：
1. planner_agent: 生成研究计划步骤
2. executor_agent_step: 执行单个计划步骤
3. clean_json_block: 清理 JSON 代码块
"""

import json
import re
from typing import List
from datetime import datetime
from aisuite import Client
from src.agents import (
    research_agent,
    writer_agent,
    editor_agent,
)
from src.config import ModelConfig
from src.cost_tracker import tracker
from src.fallback import with_fallback
from src.model_adapter import ModelAdapter

# 初始化 AI 客户端
client = Client()


def clean_json_block(raw: str) -> str:
    """
    清理 JSON 代码块，移除 markdown 代码围栏标记
    
    参数:
        raw: 原始字符串，可能包含 ```json 等标记
    
    返回:
        清理后的字符串
    """
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
    return raw.strip("` \n")


from typing import List
import json, ast


@with_fallback
def planner_agent(topic: str, model: str = None) -> List[str]:
    """
    规划代理 - 为研究主题生成结构化的执行步骤

    参数:
        topic: 研究主题
        model: 使用的 AI 模型（默认: None, 使用 ModelConfig.PLANNER_MODEL）

    返回:
        List[str]: 研究步骤列表（最多7步）
    """
    # 如果未指定模型，使用配置的默认模型
    if model is None:
        model = ModelConfig.PLANNER_MODEL

    print("==================================")
    print(f"🧠 规划代理 (使用 {model})")
    print("==================================")
    # 构建规划提示词，定义可用代理和规划要求
    prompt = f"""
You are a planning agent responsible for organizing a research workflow using multiple intelligent agents.

🧠 Available agents:
- Research agent: MUST begin with a broad **web search using Tavily** to identify only **relevant** and **authoritative** items (e.g., high-impact venues, seminal works, surveys, or recent comprehensive sources). The output of this step MUST capture for each candidate: title, authors, year, venue/source, URL, and (if available) DOI.
- Research agent: AFTER the Tavily step, perform a **targeted arXiv search** ONLY for the candidates discovered in the web step (match by title/author/DOI). If an arXiv preprint/version exists, record its arXiv URL and version info. Do NOT run a generic arXiv search detached from the Tavily results.
- Writer agent: drafts based on research findings.
- Editor agent: reviews, reflects on, and improves drafts.

🎯 Produce a clear step-by-step research plan **as a valid Python list of strings** (no markdown, no explanations). 
Each step must be atomic, actionable, and assigned to one of the agents.
Maximum of 7 steps.

🚫 DO NOT include steps like “create CSV”, “set up repo”, “install packages”.
✅ Focus on meaningful research tasks (search, extract, rank, draft, revise).
✅ The FIRST step MUST be exactly: 
"Research agent: Use Tavily to perform a broad web search and collect top relevant items (title, authors, year, venue/source, URL, DOI if available)."
✅ The SECOND step MUST be exactly:
"Research agent: For each collected item, search on arXiv to find matching preprints/versions and record arXiv URLs (if they exist)."

🔚 The FINAL step MUST instruct the writer agent to generate a comprehensive Markdown report that:
- Uses all findings and outputs from previous steps
- Includes inline citations (e.g., [1], (Wikipedia/arXiv))
- Includes a References section with clickable links for all citations
- Preserves earlier sources
- Is detailed and self-contained

Topic: "{topic}"
"""

    # 调用 AI 模型生成研究计划（使用 ModelAdapter 确保参数安全）
    response = ModelAdapter.safe_api_call(
        client=client,
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1,  # 允许一定的创造性
    )

    # 追踪成本
    if hasattr(response, 'usage') and response.usage:
        tracker.track(
            model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
            metadata={"agent": "planner_agent"}
        )

    raw = response.choices[0].message.content.strip()

    # --- 鲁棒的解析：尝试 JSON -> Python 字面量 -> 回退 ---
    def _coerce_to_list(s: str) -> List[str]:
        """尝试将字符串转换为字符串列表"""
        # 尝试严格的 JSON 解析
        try:
            obj = json.loads(s)
            if isinstance(obj, list) and all(isinstance(x, str) for x in obj):
                return obj[:7]
        except json.JSONDecodeError:
            pass
        # 尝试 Python 字面量列表
        try:
            obj = ast.literal_eval(s)
            if isinstance(obj, list) and all(isinstance(x, str) for x in obj):
                return obj[:7]
        except Exception:
            pass
        # 尝试提取代码围栏中的内容
        if s.startswith("```") and s.endswith("```"):
            inner = s.strip("`")
            try:
                obj = ast.literal_eval(inner)
                if isinstance(obj, list) and all(isinstance(x, str) for x in obj):
                    return obj[:7]
            except Exception:
                pass
        return []

    steps = _coerce_to_list(raw)

    # 强制执行步骤顺序和最小契约
    required_first = "Research agent: Use Tavily to perform a broad web search and collect top relevant items (title, authors, year, venue/source, URL, DOI if available)."
    required_second = "Research agent: For each collected item, search on arXiv to find matching preprints/versions and record arXiv URLs (if they exist)."
    final_required = "Writer agent: Generate the final comprehensive Markdown report with inline citations and a complete References section with clickable links."

    def _ensure_contract(steps_list: List[str]) -> List[str]:
        """确保步骤列表符合最小契约要求"""
        if not steps_list:
            # 如果没有步骤，返回默认步骤列表
            return [
                required_first,
                required_second,
                "Research agent: Synthesize and rank findings by relevance, recency, and authority; deduplicate by title/DOI.",
                "Writer agent: Draft a structured outline based on the ranked evidence.",
                "Editor agent: Review for coherence, coverage, and citation completeness; request fixes.",
                final_required,
            ]
        # 注入/替换前两个步骤（如果缺失或顺序错误）
        steps_list = [s for s in steps_list if isinstance(s, str)]
        if not steps_list or steps_list[0] != required_first:
            steps_list = [required_first] + steps_list
        if len(steps_list) < 2 or steps_list[1] != required_second:
            # 移除任何未与 Tavily 结果关联的通用 arXiv 步骤
            steps_list = (
                [steps_list[0]]
                + [required_second]
                + [
                    s
                    for s in steps_list[1:]
                    if "arXiv" not in s or "For each collected item" in s
                ]
            )
        # 确保最终步骤存在
        if final_required not in steps_list:
            steps_list.append(final_required)
        # 限制为最多7步
        return steps_list[:7]

    steps = _ensure_contract(steps)

    return steps


def executor_agent_step(step_title: str, history: list, prompt: str):
    """
    执行单个代理步骤
    
    参数:
        step_title: 步骤描述
        history: 历史执行记录列表 [(描述, 代理名, 输出), ...]
        prompt: 用户原始提示
    
    返回:
        tuple: (步骤标题, 代理名称, 输出内容)
    """
    """
    Executes a step of the executor agent.
    Returns:
        - step_title (str)
        - agent_name (str)
        - output (str)
    """

    # 构建结构化的丰富上下文
    context = f"📘 用户提示:\n{prompt}\n\n📜 历史记录:\n"
    for i, (desc, agent, output) in enumerate(history):
        if "draft" in desc.lower() or agent == "writer_agent":
            context += f"\n✍️ 草稿 (步骤 {i + 1}):\n{output.strip()}\n"
        elif "feedback" in desc.lower() or agent == "editor_agent":
            context += f"\n🧠 反馈 (步骤 {i + 1}):\n{output.strip()}\n"
        elif "research" in desc.lower() or agent == "research_agent":
            context += f"\n🔍 研究 (步骤 {i + 1}):\n{output.strip()}\n"
        else:
            context += f"\n🧩 其他 (步骤 {i + 1}) 由 {agent} 执行:\n{output.strip()}\n"

    enriched_task = f"""{context}

🧩 下一个任务:
{step_title}
"""

    # 根据步骤描述选择相应的代理
    step_lower = step_title.lower()
    if "research" in step_lower:
        # 调用研究代理
        content, _ = research_agent(prompt=enriched_task)
        print("🔍 研究代理输出:", content)
        return step_title, "research_agent", content
    elif "draft" in step_lower or "write" in step_lower:
        # 调用写作代理
        content, _ = writer_agent(prompt=enriched_task)
        return step_title, "writer_agent", content
    elif "revise" in step_lower or "edit" in step_lower or "feedback" in step_lower:
        # 调用编辑代理
        content, _ = editor_agent(prompt=enriched_task)
        return step_title, "editor_agent", content
    else:
        raise ValueError(f"未知的步骤类型: {step_title}")
