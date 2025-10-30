"""
单元测试 - CostTracker 成本追踪

测试范围：
- 成本计算准确性
- 累计统计
- 摘要生成
- 对比功能
"""

import pytest
from src.cost_tracker import CostTracker


def test_track_cost_deepseek_chat():
    """测试 DeepSeek Chat 成本计算"""
    tracker = CostTracker()
    cost = tracker.track("deepseek:deepseek-chat", 1000, 500)

    # 期望成本 = (1000/1M * 0.14) + (500/1M * 0.28)
    expected = (1000 / 1_000_000 * 0.14) + (500 / 1_000_000 * 0.28)
    assert abs(cost - expected) < 0.000001


def test_track_cost_deepseek_reasoner():
    """测试 DeepSeek Reasoner 成本计算"""
    tracker = CostTracker()
    cost = tracker.track("deepseek:deepseek-reasoner", 1000, 500)

    # 期望成本 = (1000/1M * 0.55) + (500/1M * 2.19)
    expected = (1000 / 1_000_000 * 0.55) + (500 / 1_000_000 * 2.19)
    assert abs(cost - expected) < 0.000001


def test_track_cost_openai():
    """测试 OpenAI 成本计算"""
    tracker = CostTracker()
    cost = tracker.track("openai:gpt-4o-mini", 1000, 500)

    # 期望成本 = (1000/1M * 0.15) + (500/1M * 0.60)
    expected = (1000 / 1_000_000 * 0.15) + (500 / 1_000_000 * 0.60)
    assert abs(cost - expected) < 0.000001


def test_track_unknown_model():
    """测试未知模型"""
    tracker = CostTracker()
    cost = tracker.track("unknown:model", 1000, 500)
    assert cost == 0.0


def test_accumulate_costs():
    """测试成本累计"""
    tracker = CostTracker()

    # 第一次调用
    tracker.track("deepseek:deepseek-chat", 1000, 500)
    # 第二次调用
    tracker.track("deepseek:deepseek-chat", 2000, 1000)

    # 验证累计成本
    expected_total = (
        (1000 / 1_000_000 * 0.14) + (500 / 1_000_000 * 0.28) +
        (2000 / 1_000_000 * 0.14) + (1000 / 1_000_000 * 0.28)
    )
    assert abs(tracker.costs["deepseek:deepseek-chat"] - expected_total) < 0.000001


def test_accumulate_calls():
    """测试调用次数累计"""
    tracker = CostTracker()

    tracker.track("deepseek:deepseek-chat", 1000, 500)
    tracker.track("deepseek:deepseek-chat", 2000, 1000)
    tracker.track("openai:gpt-4o-mini", 1000, 500)

    assert tracker.calls["deepseek:deepseek-chat"] == 2
    assert tracker.calls["openai:gpt-4o-mini"] == 1


def test_accumulate_tokens():
    """测试 token 使用累计"""
    tracker = CostTracker()

    tracker.track("deepseek:deepseek-chat", 1000, 500)
    tracker.track("deepseek:deepseek-chat", 2000, 1000)

    assert tracker.tokens["deepseek:deepseek-chat"]["input"] == 3000
    assert tracker.tokens["deepseek:deepseek-chat"]["output"] == 1500


def test_summary():
    """测试摘要生成"""
    tracker = CostTracker()

    tracker.track("deepseek:deepseek-chat", 1000, 500)
    tracker.track("openai:gpt-4o-mini", 2000, 1000)

    summary = tracker.summary()

    assert "total_cost" in summary
    assert "total_calls" in summary
    assert "by_model" in summary
    assert "history_count" in summary

    assert summary["total_calls"] == 2
    assert summary["history_count"] == 2
    assert "deepseek:deepseek-chat" in summary["by_model"]
    assert "openai:gpt-4o-mini" in summary["by_model"]


def test_summary_by_model():
    """测试按模型分组的摘要"""
    tracker = CostTracker()

    tracker.track("deepseek:deepseek-chat", 1000, 500)
    tracker.track("deepseek:deepseek-chat", 2000, 1000)

    summary = tracker.summary()
    deepseek_stats = summary["by_model"]["deepseek:deepseek-chat"]

    assert deepseek_stats["calls"] == 2
    assert deepseek_stats["tokens"]["input"] == 3000
    assert deepseek_stats["tokens"]["output"] == 1500
    assert "avg_cost_per_call" in deepseek_stats


def test_compare():
    """测试成本对比"""
    tracker = CostTracker()

    # 当前成本
    tracker.track("deepseek:deepseek-chat", 5000, 3000)

    # 基准成本（假设使用 OpenAI 的成本）
    baseline = {
        "openai:gpt-4o-mini": 0.0127  # 假设值
    }

    comparison = tracker.compare(baseline)

    assert "current_cost" in comparison
    assert "baseline_cost" in comparison
    assert "savings" in comparison
    assert "savings_percentage" in comparison
    assert "by_model" in comparison


def test_compare_savings():
    """测试成本节省计算"""
    tracker = CostTracker()

    # DeepSeek 成本
    tracker.track("deepseek:deepseek-chat", 5000, 3000)
    current_cost = tracker.costs["deepseek:deepseek-chat"]

    # 假设 OpenAI 成本更高
    baseline_cost = current_cost * 2

    comparison = tracker.compare({"openai:gpt-4o-mini": baseline_cost})

    # 验证节省百分比
    assert comparison["savings_percentage"] > 0
    assert abs(comparison["savings_percentage"] - 50.0) < 0.1  # 应该约为 50%


def test_reset():
    """测试重置功能"""
    tracker = CostTracker()

    tracker.track("deepseek:deepseek-chat", 1000, 500)
    tracker.track("openai:gpt-4o-mini", 2000, 1000)

    # 验证有数据
    assert len(tracker.costs) > 0
    assert len(tracker.calls) > 0
    assert len(tracker.history) > 0

    # 重置
    tracker.reset()

    # 验证已清空
    assert len(tracker.costs) == 0
    assert len(tracker.calls) == 0
    assert len(tracker.tokens) == 0
    assert len(tracker.history) == 0


def test_track_with_metadata():
    """测试带元数据的追踪"""
    tracker = CostTracker()

    metadata = {"agent": "research_agent", "task_id": "123"}
    tracker.track("deepseek:deepseek-chat", 1000, 500, metadata=metadata)

    assert len(tracker.history) == 1
    assert tracker.history[0]["metadata"] == metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
