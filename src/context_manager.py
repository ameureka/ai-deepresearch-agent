"""
上下文管理器 - 智能决策文本处理策略

功能:
1. 监控上下文长度
2. 决定处理策略（直接/分块）
3. 管理文本处理流程
4. 支持配置化的阈值
"""

import logging
import os
from typing import Callable, Optional
from src.model_adapter import ModelAdapter
from src.chunking import ChunkingProcessor

logger = logging.getLogger(__name__)


class ContextManager:
    """上下文管理器 - 智能选择文本处理策略"""

    def __init__(
        self,
        model: str,
        enable_chunking: bool = None,
        chunking_threshold: float = None,
        max_chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        初始化上下文管理器

        Args:
            model: 模型名称
            enable_chunking: 是否启用分块（None 表示从环境变量读取）
            chunking_threshold: 分块阈值（上下文窗口的百分比，None 表示从环境变量读取）
            max_chunk_size: 最大块大小（None 表示从环境变量读取）
            chunk_overlap: 块重叠大小（None 表示从环境变量读取）
        """
        self.model = model
        self.limits = ModelAdapter.get_model_limits(model)

        # 从环境变量或参数获取配置
        self.enable_chunking = (
            enable_chunking
            if enable_chunking is not None
            else os.getenv('ENABLE_CHUNKING', 'true').lower() == 'true'
        )

        self.chunking_threshold = (
            chunking_threshold
            if chunking_threshold is not None
            else float(os.getenv('CHUNKING_THRESHOLD', '0.8'))
        )

        max_chunk_size = (
            max_chunk_size
            if max_chunk_size is not None
            else int(os.getenv('MAX_CHUNK_SIZE', '6000'))
        )

        chunk_overlap = (
            chunk_overlap
            if chunk_overlap is not None
            else int(os.getenv('CHUNK_OVERLAP', '200'))
        )

        # 创建分块处理器
        self.chunking_processor = ChunkingProcessor(
            max_chunk_size=max_chunk_size,
            overlap_size=chunk_overlap
        )

        logger.info(
            f"📊 上下文管理器初始化: 模型={model}, "
            f"启用分块={self.enable_chunking}, "
            f"阈值={self.chunking_threshold:.0%}"
        )

    def should_chunk(self, text: str) -> bool:
        """
        判断是否需要分块处理

        Args:
            text: 输入文本

        Returns:
            True 表示需要分块，False 表示可以直接处理
        """
        if not self.enable_chunking:
            return False

        estimated_tokens = ModelAdapter.estimate_tokens(text)
        threshold_tokens = int(self.limits['context_window'] * self.chunking_threshold)

        needs_chunking = estimated_tokens > threshold_tokens

        if needs_chunking:
            logger.info(
                f"⚠️ 文本超过阈值: {estimated_tokens} tokens > "
                f"{threshold_tokens} tokens ({self.chunking_threshold:.0%} of {self.limits['context_window']}), "
                f"将启用分块处理"
            )
        else:
            logger.debug(
                f"✅ 文本在阈值内: {estimated_tokens} tokens <= "
                f"{threshold_tokens} tokens, 直接处理"
            )

        return needs_chunking

    def get_context_usage(self, text: str) -> float:
        """
        计算上下文使用率

        Args:
            text: 输入文本

        Returns:
            使用率 (0.0 到 1.0+)
        """
        return ModelAdapter.get_context_usage(self.model, text)

    def process_text(
        self,
        text: str,
        processor_func: Callable[[str], str],
        force_chunking: bool = False,
        show_progress: bool = True
    ) -> str:
        """
        智能处理文本（自动选择策略）

        Args:
            text: 需要处理的文本
            processor_func: 处理函数，接收文本返回处理结果
            force_chunking: 强制使用分块（默认: False）
            show_progress: 是否显示进度（默认: True）

        Returns:
            处理后的文本
        """
        # 1. 评估是否需要分块
        needs_chunking = force_chunking or self.should_chunk(text)

        # 2. 根据策略处理
        if not needs_chunking:
            # 直接处理
            logger.info("📝 直接处理模式")
            return processor_func(text)
        else:
            # 分块处理
            logger.info("📦 分块处理模式")
            return self.chunking_processor.chunk_and_process(
                text=text,
                processor_func=processor_func,
                show_progress=show_progress
            )

    def estimate_cost(self, text: str, cost_per_1k_tokens: float = 0.14) -> dict:
        """
        估算处理成本

        Args:
            text: 输入文本
            cost_per_1k_tokens: 每 1K tokens 的成本（默认: DeepSeek chat 输入价格）

        Returns:
            包含估算信息的字典
        """
        estimated_tokens = ModelAdapter.estimate_tokens(text)
        needs_chunking = self.should_chunk(text)

        if not needs_chunking:
            # 直接处理：1 次调用
            calls = 1
            total_tokens = estimated_tokens
        else:
            # 分块处理：需要多次调用
            num_chunks = (estimated_tokens // self.chunking_processor.max_chunk_size) + 1
            calls = num_chunks
            # 考虑重叠区域会增加总 token 数
            overlap_overhead = (num_chunks - 1) * self.chunking_processor.overlap_size
            total_tokens = estimated_tokens + overlap_overhead

        estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens

        return {
            'input_tokens': estimated_tokens,
            'total_tokens_with_overhead': total_tokens,
            'needs_chunking': needs_chunking,
            'num_chunks': calls if needs_chunking else 1,
            'api_calls': calls,
            'estimated_cost_usd': estimated_cost,
            'context_usage': self.get_context_usage(text)
        }


# 便捷函数：创建适用于特定 Agent 的上下文管理器
def create_manager_for_agent(agent_name: str, model: str) -> ContextManager:
    """
    为特定 Agent 创建上下文管理器

    Args:
        agent_name: Agent 名称（用于日志）
        model: 模型名称

    Returns:
        配置好的 ContextManager 实例
    """
    logger.info(f"🔧 为 {agent_name} 创建上下文管理器")
    return ContextManager(model=model)
