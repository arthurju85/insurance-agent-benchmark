#!/usr/bin/env python3
"""
前后端联调测试
"""

import sys
sys.path.insert(0, 'backend/src')

import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time


def test_api_connectivity():
    """测试API连通性"""
    print("=" * 50)
    print("🔗 测试前后端连通性")
    print("=" * 50)

    try:
        import requests

        # 测试健康检查
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端API正常")
            print(f"   状态: {data['status']}")
            print(f"   题库数量: {data['questions_loaded']}")
            return True
        else:
            print(f"❌ 后端API异常: HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端API")
        print("   请确保后端服务已启动: python backend/run.py")
        return False
    except ImportError:
        print("⚠️  需要安装requests: pip install requests")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_leaderboard_api():
    """测试排行榜API"""
    print("\n" + "=" * 50)
    print("📊 测试排行榜API")
    print("=" * 50)

    try:
        import requests

        response = requests.get("http://localhost:8000/api/v1/leaderboard/current", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 排行榜API正常")
            print(f"   榜单名称: {data.get('name', 'N/A')}")
            print(f"   Agent数量: {data.get('total_agents', 0)}")
            if data.get('entries'):
                print(f"   第一名: {data['entries'][0]['agent_name']}")
            return True
        else:
            print(f"❌ 排行榜API异常: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_questions_api():
    """测试题库API"""
    print("\n" + "=" * 50)
    print("📝 测试题库API")
    print("=" * 50)

    try:
        import requests

        # 测试统计
        response = requests.get("http://localhost:8000/api/v1/questions/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 题库统计API正常")
            print(f"   总题目数: {data.get('total_questions', 0)}")
            print(f"   维度分布: {list(data.get('by_dimension', {}).keys())}")
        else:
            print(f"❌ 题库统计API异常")

        # 测试题目列表
        response = requests.get("http://localhost:8000/api/v1/questions/?limit=3", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 题目列表API正常")
            print(f"   返回题目数: {len(data)}")
            if data:
                print(f"   示例: {data[0]['title']}")
            return True
        else:
            print(f"❌ 题目列表API异常")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_arena_api():
    """测试竞技场API"""
    print("\n" + "=" * 50)
    print("🏆 测试竞技场API")
    print("=" * 50)

    try:
        import requests

        response = requests.get("http://localhost:8000/api/v1/arena/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 竞技场API正常")
            print(f"   状态: {data.get('status', 'N/A')}")
            print(f"   Agent数: {data.get('agents', 0)}")
            return True
        else:
            print(f"❌ 竞技场API异常: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("🧪 前后端联调测试")
    print("=" * 50)
    print("\n前置条件:")
    print("  1. 后端API已启动: python backend/run.py")
    print("  2. 前端已构建: npm run build (如需测试前端)")

    tests = [
        ("API连通性", test_api_connectivity),
        ("排行榜API", test_leaderboard_api),
        ("题库API", test_questions_api),
        ("竞技场API", test_arena_api),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n🔹 测试: {name}")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((name, False))

    # 总结
    print("\n\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status}: {name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n🎉 所有测试通过！前后端连通正常。")
        print("\n下一步:")
        print("  - 启动前端: npm run dev")
        print("  - 访问: http://localhost:3000")
    else:
        print("\n⚠️  部分测试失败。请检查:")
        print("  1. 后端服务是否已启动")
        print("  2. 端口是否被占用")
        print("  3. 网络连接是否正常")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
