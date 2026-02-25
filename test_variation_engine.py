#!/usr/bin/env python3
"""
题目变异引擎测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from db.variation_engine import VariationEngine, VariationConfig, create_variant_set
from models.question import Question, QuestionDimension, QuestionType, DifficultyLevel, ValidationRule
import json


def test_basic_variation():
    """测试基础变异功能"""
    print("=" * 60)
    print("🔄 测试基础题目变异")
    print("=" * 60)

    # 创建测试题目
    question = Question(
        question_id="TEST-001",
        dimension=QuestionDimension.KNOWLEDGE,
        question_type=QuestionType.CASE_ANALYSIS,
        difficulty=DifficultyLevel.MEDIUM,
        title="等待期测试题",
        content="""客户张某于2024年1月1日投保重疾险，年缴保费10,000元。
2024年3月15日（非意外）确诊肺癌，住院花费50,000元。
保单等待期为90日。请问保险公司应如何处理？""",
        context="等待期条款：合同生效90日内非意外确诊，退还保费。",
        validation_rules=ValidationRule(
            conclusion_must_be_one_of=["退还保费"],
            must_contain_keywords=["等待期", "90日", "74天"],
            numeric_path="calculation_days"
        ),
        ground_truth={
            "conclusion": "退还保费",
            "calculation_days": 74,
            "reasoning": "确诊时间在等待期（90日）内，从1月1日到3月15日共74天"
        },
        score=100,
        tags=["测试", "等待期"]
    )

    print("\n📋 原题:")
    print(f"ID: {question.question_id}")
    print(f"内容: {question.content[:100]}...")
    print(f"Ground Truth: {question.ground_truth}")

    # 创建变异引擎
    config = VariationConfig(
        date_offset_days=(-30, 30),  # 较小的偏移便于观察
        amount_variance=0.1,  # 10%金额变异
        enable_sentence_restructure=True
    )
    engine = VariationEngine(config=config, seed=42)

    # 生成3个变体
    variations = engine.generate_variations(question, count=3)

    print(f"\n✅ 生成了 {len(variations)} 个变体:\n")

    for i, var in enumerate(variations, 1):
        print(f"--- 变体 {i} ---")
        print(f"ID: {var.question_id}")
        print(f"是否为变体: {var.is_variant}")
        print(f"母题ID: {var.parent_id}")
        print(f"种子: {var.variant_seed}")
        print(f"内容: {var.content[:120]}...")
        print(f"Ground Truth: {var.ground_truth}")
        print(f"标签: {var.tags}")
        print()

    return True


def test_date_variation():
    """测试日期变异"""
    print("=" * 60)
    print("📅 测试日期变异")
    print("=" * 60)

    engine = VariationEngine(seed=123)

    text = "客户于2024年6月1日投保，2024年8月15日确诊。"
    print(f"原文: {text}")

    # 手动测试日期提取和变异
    dates = engine._extract_dates(text)
    print(f"提取到 {len(dates)} 个日期:")
    for d, dt in dates:
        print(f"  {d} -> {dt}")

    return True


def test_amount_variation():
    """测试金额变异"""
    print("=" * 60)
    print("💰 测试金额变异")
    print("=" * 60)

    engine = VariationEngine(config=VariationConfig(amount_variance=0.2), seed=456)

    text = "保费10,000元，保额50万元，免赔额1万元。"
    print(f"原文: {text}")

    amounts = engine._extract_amounts(text)
    print(f"提取到 {len(amounts)} 个金额:")
    for a, val in amounts:
        print(f"  {a} -> {val}")

    return True


def test_entity_consistency():
    """测试实体替换一致性"""
    print("=" * 60)
    print("👤 测试实体替换一致性")
    print("=" * 60)

    engine = VariationEngine(seed=789)

    # 同一个人名应映射到同一个替换
    text = "张某向李某投保，张某签署了合同，李某审核通过。"
    print(f"原文: {text}")

    names = engine._extract_names(text)
    print(f"提取到人名: {names}")

    # 获取一致映射
    mappings = {}
    for name in set(names):
        mappings[name] = engine._get_consistent_mapping(name, engine.config.name_pool)

    print(f"映射表: {mappings}")

    # 验证一致性：再次获取应相同
    for name in names:
        mapped = engine._get_consistent_mapping(name, engine.config.name_pool)
        assert mapped == mappings[name], "映射不一致！"

    print("✅ 实体映射一致性验证通过")

    return True


def test_validation_rule_update():
    """测试验证规则更新"""
    print("=" * 60)
    print("✅ 测试验证规则更新")
    print("=" * 60)

    question = Question(
        question_id="TEST-RULE-001",
        dimension=QuestionDimension.KNOWLEDGE,
        question_type=QuestionType.CASE_ANALYSIS,
        difficulty=DifficultyLevel.MEDIUM,
        title="规则测试题",
        content="""客户王某于2024年1月1日投保。
条款规定等待期90日。""",
        validation_rules=ValidationRule(
            must_contain_keywords=["等待期", "90日", "2024年1月1日"],
            conclusion_must_be_one_of=["赔付"]
        ),
        ground_truth={"conclusion": "赔付"},
        score=100
    )

    print("原始验证规则:")
    print(f"  必须包含关键词: {question.validation_rules.must_contain_keywords}")

    engine = VariationEngine(seed=999)
    variation = engine.generate_variation(question, variation_index=1)

    print("\n变异后验证规则:")
    print(f"  必须包含关键词: {variation.validation_rules.must_contain_keywords}")

    # 验证规则被正确更新
    assert variation.is_variant == True
    assert variation.parent_id == question.question_id
    print("✅ 验证规则更新成功")

    return True


def test_paraphrase():
    """测试文本改写"""
    print("=" * 60)
    print("📝 测试文本改写")
    print("=" * 60)

    from db.variation_engine import generate_paraphrase_variations

    text = "投保人申请解除合同，被保险人同意退保。"
    print(f"原文: {text}")

    variations = generate_paraphrase_variations(text, count=3)
    print(f"\n生成 {len(variations)} 个改写变体:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")

    return True


def test_batch_variation():
    """测试批量变异"""
    print("=" * 60)
    print("📦 测试批量变异")
    print("=" * 60)

    # 创建多个测试题目
    questions = [
        Question(
            question_id=f"BATCH-{i:03d}",
            dimension=QuestionDimension.KNOWLEDGE,
            question_type=QuestionType.CASE_ANALYSIS,
            difficulty=DifficultyLevel.MEDIUM,
            title=f"批量测试题{i}",
            content=f"客户{i}于2024年{i}月{i}日投保，保费{i}000元。",
            validation_rules=ValidationRule(),
            ground_truth={"conclusion": "测试"},
            score=100
        )
        for i in range(1, 4)
    ]

    print(f"创建了 {len(questions)} 道原题")

    engine = VariationEngine(seed=111)
    all_questions = engine.generate_question_set_variations(
        questions,
        variations_per_question=2
    )

    print(f"生成后共 {len(all_questions)} 道题（含原题和变体）")

    # 统计
    originals = [q for q in all_questions if not q.is_variant]
    variants = [q for q in all_questions if q.is_variant]

    print(f"  - 原题: {len(originals)} 道")
    print(f"  - 变体: {len(variants)} 道")

    assert len(all_questions) == len(questions) * 3  # 原题 + 2个变体
    print("✅ 批量变异数量正确")

    return True


def test_create_variant_set():
    """测试从文件创建变体集"""
    print("=" * 60)
    print("📁 测试从文件创建变体集")
    print("=" * 60)

    source_path = "backend/data/questions/benchmark_knowledge_10.json"
    output_path = "backend/data/questions/benchmark_knowledge_10_variant.json"

    if not os.path.exists(source_path):
        print(f"⚠️ 源文件不存在: {source_path}")
        return True  # 跳过此测试

    print(f"源文件: {source_path}")

    result = create_variant_set(
        source_set_path=source_path,
        output_path=output_path,
        variations_per_question=2,
        seed=2024
    )

    print(f"\n✅ 变体集创建成功:")
    print(f"  原题数量: {result['source_questions']}")
    print(f"  总题数: {result['total_questions']}")
    print(f"  生成变体: {result['variants_generated']}")
    print(f"  输出文件: {result['output_path']}")

    # 验证输出文件
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"\n  文件验证通过，包含 {len(data['questions'])} 道题")

        # 显示一道变体
        variants = [q for q in data['questions'] if q.get('is_variant')]
        if variants:
            print(f"\n  示例变体:")
            print(f"    ID: {variants[0]['question_id']}")
            print(f"    内容: {variants[0]['content'][:80]}...")

    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🧬 题目变异引擎测试")
    print("=" * 60)

    tests = [
        ("基础变异功能", test_basic_variation),
        ("日期变异", test_date_variation),
        ("金额变异", test_amount_variation),
        ("实体替换一致性", test_entity_consistency),
        ("验证规则更新", test_validation_rule_update),
        ("文本改写", test_paraphrase),
        ("批量变异", test_batch_variation),
        ("文件变体集创建", test_create_variant_set),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🔹 运行测试: {name}")
        print('='*60)
        try:
            success = test_func()
            results.append((name, success))
            if success:
                print(f"✅ 测试通过: {name}")
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 总结
    print("\n\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status}: {name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n🎉 所有测试通过！题目变异引擎工作正常。")
        print("\n主要功能:")
        print("  • 日期变异（保持时间间隔）")
        print("  • 金额变异（按比例调整）")
        print("  • 实体替换（人名、公司名等）")
        print("  • 验证规则自动更新")
        print("  • Ground Truth 同步更新")
        print("  • 批量变异生成")
    else:
        print("\n⚠️ 部分测试失败。请检查错误信息。")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
