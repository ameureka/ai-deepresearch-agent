"""
单元测试 - ContextManager 上下文管理器

测试范围:
- 分块策略决策
- 上下文使用率计算
- 文本处理流程
- 成本估算
"""

import pytest
from src.context_manager import ContextManager, create_manager_for_agent


@pytest.fixture
def manager():
    """创建默认的上下文管理器"""
    return ContextManager(
        model="deepseek:deepseek-chat",
        enable_chunking=True,
        chunking_threshold=0.8
    )


def test_initialization():
    """测试上下文管理器初始化"""
    manager = ContextManager(
        model="deepseek:deepseek-chat",
        enable_chunking=True,
        chunking_threshold=0.7,
        max_chunk_size=5000,
        chunk_overlap=100
    )

    assert manager.model == "deepseek:deepseek-chat"
    assert manager.enable_chunking is True
    assert manager.chunking_threshold == 0.7
    assert manager.chunking_processor.max_chunk_size == 5000
    assert manager.chunking_processor.overlap_size == 100


def test_initialization_from_env(monkeypatch):
    """测试从环境变量初始化"""
    # 设置环境变量
    monkeypatch.setenv("ENABLE_CHUNKING", "false")
    monkeypatch.setenv("CHUNKING_THRESHOLD", "0.6")
    monkeypatch.setenv("MAX_CHUNK_SIZE", "7000")
    monkeypatch.setenv("CHUNK_OVERLAP", "300")

    manager = ContextManager(model="deepseek:deepseek-chat")

    assert manager.enable_chunking is False
    assert manager.chunking_threshold == 0.6
    assert manager.chunking_processor.max_chunk_size == 7000
    assert manager.chunking_processor.overlap_size == 300


def test_should_chunk_disabled():
    """测试禁用分块时不分块"""
    manager = ContextManager(
        model="deepseek:deepseek-chat",
        enable_chunking=False
    )

    # 即使文本很长，也不应该分块
    long_text = "x" * 100000
    assert manager.should_chunk(long_text) is False


def test_should_chunk_short_text(manager):
    """测试短文本不需要分块"""
    # 短文本（远低于阈值）
    text = "Short text with a few words."

    assert manager.should_chunk(text) is False


def test_should_chunk_long_text():
    """测试长文本需要分块"""
    manager = ContextManager(
        model="deepseek:deepseek-chat",
        enable_chunking=True,
        chunking_threshold=0.5  # 50% 的阈值
    )

    # 创建超过阈值的文本
    # DeepSeek chat 上下文窗口为 32768，50% 为 16384 tokens
    # 约 65536 字符（16384 * 4）
    long_text = "x" * 70000

    assert manager.should_chunk(long_text) is True


def test_get_context_usage(manager):
    """测试上下文使用率计算"""
    text = "Hello world! " * 100  # 约 1300 字符，约 325 tokens

    usage = manager.get_context_usage(text)

    # DeepSeek chat 上下文窗口为 32768
    # 325 / 32768 ≈ 0.01 (1%)
    assert 0 < usage < 0.05


def test_process_text_short():
    """测试处理短文本（直接模式）"""
    manager = ContextManager(
        model="deepseek:deepseek-chat",
        enable_chunking=True,
        chunking_threshold=0.8
    )

    text = "Short text for processing."

    # 简单的处理函数
    def processor(t):
        return t.upper()

    result = manager.process_text(text, processor, show_progress=False)

    # 应该直接处理，不分块
    assert result == "SHORT TEXT FOR PROCESSING."


def test_process_text_long():
    """测试处理长文本（分块模式）"""
    manager = ContextManager(
        model="deepseek:deepseek-chat",
        enable_chunking=True,
        chunking_threshold=0.1,  # 很低的阈值，强制分块
        max_chunk_size=100,
        chunk_overlap=10
    )

    # 创建长文本
    text = "\n\n".join([f"Paragraph {i}." for i in range(10)])

    # 简单的处理函数
    def processor(t):
        return "[PROCESSED]"

    result = manager.process_text(text, processor, show_progress=False)

    # 应该分块处理
    assert "[PROCESSED]" in result


def test_process_text_force_chunking():
    """测试强制分块"""
    manager = ContextManager(
        model="deepseek:deepseek-chat",
        enable_chunking=True,
        max_chunk_size=100
    )

    text = "Short text."

    # 强制分块，即使文本很短
    def processor(t):
        return t.upper()

    result = manager.process_text(
        text,
        processor,
        force_chunking=True,
        show_progress=False
    )

    # 应该处理成功
    assert "SHORT TEXT" in result


def test_estimate_cost_short():
    """测试短文本成本估算"""
    manager = ContextManager(model="deepseek:deepseek-chat")

    text = "Hello world! " * 10  # 约 130 字符，约 32 tokens

    estimate = manager.estimate_cost(text)

    assert estimate['input_tokens'] > 0
    assert estimate['needs_chunking'] is False
    assert estimate['num_chunks'] == 1
    assert estimate['api_calls'] == 1
    assert estimate['estimated_cost_usd'] > 0
    assert 0 < estimate['context_usage'] < 1


def test_estimate_cost_long():
    """测试长文本成本估算"""
    manager = ContextManager(
        model="deepseek:deepseek-chat",
        enable_chunking=True,
        chunking_threshold=0.1,  # 很低的阈值
        max_chunk_size=1000
    )

    # 创建长文本（约 5000 tokens）
    text = "x" * 20000

    estimate = manager.estimate_cost(text)

    assert estimate['input_tokens'] > 1000
    assert estimate['needs_chunking'] is True
    assert estimate['num_chunks'] > 1
    assert estimate['api_calls'] > 1
    # 分块会有重叠开销
    assert estimate['total_tokens_with_overhead'] > estimate['input_tokens']


def test_create_manager_for_agent():
    """测试为 Agent 创建管理器"""
    manager = create_manager_for_agent("test_agent", "deepseek:deepseek-chat")

    assert isinstance(manager, ContextManager)
    assert manager.model == "deepseek:deepseek-chat"


def test_model_limits():
    """测试获取模型限制"""
    manager = ContextManager(model="deepseek:deepseek-chat")

    assert manager.limits['max_tokens'] == 8192
    assert manager.limits['context_window'] == 32768


def test_chunking_threshold():
    """测试分块阈值计算"""
    manager = ContextManager(
        model="deepseek:deepseek-chat",
        chunking_threshold=0.8
    )

    # 阈值应该是 80% 的上下文窗口
    # 32768 * 0.8 = 26214 tokens ≈ 104856 字符
    threshold_text = "x" * 105000

    # 应该触发分块
    assert manager.should_chunk(threshold_text) is True

    # 略低于阈值
    below_threshold = "x" * 100000
    assert manager.should_chunk(below_threshold) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
