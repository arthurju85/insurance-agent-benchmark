#!/usr/bin/env python3
"""
数据持久化测试脚本
测试数据库的读写功能
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from db.database import Database
from datetime import datetime


def test_database_init():
    """测试数据库初始化"""
    print("=" * 50)
    print("🗄️ 测试数据库初始化")
    print("=" * 50)

    # 创建内存数据库用于测试
    db = Database(":memory:")

    print("✅ 数据库初始化成功")

    # 验证表是否创建
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]

        expected_tables = [
            'evaluations', 'evaluation_details', 'leaderboard_history',
            'arena_sessions', 'arena_events', 'registered_agents'
        ]

        for table in expected_tables:
            if table in tables:
                print(f"   ✅ 表 {table} 已创建")
            else:
                print(f"   ❌ 表 {table} 缺失")

    return True


def test_save_evaluation(db):
    """测试保存评测结果"""
    print("\n" + "=" * 50)
    print("💾 测试保存评测结果")
    print("=" * 50)

    # 模拟评测结果
    evaluation = {
        "evaluation_id": "eval_20260115_001",
        "agent_id": "test-agent-1",
        "agent_name": "Test Agent",
        "agent_vendor": "Test Corp",
        "agent_version": "v1.0",
        "question_set_id": "benchmark_v1",
        "status": "completed",
        "total_score": 850.0,
        "max_total_score": 1000.0,
        "overall_percentage": 85.0,
        "total_questions": 10,
        "completed_questions": 10,
        "failed_questions": 0,
        "timeout_questions": 0,
        "total_latency_ms": 5000.0,
        "avg_latency_ms": 500.0,
        "tags": ["test", "benchmark"],
        "question_results": [
            {
                "question_id": "Q001",
                "dimension": "knowledge",
                "score": 90.0,
                "max_score": 100.0,
                "status": "completed",
                "latency_ms": 450.0,
                "agent_output": "test output",
                "validation_results": [{"rule_type": "keyword", "passed": True, "score": 100.0}]
            }
        ]
    }

    # 保存
    eval_id = db.save_evaluation(evaluation)
    print(f"✅ 评测结果已保存: {eval_id}")

    # 读取
    retrieved = db.get_evaluation(eval_id)
    if retrieved:
        print(f"✅ 评测结果已读取")
        print(f"   Agent: {retrieved['agent_name']}")
        print(f"   得分: {retrieved['total_score']}/{retrieved['max_total_score']}")
        print(f"   百分比: {retrieved['overall_percentage']}%")
    else:
        print("❌ 无法读取评测结果")
        return False

    return True


def test_leaderboard_operations():
    """测试排行榜操作"""
    print("\n" + "=" * 50)
    print("🏆 测试排行榜操作")
    print("=" * 50)

    db = Database(":memory:")

    # 保存排行榜
    leaderboard = {
        "leaderboard_id": "lb_2026_01",
        "name": "2026年1月排行榜",
        "evaluation_date": "2026-01",
        "question_set_id": "benchmark_v1",
        "entries": [
            {
                "agent_id": "agent-1",
                "agent_name": "Agent One",
                "vendor": "Vendor A",
                "version": "v1.0",
                "agent_type": "insurer",
                "rank": 1,
                "overall_score": 920.0,
                "overall_percentage": 92.0,
                "knowledge_score": 95.0,
                "understanding_score": 90.0,
                "reasoning_score": 88.0,
                "compliance_score": 94.0,
                "tools_score": 91.0,
                "change": 2.5
            },
            {
                "agent_id": "agent-2",
                "agent_name": "Agent Two",
                "vendor": "Vendor B",
                "version": "v2.0",
                "agent_type": "tech",
                "rank": 2,
                "overall_score": 880.0,
                "overall_percentage": 88.0,
                "knowledge_score": 85.0,
                "understanding_score": 90.0,
                "reasoning_score": 87.0,
                "compliance_score": 92.0,
                "tools_score": 89.0,
                "change": -1.0
            }
        ]
    }

    db.save_leaderboard(leaderboard)
    print("✅ 排行榜已保存")

    # 读取
    retrieved = db.get_leaderboard("2026-01")
    if retrieved:
        print(f"✅ 排行榜已读取: {retrieved['name']}")
        print(f"   条目数: {len(retrieved['entries'])}")
        print(f"   第一名: {retrieved['entries'][0]['agent_name']}")
    else:
        print("❌ 无法读取排行榜")
        return False

    # 最新排行榜
    latest = db.get_latest_leaderboard()
    if latest:
        print(f"✅ 最新排行榜: {latest['evaluation_date']}")

    return True


def test_agent_registration():
    """测试Agent注册"""
    print("\n" + "=" * 50)
    print("🤖 测试Agent注册")
    print("=" * 50)

    db = Database(":memory:")

    # 注册Agent
    agent_config = {
        "id": "test-agent-001",
        "name": "Test Insurance Agent",
        "vendor": "Test Corp",
        "version": "v1.0.0",
        "agent_type": "openai_api",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4",
        "system_prompt": "You are an insurance expert..."
    }

    agent_id = db.register_agent(agent_config)
    print(f"✅ Agent已注册: {agent_id}")

    # 列出Agent
    agents = db.get_registered_agents(active_only=True)
    print(f"✅ 已注册Agent数: {len(agents)}")

    if agents:
        print(f"   名称: {agents[0]['name']}")
        print(f"   厂商: {agents[0]['vendor']}")
        print(f"   模型: {agents[0]['model']}")

    return True


def test_arena_operations():
    """测试竞技场操作"""
    print("\n" + "=" * 50)
    print("🏟️ 测试竞技场操作")
    print("=" * 50)

    db = Database(":memory:")

    # 创建会话
    session_id = db.create_arena_session(
        "arena_test_001",
        "测试竞技场",
        {"duration": 60, "max_agents": 5}
    )
    print(f"✅ 竞技场会话已创建: {session_id}")

    # 保存事件
    db.save_arena_event(session_id, "customer_generated", {"customer_id": "C001"})
    db.save_arena_event(session_id, "deal_closed", {"agent_id": "A001", "amount": 10000})
    print("✅ 竞技场事件已保存")

    # 读取事件
    events = db.get_arena_events(session_id)
    print(f"✅ 事件数: {len(events)}")

    # 结束会话
    db.finish_arena_session(session_id, {"winner": "A001"})
    print("✅ 竞技场会话已结束")

    return True


def test_statistics():
    """测试统计功能"""
    print("\n" + "=" * 50)
    print("📊 测试统计功能")
    print("=" * 50)

    db = Database(":memory:")

    # 添加一些数据
    db.register_agent({
        "id": "agent-1",
        "name": "Agent 1",
        "vendor": "Vendor A",
        "agent_type": "openai_api",
        "model": "gpt-4"
    })

    db.save_evaluation({
        "evaluation_id": "eval_001",
        "agent_id": "agent-1",
        "agent_name": "Agent 1",
        "question_set_id": "test",
        "status": "completed",
        "total_score": 800,
        "max_total_score": 1000,
        "overall_percentage": 80.0,
        "question_results": []
    })

    # 获取统计
    stats = db.get_statistics()
    print("✅ 系统统计:")
    print(f"   总评测数: {stats['total_evaluations']}")
    print(f"   总Agent数: {stats['total_agents']}")
    print(f"   排行榜数: {stats['total_leaderboards']}")
    print(f"   近7天评测: {stats['recent_evaluations']}")

    return True


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("🗄️ 数据持久化测试")
    print("=" * 50)

    tests = [
        ("数据库初始化", test_database_init),
        ("评测结果保存", test_save_evaluation),
        ("排行榜操作", test_leaderboard_operations),
        ("Agent注册", test_agent_registration),
        ("竞技场操作", test_arena_operations),
        ("统计功能", test_statistics),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n🔹 运行测试: {name}")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
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
        print("\n🎉 所有测试通过！数据持久化模块工作正常。")
        print("\n数据库文件位置:")
        print("  backend/data/insurance_benchmark.db")
    else:
        print("\n⚠️ 部分测试失败。请检查错误信息。")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
