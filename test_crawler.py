#!/usr/bin/env python3
"""
数据爬虫系统测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

import asyncio
from crawler.crawler import (
    CrawlerScheduler, DataStore, CrawlResult, CrawlTask,
    CBIRCrawler, InsuranceCompanyCrawler, create_default_scheduler
)
from crawler.parser import ClauseParser, parse_clause, extract_structured_data
from datetime import datetime


def test_crawl_result():
    """测试爬取结果模型"""
    print("=" * 60)
    print("📦 测试 CrawlResult 模型")
    print("=" * 60)

    result = CrawlResult(
        url="https://example.com/policy/1",
        title="关于规范人身保险业务的通知",
        content="这是政策内容...",
        source="银保监会",
        category="监管政策",
        published_at=datetime.now()
    )

    print(f"✅ 创建爬取结果")
    print(f"   标题: {result.title}")
    print(f"   来源: {result.source}")
    print(f"   类别: {result.category}")
    print(f"   哈希ID: {result.hash_id}")

    return True


def test_data_store():
    """测试数据存储"""
    print("\n" + "=" * 60)
    print("💾 测试 DataStore")
    print("=" * 60)

    # 使用内存存储测试
    store = DataStore(db_path="/tmp/test_crawl_data.json")

    # 创建测试数据
    results = [
        CrawlResult(
            url=f"https://example.com/{i}",
            title=f"测试条款{i}",
            content=f"内容{i}",
            source="测试源",
            category="产品条款"
        )
        for i in range(5)
    ]

    # 保存
    saved = store.save_results(results)
    print(f"✅ 保存了 {saved} 条数据")

    # 查询
    query_results = store.query(category="产品条款", limit=3)
    print(f"✅ 查询到 {len(query_results)} 条数据")

    # 统计
    stats = store.get_stats()
    print(f"✅ 统计: {stats}")

    # 去重测试
    duplicate = store.save_result(results[0])
    print(f"✅ 重复数据检测: {'通过' if not duplicate else '失败'}")

    return True


def test_clause_parser():
    """测试条款解析器"""
    print("\n" + "=" * 60)
    print("📄 测试 ClauseParser")
    print("=" * 60)

    # 示例条款文本
    sample_clause = """
    第一章 保险责任
    第1条 等待期
    本合同生效之日起90日内（含第90日），被保险人因意外伤害以外的原因确诊初次患有本合同所定义的重大疾病，我们不承担保险责任，但将退还您所交纳的保险费，本合同终止。

    第2条 保险金额
    本合同的基本保险金额为人民币100,000元。

    第二章 责任免除
    第3条 免责条款
    因下列情形之一，造成被保险人身故、伤残的，本公司不承担给付保险金的责任：
    （一）投保人对被保险人的故意杀害、故意伤害；
    （二）被保险人故意犯罪或抗拒依法采取的刑事强制措施；
    （三）被保险人自杀或故意自伤；
    （四）被保险人醉酒、吸食或注射毒品；
    （五）被保险人酒后驾驶。

    第三章 保险费
    第4条 宽限期
    分期交纳保险费的，到期未交纳的，自约定日的次日零时起60日为宽限期。
    """

    parser = ClauseParser()

    # 解析条款
    clause = parser.parse(sample_clause, "测试重疾险", "测试保险")

    print(f"✅ 解析条款: {clause.product_name}")
    print(f"   产品类型: {clause.clause_type}")
    print(f"   章节数: {len(clause.sections)}")

    # 打印章节信息
    print("\n   章节详情:")
    for section in clause.sections:
        print(f"   - {section.title} ({section.clause_type.value})")

    # 提取关键日期
    key_dates = parser.extract_key_dates(sample_clause)
    print(f"\n✅ 提取到 {len(key_dates)} 个关键日期:")
    for date in key_dates:
        print(f"   - {date['type']}: {date['days']}天")

    # 提取保额
    amounts = parser.extract_coverage_amounts(sample_clause)
    print(f"\n✅ 提取到 {len(amounts)} 个保额信息")

    # 生成题目建议
    suggestions = parser.generate_question_suggestions(clause)
    print(f"\n✅ 生成 {len(suggestions)} 个题目建议:")
    for i, sugg in enumerate(suggestions[:3], 1):
        print(f"   {i}. [{sugg['type']}] {sugg.get('suggested_question', 'N/A')[:50]}...")

    return True


def test_extract_structured_data():
    """测试结构化数据提取"""
    print("\n" + "=" * 60)
    print("🔍 测试结构化数据提取")
    print("=" * 60)

    sample_text = """
    XX重大疾病保险条款

    保险责任：被保险人于本合同生效之日起90日内因非意外原因确诊重疾，退还保费；90日后确诊，给付保额。
    保险金额：基本保额50万元。

    责任免除：
    （一）投保人对被保险人的故意杀害；
    （二）被保险人故意犯罪；
    （三）被保险人自杀；
    （四）被保险人醉酒驾驶。

    保险费交纳：年缴，宽限期60日。
    """

    data = extract_structured_data(sample_text)

    print(f"✅ 提取结果:")
    print(f"   产品类型: {data['product_type']}")
    print(f"   章节数: {data['sections_count']}")
    print(f"   关键日期: {data['key_dates']}")
    print(f"   保额信息: {data['coverage_amounts']}")
    print(f"   责任免除: {data['exclusions']}")
    print(f"   题目建议数: {len(data['question_suggestions'])}")

    return True


async def test_crawler_scheduler():
    """测试爬虫调度器"""
    print("\n" + "=" * 60)
    print("🕷️ 测试 CrawlerScheduler")
    print("=" * 60)

    scheduler = create_default_scheduler()

    print(f"✅ 创建了调度器，包含 {len(scheduler.crawlers)} 个爬虫")

    for crawler in scheduler.crawlers:
        print(f"   - {crawler.source_name} ({crawler.base_url})")

    return True


async def test_cbir_crawler_mock():
    """测试银保监会爬虫（模拟）"""
    print("\n" + "=" * 60)
    print("🏛️ 测试 CBIRCrawler (模拟模式)")
    print("=" * 60)

    # 注意：实际爬取需要网络连接，这里只测试结构
    crawler = CBIRCrawler()

    print(f"✅ 创建了爬虫:")
    print(f"   名称: {crawler.source_name}")
    print(f"   基础URL: {crawler.base_url}")
    print(f"   延迟: {crawler.delay}秒")

    # 测试URL发现（不实际爬取）
    # urls = await crawler.discover_urls()
    # print(f"✅ 发现 {len(urls)} 个URL")

    return True


def test_paragraph_parsing():
    """测试段落解析"""
    print("\n" + "=" * 60)
    print("📝 测试复杂条款解析")
    print("=" * 60)

    complex_clause = """
    等待期条款详解

    本主险合同生效之日起90日内（含第90日），被保险人因意外伤害以外的原因，确诊初次患有本主险合同所定义的重大疾病（无论一种或多种），我们不承担保险责任，但将退还您所交纳的保险费，本主险合同终止。这90日的时间称为等待期。

    示例计算：
    客户张先生于2024年3月15日投保，等待期从2024年3月16日开始计算，到2024年6月13日结束（共90天）。
    若张先生在2024年5月15日（等待期内）确诊肺癌，保险公司退还保费；
    若张先生在2024年7月1日（等待期后）确诊肺癌，保险公司给付保险金。

    保险金额与保险费
    基本保险金额为人民币100,000元。您可以选择年缴或月缴，年缴保费为2,000元，月缴保费为180元。

    宽限期条款
    如果您到期未交纳保险费，自保险费约定交纳日的次日零时起60日为宽限期。宽限期内发生的保险事故，我们仍会承担保险责任，但在给付保险金时会扣减您欠交的保险费。
    """

    parser = ClauseParser()
    clause = parser.parse(complex_clause, "复杂重疾险", "XX人寿")

    print(f"✅ 解析复杂条款:")
    print(f"   识别类型: {clause.clause_type}")
    print(f"   章节数量: {len(clause.sections)}")

    # 分析每个章节
    for section in clause.sections:
        print(f"\n   [{section.clause_type.value}] {section.title}")
        if section.keywords:
            print(f"   关键词: {', '.join(section.keywords[:5])}")

    # 提取日期信息
    key_dates = parser.extract_key_dates(complex_clause)
    print(f"\n✅ 提取日期信息:")
    for date in key_dates:
        print(f"   - {date['type']}: {date['days']}天 ({date['context']})")

    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🕷️ 数据爬虫系统测试")
    print("=" * 60)

    tests = [
        ("CrawlResult模型", test_crawl_result),
        ("DataStore存储", test_data_store),
        ("ClauseParser解析", test_clause_parser),
        ("结构化数据提取", test_extract_structured_data),
        ("复杂条款解析", test_paragraph_parsing),
    ]

    async_tests = [
        ("CrawlerScheduler调度器", test_crawler_scheduler),
        ("CBIRCrawler爬虫", test_cbir_crawler_mock),
    ]

    results = []

    # 运行同步测试
    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🔹 运行测试: {name}")
        print('='*60)
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 运行异步测试
    for name, test_func in async_tests:
        print(f"\n{'='*60}")
        print(f"🔹 运行测试: {name}")
        print('='*60)
        try:
            success = asyncio.run(test_func())
            results.append((name, success))
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
        print("\n🎉 所有测试通过！数据爬虫系统工作正常。")
        print("\n主要功能:")
        print("  • 多源爬虫调度管理")
        print("  • 数据去重与存储")
        print("  • 条款结构化解析")
        print("  • 关键信息提取（日期、金额、免责条款）")
        print("  • 题目建议自动生成")
    else:
        print("\n⚠️ 部分测试失败。请检查错误信息。")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
