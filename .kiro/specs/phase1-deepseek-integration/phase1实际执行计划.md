 Phase 1: DeepSeek API 全面集成 - 最终执行方案

 🎯 目标

 将所有 4 个 Agent 切换到 DeepSeek 模型，实现约 45% 的成本节省。

 📦 模型配置方案

 PLANNER_MODEL = "deepseek:deepseek-reasoner"  # 推理能力
 RESEARCHER_MODEL = "deepseek:deepseek-chat"    # 工具调用
 WRITER_MODEL = "deepseek:deepseek-chat"        # 长文本生成
 EDITOR_MODEL = "deepseek:deepseek-chat"        # 文本改进
 FALLBACK_MODEL = "openai:gpt-4o-mini"          # 降级备用

 ---
 📋 执行步骤（6.5 小时，20 个任务）

 第 1 步：环境准备（30 分钟）

 任务 1.1: 验证 DeepSeek API Key
 - 检查 .env 文件中的 DEEPSEEK_API_KEY
 - 验证格式（sk- 前缀）
 - 测试 API 连接

 任务 1.2: 验证依赖版本
 pip show aisuite  # 确保 >= 0.1.12

 任务 1.3: 修复现有 Bug
 - src/agents.py:24: gpt-4.1-mini → gpt-4o-mini
 - src/planning_agent.py:45: o4-mini → o1-mini

 ---
 第 2 步：创建配置管理（1 小时）

 任务 2.1: 创建 src/config.py
 import os

 class ModelConfig:
     """统一的模型配置管理"""

     PLANNER_MODEL = os.getenv("PLANNER_MODEL", "deepseek:deepseek-reasoner")
     RESEARCHER_MODEL = os.getenv("RESEARCHER_MODEL", "deepseek:deepseek-chat")
     WRITER_MODEL = os.getenv("WRITER_MODEL", "deepseek:deepseek-chat")
     EDITOR_MODEL = os.getenv("EDITOR_MODEL", "deepseek:deepseek-chat")
     FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "openai:gpt-4o-mini")
     REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "90"))

     @classmethod
     def get_model(cls, agent_type: str) -> str:
         """获取指定代理的模型"""
         mapping = {
             "planner": cls.PLANNER_MODEL,
             "researcher": cls.RESEARCHER_MODEL,
             "writer": cls.WRITER_MODEL,
             "editor": cls.EDITOR_MODEL,
         }
         return mapping.get(agent_type.lower())

     @classmethod
     def validate(cls) -> bool:
         """验证配置"""
         deepseek_key = os.getenv("DEEPSEEK_API_KEY")
         openai_key = os.getenv("OPENAI_API_KEY")

         if not deepseek_key or not deepseek_key.startswith("sk-"):
             raise ValueError("DEEPSEEK_API_KEY 无效或未设置")
         if not openai_key or not openai_key.startswith("sk-"):
             raise ValueError("OPENAI_API_KEY 无效或未设置（降级需要）")

         return True

 任务 2.2: 更新 .env.example
 # DeepSeek API Key
 DEEPSEEK_API_KEY=sk-your-deepseek-key

 # OpenAI API Key (用于降级)
 OPENAI_API_KEY=sk-your-openai-key

 # 模型配置（可选，已有默认值）
 PLANNER_MODEL=deepseek:deepseek-reasoner
 RESEARCHER_MODEL=deepseek:deepseek-chat
 WRITER_MODEL=deepseek:deepseek-chat
 EDITOR_MODEL=deepseek:deepseek-chat
 FALLBACK_MODEL=openai:gpt-4o-mini
 REQUEST_TIMEOUT=90

 任务 2.3: 创建配置验证脚本 scripts/check_config.py
 #!/usr/bin/env python3
 """配置验证脚本"""

 from src.config import ModelConfig

 def main():
     print("🔍 验证配置...")
     try:
         ModelConfig.validate()
         print("✅ 配置验证通过")
         print(f"📦 Planner Model: {ModelConfig.PLANNER_MODEL}")
         print(f"📦 Researcher Model: {ModelConfig.RESEARCHER_MODEL}")
         print(f"📦 Writer Model: {ModelConfig.WRITER_MODEL}")
         print(f"📦 Editor Model: {ModelConfig.EDITOR_MODEL}")
     except ValueError as e:
         print(f"❌ 配置错误: {e}")
         return 1
     return 0

 if __name__ == "__main__":
     exit(main())

 ---
 第 3 步：创建成本追踪（1 小时）

 任务 3.1: 创建 src/cost_tracker.py
 from typing import Dict
 import logging

 logger = logging.getLogger(__name__)

 class CostTracker:
     """API 调用成本追踪"""

     # 价格表（每百万 token，单位：美元）
     PRICES = {
         "deepseek:deepseek-chat": {"input": 0.14, "output": 0.28},
         "deepseek:deepseek-reasoner": {"input": 0.55, "output": 2.19},
         "openai:gpt-4o-mini": {"input": 0.15, "output": 0.60},
         "openai:o1-mini": {"input": 3.00, "output": 12.00},
     }

     def __init__(self):
         self.costs: Dict[str, float] = {}
         self.calls: Dict[str, int] = {}
         self.tokens: Dict[str, Dict[str, int]] = {}

     def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
         """记录一次 API 调用"""
         if model not in self.PRICES:
             logger.warning(f"未知模型: {model}")
             return 0.0

         prices = self.PRICES[model]
         cost = (input_tokens / 1_000_000 * prices["input"]) + \
                (output_tokens / 1_000_000 * prices["output"])

         # 累计统计
         self.costs[model] = self.costs.get(model, 0.0) + cost
         self.calls[model] = self.calls.get(model, 0) + 1
         if model not in self.tokens:
             self.tokens[model] = {"input": 0, "output": 0}
         self.tokens[model]["input"] += input_tokens
         self.tokens[model]["output"] += output_tokens

         logger.info(f"💰 {model}: ${cost:.6f} ({input_tokens} in, {output_tokens} out)")
         return cost

     def summary(self) -> Dict:
         """生成成本摘要"""
         total_cost = sum(self.costs.values())
         total_calls = sum(self.calls.values())

         return {
             "total_cost": total_cost,
             "total_calls": total_calls,
             "by_model": {
                 model: {
                     "cost": self.costs.get(model, 0.0),
                     "calls": self.calls.get(model, 0),
                     "tokens": self.tokens.get(model, {}),
                 }
                 for model in set(list(self.costs.keys()) + list(self.calls.keys()))
             }
         }

 # 全局单例
 tracker = CostTracker()

 ---
 第 4 步：更新所有 Agent（2.5 小时）

 任务 4.1: 更新 src/agents.py - Research Agent
 from src.config import ModelConfig
 from src.cost_tracker import tracker

 def research_agent(
     prompt: str, 
     model: str = None,  # 改为 None
     return_messages: bool = False
 ):
     """研究代理 - 使用 DeepSeek"""
     if model is None:
         model = ModelConfig.RESEARCHER_MODEL  # 默认使用 deepseek-chat

     print("==================================")
     print(f"🔍 研究代理 (使用 {model})")
     print("==================================")

     # ... 原有代码 ...

     try:
         resp = client.chat.completions.create(
             model=model,
             messages=messages,
             tools=tools,
             tool_choice="auto",
             max_turns=5,
             temperature=0.0,
         )

         # 追踪成本
         if hasattr(resp, 'usage'):
             tracker.track(model, resp.usage.prompt_tokens, resp.usage.completion_tokens)

         content = resp.choices[0].message.content or ""
         # ... 其余代码 ...

 任务 4.2: 更新 src/agents.py - Writer Agent
 def writer_agent(
     prompt: str,
     model: str = None,  # 改为 None
     min_words_total: int = 2400,
     min_words_per_section: int = 400,
     max_tokens: int = 15000,
     retries: int = 1,
 ):
     """写作代理 - 使用 DeepSeek"""
     if model is None:
         model = ModelConfig.WRITER_MODEL  # 默认使用 deepseek-chat

     print("==================================")
     print(f"✍️ 写作代理 (使用 {model})")
     print("==================================")

     # ... 原有代码 ...

     # 追踪成本（在 API 调用后）
     if hasattr(resp, 'usage'):
         tracker.track(model, resp.usage.prompt_tokens, resp.usage.completion_tokens)

 任务 4.3: 更新 src/agents.py - Editor Agent
 def editor_agent(
     prompt: str,
     model: str = None,  # 改为 None
     target_min_words: int = 2400,
 ):
     """编辑代理 - 使用 DeepSeek"""
     if model is None:
         model = ModelConfig.EDITOR_MODEL  # 默认使用 deepseek-chat

     print("==================================")
     print(f"📝 编辑代理 (使用 {model})")
     print("==================================")

     # ... 原有代码 ...

     # 追踪成本
     if hasattr(resp, 'usage'):
         tracker.track(model, resp.usage.prompt_tokens, resp.usage.completion_tokens)

 任务 4.4: 更新 src/planning_agent.py
 from src.config import ModelConfig
 from src.cost_tracker import tracker

 def planner_agent(
     topic: str, 
     model: str = None  # 改为 None
 ) -> List[str]:
     """规划代理 - 使用 DeepSeek Reasoner"""
     if model is None:
         model = ModelConfig.PLANNER_MODEL  # 默认使用 deepseek-reasoner

     print("==================================")
     print(f"🧠 规划代理 (使用 {model})")
     print("==================================")

     # ... 原有代码 ...

     response = client.chat.completions.create(
         model=model,
         messages=[{"role": "user", "content": prompt}],
         temperature=1,
     )

     # 追踪成本
     if hasattr(response, 'usage'):
         tracker.track(model, response.usage.prompt_tokens, response.usage.completion_tokens)

     # ... 其余代码 ...

 任务 4.5: 创建降级机制 src/fallback.py
 import logging
 from functools import wraps
 from src.config import ModelConfig

 logger = logging.getLogger(__name__)

 def with_fallback(agent_func):
     """降级装饰器"""
     @wraps(agent_func)
     def wrapper(*args, **kwargs):
         model = kwargs.get('model')
         try:
             return agent_func(*args, **kwargs)
         except Exception as e:
             if model and "deepseek" in model:
                 logger.warning(f"⚠️ {model} 失败: {e}, 降级到 {ModelConfig.FALLBACK_MODEL}")
                 kwargs['model'] = ModelConfig.FALLBACK_MODEL
                 return agent_func(*args, **kwargs)
             raise
     return wrapper

 任务 4.6: 应用降级装饰器到所有 Agent
 # 在 src/agents.py 中
 from src.fallback import with_fallback

 @with_fallback
 def research_agent(...):
     pass

 @with_fallback
 def writer_agent(...):
     pass

 @with_fallback
 def editor_agent(...):
     pass

 # 在 src/planning_agent.py 中
 from src.fallback import with_fallback

 @with_fallback
 def planner_agent(...):
     pass

 ---
 第 5 步：测试验证（1 小时）

 任务 5.1: 创建单元测试 tests/test_config.py
 import os
 import pytest
 from src.config import ModelConfig

 def test_default_models():
     """测试默认模型配置"""
     assert ModelConfig.PLANNER_MODEL == "deepseek:deepseek-reasoner"
     assert ModelConfig.RESEARCHER_MODEL == "deepseek:deepseek-chat"
     assert ModelConfig.WRITER_MODEL == "deepseek:deepseek-chat"
     assert ModelConfig.EDITOR_MODEL == "deepseek:deepseek-chat"

 def test_get_model():
     """测试 get_model 方法"""
     assert ModelConfig.get_model("planner") == "deepseek:deepseek-reasoner"
     assert ModelConfig.get_model("researcher") == "deepseek:deepseek-chat"

 任务 5.2: 创建成本追踪测试 tests/test_cost_tracker.py
 from src.cost_tracker import CostTracker

 def test_track_cost():
     """测试成本计算"""
     tracker = CostTracker()
     cost = tracker.track("deepseek:deepseek-chat", 1000, 500)
     expected = (1000/1_000_000 * 0.14) + (500/1_000_000 * 0.28)
     assert abs(cost - expected) < 0.0001

 def test_summary():
     """测试成本摘要"""
     tracker = CostTracker()
     tracker.track("deepseek:deepseek-chat", 1000, 500)
     summary = tracker.summary()
     assert summary["total_calls"] == 1
     assert "deepseek:deepseek-chat" in summary["by_model"]

 任务 5.3: 运行配置验证
 python scripts/check_config.py

 任务 5.4: 运行单元测试
 pytest tests/test_config.py tests/test_cost_tracker.py -v

 任务 5.5: 手动测试完整流程（可选）
 # 启动服务并测试一个简单的研究任务
 # 观察日志中的模型使用和成本追踪

 ---
 第 6 步：文档更新（30 分钟）

 任务 6.1: 更新 README.md
 在 README 中添加 DeepSeek 配置说明：
 ## 🆕 DeepSeek 集成

 本项目已集成 DeepSeek API，实现约 45% 的成本节省。

 ### 配置
 在 `.env` 文件中添加：
 ```bash
 DEEPSEEK_API_KEY=sk-your-deepseek-key

 模型配置

 - Planner: deepseek-reasoner（推理能力）
 - Researcher: deepseek-chat（工具调用）
 - Writer: deepseek-chat（长文本生成）
 - Editor: deepseek-chat（文本改进）

 成本追踪

 系统会自动追踪所有 API 调用成本，在日志中输出。

 降级机制

 当 DeepSeek API 失败时，系统会自动降级到 OpenAI。

 **任务 6.2**: 创建实施报告 `docs/phase1_implementation_report.md`
 ```markdown
 # Phase 1 实施报告

 ## 完成情况
 - ✅ 所有 4 个 Agent 切换到 DeepSeek
 - ✅ 成本追踪功能实现
 - ✅ 降级机制实现
 - ✅ 配置管理实现

 ## 模型配置
 - Planner: deepseek:deepseek-reasoner
 - Researcher: deepseek:deepseek-chat
 - Writer: deepseek:deepseek-chat
 - Editor: deepseek:deepseek-chat

 ## 预期成本节省
 约 45.8%

 ## 下一步
 - Phase 2: API 标准化

 ---
 ✅ 验收标准

 功能验收

 - 所有 4 个 Agent 默认使用 DeepSeek 模型
 - Planner 使用 deepseek-reasoner
 - Researcher/Writer/Editor 使用 deepseek-chat
 - 成本追踪在日志中输出
 - 配置验证脚本通过
 - 降级机制测试通过

 代码验收

 - 所有 Bug 修复（gpt-4.1-mini, o4-mini）
 - 单元测试通过
 - 代码符合 PEP 8 规范
 - 有清晰的注释和文档

 文档验收

 - README 更新完整
 - 实施报告生成
 - .env.example 更新

 ---
 📊 预期成果

 1. 成本节省: ~45% (从 $0.0238 → $0.0129 每任务)
 2. 功能完整: 所有 Agent 正常工作，工具调用兼容
 3. 可维护性: 统一配置管理，易于调整
 4. 可靠性: 降级机制保证服务可用性

 ---
 ⏱️ 总时间估算

 | 步骤       | 时间     |
 |----------|--------|
 | 环境准备     | 0.5 小时 |
 | 配置管理     | 1 小时   |
 | 成本追踪     | 1 小时   |
 | Agent 更新 | 2.5 小时 |
 | 测试验证     | 1 小时   |
 | 文档更新     | 0.5 小时 |
 | 总计       | 6.5 小时 |

 ---
 准备好开始执行了吗？

 确认后，我将按照此计划逐步实施，充分利用已安装的 MCP 插件和 skills（python-pro agent、context7、cost tracker 等）来提高执行效率。