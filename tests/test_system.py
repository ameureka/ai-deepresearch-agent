#!/usr/bin/env python3
"""
完整系统测试脚本
测试 Phase 1 实施后的系统功能
"""

import requests
import json
import time
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_homepage():
    """测试首页访问"""
    print("1️⃣ 测试首页访问...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200 and "Reflective Research Agents" in response.text:
            print("✅ 首页访问成功")
            return True
        else:
            print(f"❌ 首页访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 首页访问异常: {e}")
        return False

def test_health_check():
    """测试健康检查端点"""
    print("\n2️⃣ 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_config():
    """测试配置"""
    print("\n3️⃣ 测试配置...")
    try:
        from src.config import ModelConfig
        
        print(f"   Planner Model: {ModelConfig.PLANNER_MODEL}")
        print(f"   Researcher Model: {ModelConfig.RESEARCHER_MODEL}")
        print(f"   Writer Model: {ModelConfig.WRITER_MODEL}")
        print(f"   Editor Model: {ModelConfig.EDITOR_MODEL}")
        print(f"   Fallback Model: {ModelConfig.FALLBACK_MODEL}")
        
        # 验证配置
        ModelConfig.validate()
        print("✅ 配置验证通过")
        return True
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

def test_cost_tracker():
    """测试成本追踪"""
    print("\n4️⃣ 测试成本追踪...")
    try:
        from src.cost_tracker import CostTracker
        
        tracker = CostTracker()
        
        # 模拟一些调用
        tracker.track('deepseek:deepseek-chat', 1000, 500)
        tracker.track('deepseek:deepseek-reasoner', 500, 200)
        
        summary = tracker.summary()
        print(f"   总成本: ${summary['total_cost']:.6f}")
        print(f"   总调用次数: {summary['total_calls']}")
        print("✅ 成本追踪功能正常")
        return True
    except Exception as e:
        print(f"❌ 成本追踪测试失败: {e}")
        return False

def test_database():
    """测试数据库连接"""
    print("\n5️⃣ 测试数据库连接...")
    try:
        # 尝试提交一个测试任务
        data = {
            'prompt': '测试：简单介绍一下人工智能'
        }
        response = requests.post(f"{BASE_URL}/generate_report", json=data)
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            print(f"✅ 数据库连接成功")
            print(f"   任务 ID: {task_id}")
            return True, task_id
        else:
            print(f"❌ 数据库测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ 数据库测试异常: {e}")
        return False, None

def test_api_keys():
    """测试 API Keys 配置"""
    print("\n6️⃣ 测试 API Keys...")
    
    keys = {
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'TAVILY_API_KEY': os.getenv('TAVILY_API_KEY'),
        'DATABASE_URL': os.getenv('DATABASE_URL')
    }
    
    all_ok = True
    for key, value in keys.items():
        if value and not value.startswith('your-') and not value.startswith('sk-your'):
            print(f"   ✅ {key}: {value[:20]}...")
        else:
            print(f"   ❌ {key}: 未配置或使用占位符")
            all_ok = False
    
    if all_ok:
        print("✅ 所有 API Keys 已配置")
    else:
        print("⚠️  部分 API Keys 未配置")
    
    return all_ok

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Phase 1 完整系统测试")
    print("=" * 60)
    print()
    
    results = []
    
    # 运行所有测试
    results.append(("首页访问", test_homepage()))
    results.append(("健康检查", test_health_check()))
    results.append(("配置验证", test_config()))
    results.append(("成本追踪", test_cost_tracker()))
    results.append(("API Keys", test_api_keys()))
    
    db_result, task_id = test_database()
    results.append(("数据库连接", db_result))
    
    # 打印测试摘要
    print()
    print("=" * 60)
    print("📊 测试摘要")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s} {status}")
    
    print()
    print(f"总计: {passed}/{total} 测试通过 ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常！")
        print("\n📝 下一步:")
        print("   1. 访问 http://localhost:8000 查看 Web 界面")
        print("   2. 提交一个研究任务测试完整流程")
        print("   3. 查看成本追踪日志")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查配置")
    
    return passed == total

if __name__ == "__main__":
    exit(0 if main() else 1)
