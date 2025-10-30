"""
智能代理模块 - 包含研究、写作和编辑代理
本模块定义了三个核心代理：
1. research_agent: 负责信息检索和学术研究
2. writer_agent: 负责根据研究结果撰写学术报告
3. editor_agent: 负责审阅和改进文稿
"""

from datetime import datetime
from urllib import response
from aisuite import Client
from src.research_tools import (
    arxiv_search_tool,
    tavily_search_tool,
    wikipedia_search_tool,
)
from src.config import ModelConfig
from src.cost_tracker import tracker
from src.fallback import with_fallback
from src.model_adapter import ModelAdapter

# 初始化 AI 客户端
client = Client()


# === 研究代理 ===
@with_fallback
def research_agent(
    prompt: str, model: str = None, return_messages: bool = False
):
    """
    研究代理 - 执行信息检索和学术研究任务

    参数:
        prompt: 用户的研究请求
        model: 使用的 AI 模型（默认: None, 使用 ModelConfig.RESEARCHER_MODEL）
        return_messages: 是否返回消息历史（默认: False）

    返回:
        tuple: (研究结果内容, 消息历史)
    """
    # 如果未指定模型，使用配置的默认模型
    if model is None:
        model = ModelConfig.RESEARCHER_MODEL

    print("==================================")
    print(f"🔍 研究代理 (使用 {model})")
    print("==================================")

    # 构建完整的提示词，包含研究方法论和工具使用指南
    full_prompt = f"""
You are an advanced research assistant with expertise in information retrieval and academic research methodology. Your mission is to gather comprehensive, accurate, and relevant information on any topic requested by the user.

## AVAILABLE RESEARCH TOOLS:

1. **`tavily_search_tool`**: General web search engine
   - USE FOR: Recent news, current events, blogs, websites, industry reports, and non-academic sources
   - BEST FOR: Up-to-date information, diverse perspectives, practical applications, and general knowledge

2. **`arxiv_search_tool`**: Academic publication database
   - USE FOR: Peer-reviewed research papers, technical reports, and scholarly articles
   - LIMITED TO THESE DOMAINS ONLY:
     * Computer Science
     * Mathematics
     * Physics
     * Statistics
     * Quantitative Biology
     * Quantitative Finance
     * Electrical Engineering and Systems Science
     * Economics
   - BEST FOR: Scientific evidence, theoretical frameworks, and technical details in supported fields

3. **`wikipedia_search_tool`**: Encyclopedia resource
   - USE FOR: Background information, definitions, overviews, historical context
   - BEST FOR: Establishing foundational knowledge and understanding basic concepts

## RESEARCH METHODOLOGY:

1. **Analyze Request**: Identify the core research questions and knowledge domains
2. **Plan Search Strategy**: Determine which tools are most appropriate for the topic
3. **Execute Searches**: Use the selected tools with effective keywords and queries
4. **Evaluate Sources**: Prioritize credibility, relevance, recency, and diversity
5. **Synthesize Findings**: Organize information logically with clear source attribution
6. **Document Search Process**: Note which tools were used and why

## TOOL SELECTION GUIDELINES:

- For scientific/academic questions in supported domains → Use `arxiv_search_tool`
- For recent developments, news, or practical information → Use `tavily_search_tool`
- For fundamental concepts or historical context → Use `wikipedia_search_tool`
- For comprehensive research → Use multiple tools strategically
- NEVER use `arxiv_search_tool` for domains outside its supported list
- ALWAYS verify information across multiple sources when possible

## OUTPUT FORMAT:

Present your research findings in a structured format that includes:
1. **Summary of Research Approach**: Tools used and search strategy
2. **Key Findings**: Organized by subtopic or source
3. **Source Details**: Include URLs, titles, authors, and publication dates
4. **Limitations**: Note any gaps in available information

Today is {datetime.now().strftime("%Y-%m-%d")}.

USER RESEARCH REQUEST:
{prompt}
""".strip()

    # 准备消息和可用工具
    messages = [{"role": "user", "content": full_prompt}]
    tools = [arxiv_search_tool, tavily_search_tool, wikipedia_search_tool]

    try:
        # 调用 AI 模型进行研究（使用 ModelAdapter 确保参数安全）
        resp = ModelAdapter.safe_api_call(
            client=client,
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",  # 自动选择工具
            max_turns=5,  # 最多5轮对话
            temperature=0.0,  # 使用确定性输出
        )

        # 追踪成本
        if hasattr(resp, 'usage') and resp.usage:
            tracker.track(
                model,
                resp.usage.prompt_tokens,
                resp.usage.completion_tokens,
                metadata={"agent": "research_agent"}
            )

        content = resp.choices[0].message.content or ""

        # ---- 从中间响应和消息中收集工具调用记录 ----
        calls = []

        # A) 从 intermediate_responses 中提取
        for ir in getattr(resp, "intermediate_responses", []) or []:
            try:
                tcs = ir.choices[0].message.tool_calls or []
                for tc in tcs:
                    calls.append((tc.function.name, tc.function.arguments))
            except Exception:
                pass

        # B) 从最终消息的 intermediate_messages 中提取
        for msg in getattr(resp.choices[0].message, "intermediate_messages", []) or []:
            # 带有 tool_calls 的助手消息
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    calls.append((tc.function.name, tc.function.arguments))

        # 去重同时保持顺序
        seen = set()
        dedup_calls = []
        for name, args in calls:
            key = (name, args)
            if key not in seen:
                seen.add(key)
                dedup_calls.append((name, args))

        # 格式化工具调用参数：尝试将 JSON 转换为字典格式
        tool_lines = []
        for name, args in dedup_calls:
            arg_text = str(args)
            try:
                import json as _json

                parsed = _json.loads(args) if isinstance(args, str) else args
                if isinstance(parsed, dict):
                    kv = ", ".join(f"{k}={repr(v)}" for k, v in parsed.items())
                    arg_text = kv
            except Exception:
                # 如果不是 JSON 格式，保持原始字符串
                pass
            tool_lines.append(f"- {name}({arg_text})")

        # 如果有工具调用，添加到输出内容中
        if tool_lines:
            tools_html = (
                "<h2 style='font-size:1.5em; color:#2563eb;'>📎 Tools used</h2>"
            )
            tools_html += (
                "<ul>" + "".join(f"<li>{line}</li>" for line in tool_lines) + "</ul>"
            )
            content += "\n\n" + tools_html

        print("✅ Output:\n", content)
        return content, messages

    except Exception as e:
        print("❌ Error:", e)
        return f"[Model Error: {str(e)}]", messages


@with_fallback
def writer_agent(
    prompt: str,
    model: str = None,
    min_words_total: int = 2400,
    min_words_per_section: int = 400,
    max_tokens: int = None,  # 改为 None，让 ModelAdapter 自动处理
    retries: int = 1,
):
    """
    写作代理 - 根据研究材料撰写学术报告

    参数:
        prompt: 写作任务描述和研究材料
        model: 使用的 AI 模型（默认: None, 使用 ModelConfig.WRITER_MODEL）
        min_words_total: 报告最少总字数（默认: 2400）
        min_words_per_section: 每个章节最少字数（默认: 400）
        max_tokens: 最大生成令牌数（默认: 15000）
        retries: 重试次数（默认: 1）

    返回:
        tuple: (报告内容, 消息历史)
    """
    # 如果未指定模型，使用配置的默认模型
    if model is None:
        model = ModelConfig.WRITER_MODEL

    print("==================================")
    print(f"✍️ 写作代理 (使用 {model})")
    print("==================================")

    # 系统消息：定义写作代理的角色和要求
    system_message = """
You are an expert academic writer with a PhD-level understanding of scholarly communication. Your task is to synthesize research materials into a comprehensive, well-structured academic report.

## REPORT REQUIREMENTS:
- Produce a COMPLETE, POLISHED, and PUBLICATION-READY academic report in Markdown format
- Create original content that thoroughly analyzes the provided research materials
- DO NOT merely summarize the sources; develop a cohesive narrative with critical analysis
- Length should be appropriate to thoroughly cover the topic (typically 1500-3000 words)

## MANDATORY STRUCTURE:
1. **Title**: Clear, concise, and descriptive of the content
2. **Abstract**: Brief summary (100-150 words) of the report's purpose, methods, and key findings
3. **Introduction**: Present the topic, research question/problem, significance, and outline of the report
4. **Background/Literature Review**: Contextualize the topic within existing scholarship
5. **Methodology**: If applicable, describe research methods, data collection, and analytical approaches
6. **Key Findings/Results**: Present the primary outcomes and evidence
7. **Discussion**: Interpret findings, address implications, limitations, and connections to broader field
8. **Conclusion**: Synthesize main points and suggest directions for future research
9. **References**: Complete list of all cited works

## ACADEMIC WRITING GUIDELINES:
- Maintain formal, precise, and objective language throughout
- Use discipline-appropriate terminology and concepts
- Support all claims with evidence and reasoning
- Develop logical flow between ideas, paragraphs, and sections
- Include relevant examples, case studies, data, or equations to strengthen arguments
- Address potential counterarguments and limitations

## CITATION AND REFERENCE RULES:
- Use numeric inline citations [1], [2], etc. for all borrowed ideas and information
- Every claim based on external sources MUST have a citation
- Each inline citation must correspond to a complete entry in the References section
- Every reference listed must be cited at least once in the text
- Preserve ALL original URLs, DOIs, and bibliographic information from source materials
- Format references consistently according to academic standards

## FORMATTING GUIDELINES:
- Use Markdown syntax for all formatting (headings, emphasis, lists, etc.)
- Include appropriate section headings and subheadings to organize content
- Format any equations, tables, or figures according to academic conventions
- Use bullet points or numbered lists when appropriate for clarity
- Use html syntax to handle all links with target="_blank", so user can always open link in new tab on both html and markdown format

Output the complete report in Markdown format only. Do not include meta-commentary about the writing process.

INTERNAL CHECKLIST (DO NOT INCLUDE IN OUTPUT):
- [ ] Incorporated all provided research materials
- [ ] Developed original analysis beyond mere summarization
- [ ] Included all mandatory sections with appropriate content
- [ ] Used proper inline citations for all borrowed content
- [ ] Created complete References section with all cited sources
- [ ] Maintained academic tone and language throughout
- [ ] Ensured logical flow and coherent structure
- [ ] Preserved all source URLs and bibliographic information
""".strip()

    # 准备消息列表
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]

    # 内部函数：调用 AI 模型
    def _call(messages_):
        # 使用 ModelAdapter 进行安全的 API 调用
        api_params = {"temperature": 0}
        if max_tokens is not None:
            api_params["max_tokens"] = max_tokens

        resp = ModelAdapter.safe_api_call(
            client=client,
            model=model,
            messages=messages_,
            **api_params
        )
        # 追踪成本
        if hasattr(resp, 'usage') and resp.usage:
            tracker.track(
                model,
                resp.usage.prompt_tokens,
                resp.usage.completion_tokens,
                metadata={"agent": "writer_agent"}
            )
        return resp.choices[0].message.content or ""

    # 内部函数：统计字数
    def _word_count(md_text: str) -> int:
        import re

        words = re.findall(r"\b\w+\b", md_text)
        return len(words)

    # 生成报告内容
    content = _call(messages)

    print("✅ Output:\n", content)
    return content, messages


@with_fallback
def editor_agent(
    prompt: str,
    model: str = None,
    target_min_words: int = 2400,
):
    """
    编辑代理 - 审阅和改进学术文稿

    参数:
        prompt: 需要编辑的文稿内容
        model: 使用的 AI 模型（默认: None, 使用 ModelConfig.EDITOR_MODEL）
        target_min_words: 目标最少字数（默认: 2400）

    返回:
        tuple: (编辑后的内容, 消息历史)
    """
    # 如果未指定模型，使用配置的默认模型
    if model is None:
        model = ModelConfig.EDITOR_MODEL

    print("==================================")
    print(f"📝 编辑代理 (使用 {model})")
    print("==================================")

    # 系统消息：定义编辑代理的角色和编辑流程
    system_message = """
You are a professional academic editor with expertise in improving scholarly writing across disciplines. Your task is to refine and elevate the quality of the academic text provided.

## Your Editing Process:
1. Analyze the overall structure, argument flow, and coherence of the text
2. Ensure logical progression of ideas with clear topic sentences and transitions between paragraphs
3. Improve clarity, precision, and conciseness of language while maintaining academic tone
4. Verify technical accuracy (to the extent possible based on context)
5. Enhance readability through appropriate formatting and organization

## Specific Elements to Address:
- Strengthen thesis statements and main arguments
- Clarify complex concepts with additional explanations or examples where needed
- Add relevant equations, diagrams, or illustrations (described in markdown) when they would enhance understanding
- Ensure proper integration of evidence and maintain academic rigor
- Standardize terminology and eliminate redundancies
- Improve sentence variety and paragraph structure
- Preserve all citations [1], [2], etc., and maintain the integrity of the References section

## Formatting Guidelines:
- Use markdown formatting consistently for headings, emphasis, lists, etc.
- Structure content with appropriate section headings and subheadings
- Format equations, tables, and figures according to academic standards

Return only the revised, polished text in Markdown format without explanatory comments about your edits.
""".strip()

    # 准备消息列表
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]

    # 调用 AI 模型进行编辑（使用 ModelAdapter 确保参数安全）
    response = ModelAdapter.safe_api_call(
        client=client,
        model=model,
        messages=messages,
        temperature=0  # 确定性输出
    )

    # 追踪成本
    if hasattr(response, 'usage') and response.usage:
        tracker.track(
            model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
            metadata={"agent": "editor_agent"}
        )

    content = response.choices[0].message.content
    print("✅ 输出:\n", content)
    return content, messages
