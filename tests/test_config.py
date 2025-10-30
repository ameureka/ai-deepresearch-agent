"""
单元测试 - ModelConfig 配置管理

测试范围：
- 默认模型配置
- get_model() 方法
- validate() 方法
- summary() 方法
"""

import os
import pytest
from src.config import ModelConfig


def test_default_models():
    """测试默认模型配置"""
    assert ModelConfig.PLANNER_MODEL == "deepseek:deepseek-reasoner"
    assert ModelConfig.RESEARCHER_MODEL == "deepseek:deepseek-chat"
    assert ModelConfig.WRITER_MODEL == "deepseek:deepseek-chat"
    assert ModelConfig.EDITOR_MODEL == "deepseek:deepseek-chat"
    assert ModelConfig.FALLBACK_MODEL == "openai:gpt-4o-mini"


def test_get_model():
    """测试 get_model 方法"""
    assert ModelConfig.get_model("planner") == "deepseek:deepseek-reasoner"
    assert ModelConfig.get_model("researcher") == "deepseek:deepseek-chat"
    assert ModelConfig.get_model("writer") == "deepseek:deepseek-chat"
    assert ModelConfig.get_model("editor") == "deepseek:deepseek-chat"
    assert ModelConfig.get_model("PLANNER") == "deepseek:deepseek-reasoner"  # 大小写不敏感


def test_get_model_unknown():
    """测试未知代理类型"""
    assert ModelConfig.get_model("unknown") is None


def test_request_timeout():
    """测试请求超时配置"""
    assert ModelConfig.REQUEST_TIMEOUT == 90


def test_summary():
    """测试配置摘要生成"""
    summary = ModelConfig.summary()

    assert "models" in summary
    assert "timeout" in summary
    assert "api_keys_configured" in summary

    assert summary["models"]["planner"] == "deepseek:deepseek-reasoner"
    assert summary["models"]["researcher"] == "deepseek:deepseek-chat"
    assert summary["models"]["writer"] == "deepseek:deepseek-chat"
    assert summary["models"]["editor"] == "deepseek:deepseek-chat"
    assert summary["models"]["fallback"] == "openai:gpt-4o-mini"

    assert summary["timeout"] == 90


def test_validate_missing_deepseek_key(monkeypatch):
    """测试缺少 DeepSeek API Key 的情况"""
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

    with pytest.raises(ValueError, match="DEEPSEEK_API_KEY 未设置"):
        ModelConfig.validate()


def test_validate_missing_openai_key(monkeypatch):
    """测试缺少 OpenAI API Key 的情况"""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-key")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY 未设置"):
        ModelConfig.validate()


def test_validate_invalid_deepseek_key(monkeypatch):
    """测试无效的 DeepSeek API Key 格式"""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "invalid-key")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

    with pytest.raises(ValueError, match="DEEPSEEK_API_KEY 格式无效"):
        ModelConfig.validate()


def test_validate_invalid_openai_key(monkeypatch):
    """测试无效的 OpenAI API Key 格式"""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "invalid-key")

    with pytest.raises(ValueError, match="OPENAI_API_KEY 格式无效"):
        ModelConfig.validate()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
