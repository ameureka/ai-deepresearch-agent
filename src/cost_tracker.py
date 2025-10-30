"""
成本追踪模块 - 追踪和分析 API 调用成本

本模块提供：
1. CostTracker: API 调用成本追踪类
2. 价格表管理
3. 成本统计和对比功能
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CostTracker:
    """
    API 调用成本追踪器

    功能：
    - 追踪每次 API 调用的 token 使用和成本
    - 按模型分组统计
    - 生成成本摘要报告
    - 对比不同配置的成本

    使用示例：
        >>> tracker = CostTracker()
        >>> cost = tracker.track("deepseek:deepseek-chat", 1000, 500)
        >>> print(f"本次调用成本: ${cost:.6f}")
        >>> summary = tracker.summary()
        >>> print(f"总成本: ${summary['total_cost']:.4f}")
    """

    # 价格表（每百万 token 的价格，单位：美元）
    PRICES = {
        "deepseek:deepseek-chat": {
            "input": 0.14,
            "output": 0.28,
        },
        "deepseek:deepseek-reasoner": {
            "input": 0.55,
            "output": 2.19,
        },
        "openai:gpt-4o-mini": {
            "input": 0.15,
            "output": 0.60,
        },
        "openai:o1-mini": {
            "input": 3.00,
            "output": 12.00,
        },
    }

    def __init__(self):
        """初始化成本追踪器"""
        # 按模型统计的成本
        self.costs: Dict[str, float] = {}

        # 按模型统计的调用次数
        self.calls: Dict[str, int] = {}

        # 按模型统计的 token 使用
        self.tokens: Dict[str, Dict[str, int]] = {}

        # 调用历史记录
        self.history: list = []

        logger.info("💰 成本追踪器已初始化")

    def track(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        记录一次 API 调用的成本

        参数:
            model: 模型名称（如 "deepseek:deepseek-chat"）
            input_tokens: 输入 token 数量
            output_tokens: 输出 token 数量
            metadata: 可选的元数据（如 agent 名称、任务 ID 等）

        返回:
            float: 本次调用的成本（美元）

        示例:
            >>> tracker.track("deepseek:deepseek-chat", 1000, 500)
            0.00028
        """
        # 检查模型是否在价格表中
        if model not in self.PRICES:
            logger.warning(f"⚠️  未知模型: {model}，无法计算成本")
            return 0.0

        # 获取价格
        prices = self.PRICES[model]
        input_price = prices["input"]
        output_price = prices["output"]

        # 计算成本（每百万 token）
        input_cost = (input_tokens / 1_000_000) * input_price
        output_cost = (output_tokens / 1_000_000) * output_price
        total_cost = input_cost + output_cost

        # 累计统计
        self.costs[model] = self.costs.get(model, 0.0) + total_cost
        self.calls[model] = self.calls.get(model, 0) + 1

        # 累计 token 使用
        if model not in self.tokens:
            self.tokens[model] = {"input": 0, "output": 0}
        self.tokens[model]["input"] += input_tokens
        self.tokens[model]["output"] += output_tokens

        # 记录调用历史
        record = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost,
            "metadata": metadata or {},
        }
        self.history.append(record)

        # 日志输出
        logger.info(
            f"💰 {model}: ${total_cost:.6f} "
            f"({input_tokens} in, {output_tokens} out)"
        )

        return total_cost

    def summary(self) -> Dict[str, Any]:
        """
        生成成本摘要报告

        返回:
            dict: 包含总成本、总调用次数和按模型分组的详细信息

        示例:
            >>> summary = tracker.summary()
            >>> print(f"总成本: ${summary['total_cost']:.4f}")
            >>> print(f"总调用次数: {summary['total_calls']}")
        """
        total_cost = sum(self.costs.values())
        total_calls = sum(self.calls.values())

        by_model = {}
        for model in set(list(self.costs.keys()) + list(self.calls.keys())):
            by_model[model] = {
                "cost": self.costs.get(model, 0.0),
                "calls": self.calls.get(model, 0),
                "tokens": self.tokens.get(model, {"input": 0, "output": 0}),
                "avg_cost_per_call": (
                    self.costs.get(model, 0.0) / self.calls.get(model, 1)
                    if self.calls.get(model, 0) > 0
                    else 0.0
                ),
            }

        return {
            "total_cost": total_cost,
            "total_calls": total_calls,
            "by_model": by_model,
            "history_count": len(self.history),
        }

    def compare(self, baseline: Dict[str, float]) -> Dict[str, Any]:
        """
        对比当前成本与基准成本

        参数:
            baseline: 基准成本字典，格式为 {model: cost}

        返回:
            dict: 包含成本对比和节省百分比的字典

        示例:
            >>> baseline = {"openai:gpt-4o-mini": 0.0238}
            >>> comparison = tracker.compare(baseline)
            >>> print(f"成本节省: {comparison['savings_percentage']:.1f}%")
        """
        current_total = sum(self.costs.values())
        baseline_total = sum(baseline.values())

        if baseline_total == 0:
            savings_percentage = 0.0
        else:
            savings_percentage = (
                (baseline_total - current_total) / baseline_total * 100
            )

        return {
            "current_cost": current_total,
            "baseline_cost": baseline_total,
            "savings": baseline_total - current_total,
            "savings_percentage": savings_percentage,
            "by_model": {
                model: {
                    "current": self.costs.get(model, 0.0),
                    "baseline": baseline.get(model, 0.0),
                    "diff": baseline.get(model, 0.0) - self.costs.get(model, 0.0),
                }
                for model in set(list(self.costs.keys()) + list(baseline.keys()))
            },
        }

    def print_summary(self):
        """打印格式化的成本摘要"""
        summary = self.summary()

        print("\n" + "=" * 60)
        print("   成本追踪摘要")
        print("=" * 60)

        print(f"\n💰 总成本: ${summary['total_cost']:.6f}")
        print(f"📞 总调用次数: {summary['total_calls']}")

        if summary['by_model']:
            print("\n按模型统计:")
            print("-" * 60)
            for model, stats in summary['by_model'].items():
                print(f"\n📦 {model}:")
                print(f"  • 成本: ${stats['cost']:.6f}")
                print(f"  • 调用次数: {stats['calls']}")
                print(f"  • 平均成本/调用: ${stats['avg_cost_per_call']:.6f}")
                print(f"  • Token 使用: {stats['tokens']['input']} in, {stats['tokens']['output']} out")

        print("\n" + "=" * 60 + "\n")

    def reset(self):
        """重置所有统计数据"""
        self.costs.clear()
        self.calls.clear()
        self.tokens.clear()
        self.history.clear()
        logger.info("♻️  成本追踪器已重置")


# 全局单例实例
tracker = CostTracker()
