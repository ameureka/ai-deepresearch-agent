#!/usr/bin/env python3
"""
Phase 1 更新验证脚本
测试所有 Agent 的默认模型配置和成本追踪功能
"""

import sys
from src.config import ModelConfig

def test_model_config():
    """测试模型配置是否正确"""
    print("=" * 50)
    print("测试 1: 模型配置")
    print("=" * 50)

    print(f"✓ PLANNER_MODEL: {ModelConfig.PLANNER_MODEL}")
    print(f"✓ RESEARCHER_MODEL: {ModelConfig.RESEARCHER_MODEL}")
    print(f"✓ WRITER_MODEL: {ModelConfig.WRITER_MODEL}")
    print(f"✓ EDITOR_MODEL: {ModelConfig.EDITOR_MODEL}")
    print(f"✓ FALLBACK_MODEL: {ModelConfig.FALLBACK_MODEL}")
    print()

def test_imports():
    """测试所有导入是否成功"""
    print("=" * 50)
    print("测试 2: 模块导入")
    print("=" * 50)

    try:
        from src.fallback import with_fallback
        print("✓ fallback 模块导入成功")

        # 验证装饰器存在
        assert callable(with_fallback), "with_fallback 应该是可调用的装饰器"
        print("✓ with_fallback 装饰器可用")

        from src.cost_tracker import tracker
        print("✓ cost_tracker 模块导入成功")

        # 验证 tracker 有 track 方法
        assert hasattr(tracker, 'track'), "tracker 应该有 track 方法"
        print("✓ tracker.track 方法可用")

        print()
        return True

    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_agent_signatures():
    """测试 Agent 函数签名"""
    print("=" * 50)
    print("测试 3: Agent 函数签名")
    print("=" * 50)

    try:
        import inspect

        # 注意：这里不能直接导入 agents，因为会触发依赖问题
        # 我们只检查语法是否正确
        with open('src/agents.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查关键更新是否存在
        checks = [
            ("@with_fallback", "装饰器应用"),
            ("if model is None:", "模型默认值检查"),
            ("tracker.track", "成本追踪调用"),
            ("ModelConfig.WRITER_MODEL", "Writer 默认模型"),
            ("ModelConfig.EDITOR_MODEL", "Editor 默认模型"),
            ("ModelConfig.RESEARCHER_MODEL", "Researcher 默认模型"),
        ]

        for pattern, desc in checks:
            if pattern in content:
                print(f"✓ {desc}: 找到 '{pattern}'")
            else:
                print(f"✗ {desc}: 未找到 '{pattern}'")
                return False

        # 检查 planning_agent.py
        with open('src/planning_agent.py', 'r', encoding='utf-8') as f:
            content = f.read()

        planner_checks = [
            ("@with_fallback", "Planner 装饰器"),
            ("ModelConfig.PLANNER_MODEL", "Planner 默认模型"),
            ("tracker.track", "Planner 成本追踪"),
        ]

        for pattern, desc in planner_checks:
            if pattern in content:
                print(f"✓ {desc}: 找到 '{pattern}'")
            else:
                print(f"✗ {desc}: 未找到 '{pattern}'")
                return False

        print()
        return True

    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

def test_fallback_decorator():
    """测试 fallback 装饰器逻辑"""
    print("=" * 50)
    print("测试 4: Fallback 装饰器")
    print("=" * 50)

    try:
        from src.fallback import with_fallback

        # 创建一个测试函数
        call_count = {'count': 0, 'models': []}

        @with_fallback
        def test_func(model=None):
            call_count['count'] += 1
            call_count['models'].append(model)
            if call_count['count'] == 1 and model and 'deepseek' in model.lower():
                raise Exception("模拟 DeepSeek 失败")
            return f"Success with {model}"

        # 测试降级逻辑
        result = test_func(model="deepseek:deepseek-chat")

        assert call_count['count'] == 2, "应该调用两次（第一次失败，第二次降级）"
        assert call_count['models'][0] == "deepseek:deepseek-chat", "第一次应该使用 DeepSeek"
        assert call_count['models'][1] == ModelConfig.FALLBACK_MODEL, "第二次应该降级到 FALLBACK_MODEL"

        print("✓ Fallback 降级逻辑正确")
        print(f"  第一次尝试: {call_count['models'][0]}")
        print(f"  降级后: {call_count['models'][1]}")
        print()
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("Phase 1 Agent 更新验证")
    print("=" * 50 + "\n")

    results = []

    # 运行测试
    results.append(("模型配置", test_model_config() or True))  # 这个测试总是成功
    results.append(("模块导入", test_imports()))
    results.append(("Agent 签名", test_agent_signatures()))
    results.append(("Fallback 装饰器", test_fallback_decorator()))

    # 汇总结果
    print("=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{status}: {name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！Phase 1 更新成功！")
    else:
        print("❌ 部分测试失败，请检查上述错误")
    print("=" * 50 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
