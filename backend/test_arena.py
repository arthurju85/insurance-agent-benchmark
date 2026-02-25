#!/usr/bin/env python3
"""
竞技场系统测试脚本
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from src.models.agent import AgentConfig, AgentType
from src.arena.orchestrator import ArenaOrchestrator, ArenaConfig
from src.arena.customer_simulator import generate_random_customer, CustomerTag


def test_customer_simulator():
    """测试虚拟客户生成器"""
    print("=" * 50)
    print("🧪 测试虚拟客户生成器")
    print("=" * 50)

    # 生成随机客户
    print("\n1. 随机客户生成：")
    for i in range(3):
        customer = generate_random_customer(f"TEST_{i}")
        print(f"\n  客户{i+1}: {customer.persona.label}")
        print(f"    标签: {customer.persona.tag.value}")
        print(f"    年龄: {customer.persona.age}, 收入: {customer.persona.income}")
        print(f"    开场白: {customer.get_opening_message()[:50]}...")

    # 按标签获取客户
    print("\n2. 按标签获取客户：")
    customer = generate_random_customer("TEST_TAG")
    print(f"  标签 {customer.persona.tag.value}: {customer.persona.label}")

    # 测试对话
    print("\n3. 模拟对话：")
    customer = generate_random_customer("TEST_CONV")
    print(f"  客户: {customer.persona.label}")

    messages = [
        "您好，请问有什么可以帮您？",
        "这款产品的年保费是5000元",
        "保障范围包括重疾和医疗"
    ]

    for msg in messages:
        response = customer.respond_to_agent(msg)
        print(f"\n  Agent: {msg}")
        print(f"  客户: {response}")

    return True


def test_purchase_decision():
    """测试购买决策"""
    print("\n" + "=" * 50)
    print("🧪 测试购买决策")
    print("=" * 50)

    test_cases = [
        ("高信任度", 0.8),
        ("中信任度", 0.5),
        ("低信任度", 0.2)
    ]

    for name, trust in test_cases:
        customer = generate_random_customer(f"DECISION_{name}")
        customer.trust_score = trust

        # 多次决策看概率分布
        results = {"purchase": 0, "reject": 0}
        for _ in range(10):
            decision = customer.make_purchase_decision({"premium": 10000})
            results[decision["decision"]] += 1

        print(f"\n  {name} (信任度={trust}):")
        print(f"    成交: {results['purchase']}/10")
        print(f"    流失: {results['reject']}/10")

    return True


async def test_arena_orchestrator():
    """测试竞技调度器"""
    print("\n" + "=" * 50)
    print("🧪 测试竞技调度器")
    print("=" * 50)

    # 创建模拟Agent配置
    agents = [
        AgentConfig(
            id="agent_1",
            name="Agent-A",
            vendor="Test",
            agent_type=AgentType.OPENAI_API,
            base_url="http://test",
            api_key="test",
            model="gpt-4"
        ),
        AgentConfig(
            id="agent_2",
            name="Agent-B",
            vendor="Test",
            agent_type=AgentType.OPENAI_API,
            base_url="http://test",
            api_key="test",
            model="gpt-4"
        ),
        AgentConfig(
            id="agent_3",
            name="Agent-C",
            vendor="Test",
            agent_type=AgentType.OPENAI_API,
            base_url="http://test",
            api_key="test",
            model="gpt-4"
        )
    ]

    # 配置（短时长用于测试）
    config = ArenaConfig(
        session_duration_hours=0.05,  # 3分钟
        customer_generation_interval=(5, 10),  # 5-10秒生成一个
        max_concurrent_customers=5
    )

    orchestrator = ArenaOrchestrator(agents, config)

    # 注册事件回调
    def on_event(event):
        print(f"  📡 事件: {event.event_type} - {event.data.get('customer_id', 'N/A')}")

    orchestrator.add_event_callback(on_event)

    print("\n1. 启动竞技场（3分钟）...")
    await orchestrator.start()

    print("\n2. 等待竞技场运行...")
    while orchestrator.status.value == "running":
        state = orchestrator.get_current_state()
        print(f"\r  状态: {state['status']} | "
              f"客户: {state['total_customers']} | "
              f"服务中: {state['serving_customers']}",
              end="", flush=True)
        await asyncio.sleep(2)

    print("\n\n3. 最终结果：")
    leaderboard = orchestrator.get_leaderboard()

    print("\n  🏆 排行榜：")
    for entry in leaderboard:
        print(f"\n    {entry['rank']}. {entry['agent_name']}")
        print(f"       GMV: ¥{entry['total_gmv']:,.0f}")
        print(f"       成交: {entry['deal_count']}单")
        print(f"       转化率: {entry['conversion_rate']}%")
        print(f"       综合得分: {entry['composite_score']}")

    return True


async def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("🏆 竞技场系统测试")
    print("=" * 50)

    tests = [
        ("客户生成器", test_customer_simulator),
        ("购买决策", test_purchase_decision),
        ("竞技调度器", test_arena_orchestrator),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n\n🔹 运行测试: {name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                success = await test_func()
            else:
                success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
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
    print(f"\n总体结果: {'全部通过' if all_passed else '存在失败'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
