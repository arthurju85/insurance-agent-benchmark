#!/usr/bin/env python3
"""
评测系统测试脚本
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.agent import AgentConfig, AgentType
from src.db.question_repo import get_repository
from src.pipeline.evaluator import evaluate_agent


async def test_repository():
    """测试题库加载"""
    print("=" * 50)
    print("测试题库加载")
    print("=" * 50)

    repo = get_repository()
    stats = repo.get_statistics()

    print(f"题库统计: {stats}")
    print(f"总题目数: {stats.get('total_questions', 0)}")
    print(f"维度分布: {stats.get('by_dimension', {})}")

    # 按维度获取题目
    for dimension in stats.get('by_dimension', {}).keys():
        questions = repo.get_questions_by_dimension(dimension)
        print(f"\n{dimension} 维度题目数: {len(questions)}")
        if questions:
            print(f"  示例: {questions[0].question_id} - {questions[0].title}")

    return stats.get('total_questions', 0) > 0


async def test_evaluator_single():
    """测试单题评分"""
    print("\n" + "=" * 50)
    print("测试评分引擎")
    print("=" * 50)

    from src.models.question import Question, ValidationRule
    from src.evaluators.factory import EvaluatorFactory

    # 创建一个测试题目
    question = Question(
        question_id="TEST-001",
        dimension="knowledge",
        question_type="case_analysis",
        title="测试题",
        content="测试内容",
        validation_rules=ValidationRule(
            must_contain_keywords=["正确"],
            prohibited_keywords=["错误"]
        ),
        score=100
    )

    # 测试正确回答
    result_correct = EvaluatorFactory.evaluate_question(
        question=question,
        agent_output="这是正确的回答",
        parsed_output=None
    )
    print(f"正确回答评分: {result_correct['score']:.1f}")
    print(f"是否通过: {result_correct['passed']}")

    # 测试错误回答
    result_wrong = EvaluatorFactory.evaluate_question(
        question=question,
        agent_output="这是错误的回答",
        parsed_output=None
    )
    print(f"错误回答评分: {result_wrong['score']:.1f}")
    print(f"是否通过: {result_wrong['passed']}")

    return True


async def test_full_evaluation():
    """测试完整评测流程（需要配置真实的Agent）"""
    print("\n" + "=" * 50)
    print("测试完整评测流程")
    print("=" * 50)

    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未设置 OPENAI_API_KEY，跳过完整评测测试")
        print("如需测试，请设置: export OPENAI_API_KEY=your_key")
        return True

    # 创建Agent配置
    agent_config = AgentConfig(
        id="test-gpt4",
        name="GPT-4 Test Agent",
        vendor="OpenAI",
        agent_type=AgentType.OPENAI_API,
        base_url="https://api.openai.com/v1",
        api_key=api_key,
        model="gpt-4",
        temperature=0.3
    )

    # 获取题目
    repo = get_repository()
    questions = repo.get_questions_by_dimension("knowledge")[:2]  # 只测试2题

    if not questions:
        print("错误: 未找到题目")
        return False

    print(f"开始评测 {len(questions)} 道题目...")

    # 执行评测
    result = await evaluate_agent(agent_config, questions, concurrency=1)

    print(f"\n评测完成!")
    print(f"评测ID: {result.evaluation_id}")
    print(f"总得分: {result.total_score:.1f}/{result.max_total_score}")
    print(f"得分率: {result.overall_percentage:.1f}%")
    print(f"平均响应时间: {result.avg_latency_ms:.0f}ms")

    # 各维度得分
    print("\n各维度得分:")
    for dim_score in result.dimension_scores:
        print(f"  {dim_score.dimension}: {dim_score.score:.1f}/{dim_score.max_score}")

    return True


async def main():
    """主函数"""
    print("保险智能体评测系统 - 测试脚本")
    print("=" * 50)

    tests = [
        ("题库加载", test_repository),
        ("评分引擎", test_evaluator_single),
        ("完整评测", test_full_evaluation),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n错误: {e}")
            results.append((name, False))

    # 打印总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    for name, success in results:
        status = "通过" if success else "失败"
        print(f"  {name}: {status}")

    all_passed = all(success for _, success in results)
    print(f"\n总体结果: {'全部通过' if all_passed else '存在失败'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
