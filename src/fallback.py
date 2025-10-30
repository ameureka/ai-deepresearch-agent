"""
模型降级装饰器模块 - 提供自动降级功能

本模块包含：
1. with_fallback: 装饰器函数，当主模型失败时自动降级到 OpenAI 模型
"""

import logging
from functools import wraps
from src.config import ModelConfig

logger = logging.getLogger(__name__)


def with_fallback(agent_func):
    """
    增强的模型降级装饰器 - 智能处理参数错误和模型失败

    用法:
        @with_fallback
        def some_agent(prompt: str, model: str = None):
            # agent 实现
            pass

    工作原理:
        1. 首先尝试使用指定的模型执行函数
        2. 如果遇到参数错误（400），ModelAdapter.safe_api_call 会自动调整参数重试
        3. 如果模型包含 "deepseek" 且执行失败（非参数错误），降级到 FALLBACK_MODEL
        4. 如果降级模型也失败，则抛出原始异常

    错误处理策略:
        - 400 错误（参数错误）：由 ModelAdapter 自动处理
        - 429 错误（速率限制）：等待后重试（由 ModelAdapter 处理）
        - 500 错误（模型错误）：降级到 OpenAI
        - 其他错误：直接抛出

    参数:
        agent_func: 被装饰的 agent 函数

    返回:
        包装后的函数
    """
    @wraps(agent_func)
    def wrapper(*args, **kwargs):
        model = kwargs.get('model')
        max_fallback_retries = 1  # 降级最多重试 1 次

        for attempt in range(max_fallback_retries + 1):
            try:
                return agent_func(*args, **kwargs)

            except (BrokenPipeError, ConnectionError, OSError, TimeoutError) as e:
                # 网络连接错误 - 直接降级到 OpenAI（通常更稳定）
                error_name = type(e).__name__
                logger.warning(
                    f"⚠️ 网络连接错误 ({error_name}): {str(e)[:100]} "
                    f"(尝试 {attempt + 1}/{max_fallback_retries + 1})"
                )

                # 对于连接错误，立即降级到 OpenAI
                if model and "deepseek" in model.lower() and attempt < max_fallback_retries:
                    logger.warning(
                        f"🔄 网络错误，{model} 降级到 {ModelConfig.FALLBACK_MODEL}"
                    )
                    kwargs['model'] = ModelConfig.FALLBACK_MODEL
                    model = ModelConfig.FALLBACK_MODEL
                    continue
                else:
                    logger.error(f"❌ 网络错误，降级也失败")
                    raise

            except Exception as e:
                error_str = str(e)
                error_type = type(e).__name__

                # 识别错误类型
                is_rate_limit = "429" in error_str or "rate_limit" in error_str.lower()
                is_model_error = "500" in error_str or "internal_error" in error_str.lower()
                is_param_error = "400" in error_str or "max_tokens" in error_str.lower()
                is_connection_error = any(
                    err in error_str.lower()
                    for err in ["broken pipe", "connection reset", "connection refused", "connection error"]
                )

                # 记录详细错误信息
                logger.warning(
                    f"⚠️ Agent 执行失败 ({error_type}): {error_str[:200]} "
                    f"(尝试 {attempt + 1}/{max_fallback_retries + 1}), 模型={model}"
                )

                # 参数错误应该已经由 ModelAdapter 处理，如果还是失败，说明无法修复
                if is_param_error:
                    logger.error(
                        "❌ 参数错误未被 ModelAdapter 修复，这可能是一个 bug"
                    )

                # 仅对 DeepSeek 模型进行降级（且不是参数错误）
                if model and "deepseek" in model.lower() and attempt < max_fallback_retries:
                    if is_model_error or is_rate_limit or is_connection_error or not is_param_error:
                        logger.warning(
                            f"🔄 {model} 失败，降级到 {ModelConfig.FALLBACK_MODEL}"
                        )
                        kwargs['model'] = ModelConfig.FALLBACK_MODEL
                        model = ModelConfig.FALLBACK_MODEL  # 更新 model 变量
                        continue

                # 所有尝试失败，抛出异常
                if attempt == max_fallback_retries:
                    logger.error(
                        f"❌ Agent 执行失败，所有重试已用尽: {error_str[:200]}"
                    )
                raise

        # 理论上不会到这里
        raise RuntimeError("Unexpected error in fallback wrapper")

    return wrapper
