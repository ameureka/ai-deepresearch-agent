"""
配置管理模块 - 统一管理所有 Agent 的模型配置

本模块提供：
1. ModelConfig: 统一的模型配置类
2. 环境变量读取和验证
3. 默认值管理
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ModelConfig:
    """
    统一的模型配置管理类

    从环境变量读取配置，提供默认值。
    支持运行时验证和模型查询。
    """

    # 模型配置 - 从环境变量读取，提供默认值
    PLANNER_MODEL = os.getenv("PLANNER_MODEL", "deepseek:deepseek-reasoner")
    RESEARCHER_MODEL = os.getenv("RESEARCHER_MODEL", "deepseek:deepseek-chat")
    WRITER_MODEL = os.getenv("WRITER_MODEL", "deepseek:deepseek-chat")
    EDITOR_MODEL = os.getenv("EDITOR_MODEL", "deepseek:deepseek-chat")

    # 降级配置
    FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "openai:gpt-4o-mini")

    # 请求超时（秒）
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "90"))

    @classmethod
    def get_model(cls, agent_type: str) -> Optional[str]:
        """
        获取指定代理的模型配置

        参数:
            agent_type: 代理类型 ("planner", "researcher", "writer", "editor")

        返回:
            str: 模型名称，如果代理类型未知则返回 None

        示例:
            >>> ModelConfig.get_model("planner")
            'deepseek:deepseek-reasoner'
            >>> ModelConfig.get_model("researcher")
            'deepseek:deepseek-chat'
        """
        mapping = {
            "planner": cls.PLANNER_MODEL,
            "researcher": cls.RESEARCHER_MODEL,
            "writer": cls.WRITER_MODEL,
            "editor": cls.EDITOR_MODEL,
        }
        model = mapping.get(agent_type.lower())
        if model is None:
            logger.warning(f"未知的代理类型: {agent_type}")
        return model

    @classmethod
    def validate(cls) -> bool:
        """
        验证配置的有效性

        检查：
        1. DEEPSEEK_API_KEY 存在且格式正确
        2. OPENAI_API_KEY 存在且格式正确（降级需要）
        3. 所有模型配置非空

        返回:
            bool: 配置有效返回 True

        抛出:
            ValueError: 配置无效时抛出，包含详细错误信息
        """
        # 检查 DeepSeek API Key
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if not deepseek_key:
            raise ValueError(
                "DEEPSEEK_API_KEY 未设置。请在 .env 文件中添加：\n"
                "DEEPSEEK_API_KEY=sk-your-deepseek-key"
            )
        if not deepseek_key.startswith("sk-"):
            raise ValueError(
                f"DEEPSEEK_API_KEY 格式无效：{deepseek_key[:10]}...\n"
                "API Key 应以 'sk-' 开头"
            )

        # 检查 OpenAI API Key（降级需要）
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY 未设置（降级机制需要）。请在 .env 文件中添加：\n"
                "OPENAI_API_KEY=sk-your-openai-key"
            )
        if not openai_key.startswith("sk-"):
            raise ValueError(
                f"OPENAI_API_KEY 格式无效：{openai_key[:10]}...\n"
                "API Key 应以 'sk-' 开头"
            )

        # 检查模型配置
        required_models = {
            "PLANNER_MODEL": cls.PLANNER_MODEL,
            "RESEARCHER_MODEL": cls.RESEARCHER_MODEL,
            "WRITER_MODEL": cls.WRITER_MODEL,
            "EDITOR_MODEL": cls.EDITOR_MODEL,
            "FALLBACK_MODEL": cls.FALLBACK_MODEL,
        }

        for name, value in required_models.items():
            if not value:
                raise ValueError(f"{name} 未设置或为空")

        # 验证通过，记录配置信息
        logger.info("✅ 配置验证通过")
        logger.info(f"📦 Planner Model: {cls.PLANNER_MODEL}")
        logger.info(f"📦 Researcher Model: {cls.RESEARCHER_MODEL}")
        logger.info(f"📦 Writer Model: {cls.WRITER_MODEL}")
        logger.info(f"📦 Editor Model: {cls.EDITOR_MODEL}")
        logger.info(f"🔄 Fallback Model: {cls.FALLBACK_MODEL}")
        logger.info(f"⏱️  Request Timeout: {cls.REQUEST_TIMEOUT}s")

        return True

    @classmethod
    def summary(cls) -> dict:
        """
        生成配置摘要字典

        返回:
            dict: 包含所有配置信息的字典
        """
        return {
            "models": {
                "planner": cls.PLANNER_MODEL,
                "researcher": cls.RESEARCHER_MODEL,
                "writer": cls.WRITER_MODEL,
                "editor": cls.EDITOR_MODEL,
                "fallback": cls.FALLBACK_MODEL,
            },
            "timeout": cls.REQUEST_TIMEOUT,
            "api_keys_configured": {
                "deepseek": bool(os.getenv("DEEPSEEK_API_KEY")),
                "openai": bool(os.getenv("OPENAI_API_KEY")),
            }
        }
