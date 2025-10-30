"""
模型适配器 - 处理不同模型的参数差异

功能:
1. 管理不同模型的参数限制（max_tokens, context_window）
2. 自动验证和调整参数
3. 提供安全的 API 调用方法
4. 处理参数错误并自动重试
"""

import logging
from typing import Optional, Dict, Any
import aisuite as ai

logger = logging.getLogger(__name__)


class ModelAdapter:
    """模型适配器 - 统一管理不同模型的参数限制"""

    # 模型限制配置
    MODEL_LIMITS = {
        "deepseek:deepseek-chat": {
            "max_tokens": 8192,
            "context_window": 32768,
            "supports_streaming": True
        },
        "deepseek:deepseek-reasoner": {
            "max_tokens": 8192,
            "context_window": 65536,
            "supports_streaming": False
        },
        "openai:gpt-4o-mini": {
            "max_tokens": 16384,
            "context_window": 128000,
            "supports_streaming": True
        },
        "openai:gpt-4o": {
            "max_tokens": 16384,
            "context_window": 128000,
            "supports_streaming": True
        },
        "openai:o1-mini": {
            "max_tokens": 65536,
            "context_window": 128000,
            "supports_streaming": False
        }
    }

    @classmethod
    def get_model_limits(cls, model: str) -> Dict[str, Any]:
        """
        获取模型限制

        Args:
            model: 模型名称，如 "deepseek:deepseek-chat"

        Returns:
            包含 max_tokens 和 context_window 的字典
        """
        limits = cls.MODEL_LIMITS.get(model)
        if limits:
            return limits

        # 未知模型，返回保守默认值
        logger.warning(f"未知模型 {model}，使用保守默认限制")
        return {
            "max_tokens": 4096,
            "context_window": 8192,
            "supports_streaming": True
        }

    @classmethod
    def validate_and_adjust_params(cls, model: str, **kwargs) -> Dict[str, Any]:
        """
        验证并调整参数

        Args:
            model: 模型名称
            **kwargs: API 调用参数

        Returns:
            调整后的参数字典
        """
        limits = cls.get_model_limits(model)
        adjusted = kwargs.copy()

        # 调整 max_tokens
        if 'max_tokens' in adjusted:
            requested = adjusted['max_tokens']
            max_allowed = limits['max_tokens']

            if requested > max_allowed:
                logger.warning(
                    f"⚠️ max_tokens {requested} 超过模型 {model} 的限制 {max_allowed}，"
                    f"自动调整为 {max_allowed}"
                )
                adjusted['max_tokens'] = max_allowed
        else:
            # 如果未设置，使用模型限制的 80% 作为默认值
            default_max_tokens = int(limits['max_tokens'] * 0.8)
            adjusted['max_tokens'] = default_max_tokens
            logger.debug(f"未设置 max_tokens，使用默认值 {default_max_tokens}")

        return adjusted

    @classmethod
    def safe_api_call(cls, client: ai.Client, model: str, messages: list, **kwargs):
        """
        安全的 API 调用（带参数验证和错误重试）

        Args:
            client: aisuite 客户端实例
            model: 模型名称
            messages: 消息列表
            **kwargs: 其他 API 参数

        Returns:
            API 响应对象

        Raises:
            Exception: 所有重试失败后抛出原始异常
        """
        import time
        max_retries = 3  # 增加到 3 次重试
        base_wait_time = 2  # 基础等待时间（秒）

        for attempt in range(max_retries):
            try:
                # 1. 验证和调整参数
                adjusted_params = cls.validate_and_adjust_params(model, **kwargs)

                logger.info(
                    f"📡 调用 {model} API (尝试 {attempt + 1}/{max_retries}), "
                    f"max_tokens={adjusted_params.get('max_tokens')}"
                )

                # 2. 调用 API
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **adjusted_params
                )

                # 3. 成功返回
                logger.info(f"✅ {model} API 调用成功")
                return response

            except (BrokenPipeError, ConnectionError, OSError) as e:
                # 连接错误 - 使用指数退避重试
                error_name = type(e).__name__
                logger.warning(
                    f"⚠️ 连接错误 ({error_name}): {str(e)[:100]} "
                    f"(尝试 {attempt + 1}/{max_retries})"
                )

                if attempt < max_retries - 1:
                    # 指数退避：2s, 4s, 8s
                    wait_time = base_wait_time * (2 ** attempt)
                    logger.info(f"🔄 等待 {wait_time}s 后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ 连接错误，所有重试已用尽")
                    raise

            except TimeoutError as e:
                # 超时错误 - 重试
                logger.warning(
                    f"⚠️ 请求超时: {str(e)[:100]} "
                    f"(尝试 {attempt + 1}/{max_retries})"
                )

                if attempt < max_retries - 1:
                    wait_time = base_wait_time * (2 ** attempt)
                    logger.info(f"🔄 等待 {wait_time}s 后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ 超时错误，所有重试已用尽")
                    raise

            except Exception as e:
                error_str = str(e)
                error_type = type(e).__name__
                logger.warning(
                    f"⚠️ API 调用失败 ({error_type}): {error_str[:200]} "
                    f"(尝试 {attempt + 1}/{max_retries})"
                )

                # 4. 参数错误处理
                if "max_tokens" in error_str or "400" in error_str:
                    # 参数错误，进一步降低 max_tokens
                    if attempt < max_retries - 1:
                        if 'max_tokens' in adjusted_params:
                            # 减半重试
                            old_value = adjusted_params['max_tokens']
                            adjusted_params['max_tokens'] = old_value // 2
                            kwargs['max_tokens'] = adjusted_params['max_tokens']
                            logger.info(
                                f"🔧 参数错误，降低 max_tokens: {old_value} → "
                                f"{adjusted_params['max_tokens']}，重试中..."
                            )
                            continue

                # 5. 速率限制处理
                if "429" in error_str or "rate_limit" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = base_wait_time * (2 ** attempt) * 2  # 速率限制等待更久
                        logger.info(f"⏳ 速率限制，等待 {wait_time}s 后重试...")
                        time.sleep(wait_time)
                        continue

                # 6. 其他可重试错误
                retriable_errors = ["broken pipe", "connection reset", "connection refused"]
                if any(err in error_str.lower() for err in retriable_errors):
                    if attempt < max_retries - 1:
                        wait_time = base_wait_time * (2 ** attempt)
                        logger.info(f"🔄 网络错误，等待 {wait_time}s 后重试...")
                        time.sleep(wait_time)
                        continue

                # 7. 如果是最后一次尝试，则抛出异常
                if attempt == max_retries - 1:
                    logger.error(f"❌ {model} API 调用失败，所有重试已用尽")
                    raise

        # 理论上不会到这里
        raise RuntimeError("Unexpected error in safe_api_call")

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """
        估算文本的 token 数量

        使用简单的启发式方法：
        - 英文: ~4 字符 = 1 token
        - 中文: ~1.5 字符 = 1 token

        Args:
            text: 输入文本

        Returns:
            估算的 token 数量
        """
        if not text:
            return 0

        # 简单的启发式估算
        # 统计英文和中文字符
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        english_chars = len(text) - chinese_chars

        # 英文约 4 字符 1 token，中文约 1.5 字符 1 token
        estimated_tokens = (english_chars / 4) + (chinese_chars / 1.5)

        return int(estimated_tokens)

    @classmethod
    def get_context_usage(cls, model: str, input_text: str) -> float:
        """
        计算上下文窗口使用率

        Args:
            model: 模型名称
            input_text: 输入文本

        Returns:
            使用率 (0.0 到 1.0)
        """
        limits = cls.get_model_limits(model)
        estimated_tokens = cls.estimate_tokens(input_text)
        context_window = limits['context_window']

        usage = estimated_tokens / context_window

        if usage > 0.9:
            logger.warning(
                f"⚠️ 上下文使用率过高: {usage:.1%} "
                f"({estimated_tokens}/{context_window} tokens)"
            )

        return usage


# 创建默认客户端实例（用于向后兼容）
_default_client = None


def get_default_client() -> ai.Client:
    """获取默认的 aisuite 客户端"""
    global _default_client
    if _default_client is None:
        _default_client = ai.Client()
    return _default_client
