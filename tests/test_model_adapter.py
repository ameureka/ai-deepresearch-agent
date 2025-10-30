"""
单元测试 - ModelAdapter 模型适配器

测试范围:
- 模型限制获取
- 参数验证和调整
- Token 估算
- 上下文使用率计算
"""

import pytest
from src.model_adapter import ModelAdapter


def test_get_model_limits_deepseek_chat():
    """测试 DeepSeek Chat 模型限制"""
    limits = ModelAdapter.get_model_limits("deepseek:deepseek-chat")

    assert limits["max_tokens"] == 8192
    assert limits["context_window"] == 32768
    assert limits["supports_streaming"] is True


def test_get_model_limits_deepseek_reasoner():
    """测试 DeepSeek Reasoner 模型限制"""
    limits = ModelAdapter.get_model_limits("deepseek:deepseek-reasoner")

    assert limits["max_tokens"] == 8192
    assert limits["context_window"] == 65536
    assert limits["supports_streaming"] is False


def test_get_model_limits_openai():
    """测试 OpenAI 模型限制"""
    limits = ModelAdapter.get_model_limits("openai:gpt-4o-mini")

    assert limits["max_tokens"] == 16384
    assert limits["context_window"] == 128000
    assert limits["supports_streaming"] is True


def test_get_model_limits_unknown():
    """测试未知模型返回保守默认值"""
    limits = ModelAdapter.get_model_limits("unknown:model")

    assert limits["max_tokens"] == 4096
    assert limits["context_window"] == 8192


def test_validate_and_adjust_params_within_limit():
    """测试参数在限制内不调整"""
    adjusted = ModelAdapter.validate_and_adjust_params(
        "deepseek:deepseek-chat",
        max_tokens=5000,
        temperature=0
    )

    assert adjusted["max_tokens"] == 5000
    assert adjusted["temperature"] == 0


def test_validate_and_adjust_params_exceed_limit():
    """测试参数超过限制时自动调整"""
    adjusted = ModelAdapter.validate_and_adjust_params(
        "deepseek:deepseek-chat",
        max_tokens=15000,  # 超过 8192
        temperature=0
    )

    # 应该被调整为限制值
    assert adjusted["max_tokens"] == 8192
    assert adjusted["temperature"] == 0


def test_validate_and_adjust_params_no_max_tokens():
    """测试未设置 max_tokens 时使用默认值"""
    adjusted = ModelAdapter.validate_and_adjust_params(
        "deepseek:deepseek-chat",
        temperature=0
    )

    # 应该设置为 80% 的限制值
    expected_default = int(8192 * 0.8)
    assert adjusted["max_tokens"] == expected_default
    assert adjusted["temperature"] == 0


def test_validate_and_adjust_params_openai():
    """测试 OpenAI 模型参数调整"""
    adjusted = ModelAdapter.validate_and_adjust_params(
        "openai:gpt-4o-mini",
        max_tokens=20000,  # 超过 16384
        temperature=0.5
    )

    assert adjusted["max_tokens"] == 16384
    assert adjusted["temperature"] == 0.5


def test_estimate_tokens_empty():
    """测试空文本 token 估算"""
    tokens = ModelAdapter.estimate_tokens("")
    assert tokens == 0


def test_estimate_tokens_english():
    """测试英文文本 token 估算"""
    text = "Hello world! This is a test."  # ~7 个单词
    tokens = ModelAdapter.estimate_tokens(text)

    # 英文约 4 字符 1 token，这里约 29 字符，估算约 7 tokens
    assert 5 <= tokens <= 10


def test_estimate_tokens_chinese():
    """测试中文文本 token 估算"""
    text = "你好世界！这是一个测试。"  # 12 个中文字符
    tokens = ModelAdapter.estimate_tokens(text)

    # 中文约 1.5 字符 1 token，12 字符估算约 8 tokens
    assert 6 <= tokens <= 10


def test_estimate_tokens_mixed():
    """测试中英文混合文本 token 估算"""
    text = "Hello 你好 World 世界"  # 混合文本
    tokens = ModelAdapter.estimate_tokens(text)

    # 应该返回合理的估算值
    assert tokens > 0
    assert tokens < 100


def test_get_context_usage():
    """测试上下文使用率计算"""
    # 创建一个约 1000 tokens 的文本（4000 字符）
    text = "x" * 4000

    usage = ModelAdapter.get_context_usage("deepseek:deepseek-chat", text)

    # DeepSeek chat 上下文窗口为 32768
    # 1000 / 32768 ≈ 0.03 (3%)
    assert 0 < usage < 0.1


def test_get_context_usage_high():
    """测试高上下文使用率"""
    # 创建一个约 30000 tokens 的文本（120000 字符）
    text = "x" * 120000

    usage = ModelAdapter.get_context_usage("deepseek:deepseek-chat", text)

    # 30000 / 32768 ≈ 0.91 (91%)
    assert usage > 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
