#!/usr/bin/env python3
"""
配置验证脚本

用途：
- 验证所有必需的环境变量
- 检查 API Key 格式
- 验证 aisuite 版本
- 输出配置摘要

运行方法：
    python scripts/check_config.py
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from src.config import ModelConfig


def check_aisuite_version():
    """检查 aisuite 版本"""
    print("\n🔍 检查 aisuite 版本...")
    try:
        import aisuite
        version = aisuite.__version__

        # 解析版本号
        major, minor, patch = map(int, version.split('.'))

        if (major, minor, patch) >= (0, 1, 12):
            print(f"✅ aisuite 版本: {version} (>= 0.1.12)")
            return True
        else:
            print(f"❌ aisuite 版本: {version} (需要 >= 0.1.12)")
            print("请运行: pip install --upgrade aisuite")
            return False
    except ImportError:
        print("❌ aisuite 未安装")
        print("请运行: pip install aisuite")
        return False
    except Exception as e:
        print(f"❌ 版本检查失败: {e}")
        return False


def check_api_keys():
    """检查 API Keys"""
    print("\n🔑 检查 API Keys...")

    keys_to_check = {
        "DEEPSEEK_API_KEY": "DeepSeek",
        "OPENAI_API_KEY": "OpenAI",
        "TAVILY_API_KEY": "Tavily",
    }

    all_valid = True
    for key_name, service_name in keys_to_check.items():
        key_value = os.getenv(key_name)

        if not key_value:
            print(f"❌ {service_name} API Key ({key_name}) 未设置")
            all_valid = False
        elif key_value in ["your-key-here", "sk-your-key-here", "tvly-your-key-here"]:
            print(f"⚠️  {service_name} API Key ({key_name}) 使用占位符值，请替换为真实 Key")
            all_valid = False
        else:
            # 隐藏 Key 的中间部分
            masked = key_value[:7] + "..." + key_value[-4:] if len(key_value) > 11 else "***"
            print(f"✅ {service_name} API Key: {masked}")

    return all_valid


def main():
    """主函数"""
    print("=" * 60)
    print("   配置验证脚本")
    print("=" * 60)

    # 加载 .env 文件
    print("\n📂 加载 .env 文件...")
    load_dotenv()

    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        print(f"✅ 找到 .env 文件: {env_path}")
    else:
        print(f"⚠️  未找到 .env 文件: {env_path}")
        print("请从 .env.example 复制并配置")

    # 检查 aisuite 版本
    aisuite_ok = check_aisuite_version()

    # 检查 API Keys
    keys_ok = check_api_keys()

    # 验证配置
    print("\n⚙️  验证模型配置...")
    try:
        ModelConfig.validate()

        # 打印配置摘要
        print("\n📊 配置摘要:")
        print("-" * 60)
        summary = ModelConfig.summary()

        print("\n模型配置:")
        for agent, model in summary["models"].items():
            print(f"  • {agent.capitalize():<12}: {model}")

        print(f"\n请求超时: {summary['timeout']} 秒")

        config_ok = True
    except ValueError as e:
        print(f"❌ 配置验证失败:")
        print(f"   {e}")
        config_ok = False

    # 总结
    print("\n" + "=" * 60)
    if aisuite_ok and keys_ok and config_ok:
        print("✅ 所有检查通过！系统已准备好运行。")
        print("=" * 60)
        return 0
    else:
        print("❌ 部分检查失败，请修复上述问题。")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
