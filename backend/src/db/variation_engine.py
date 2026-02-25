"""
题目变异引擎
用于自动生成题目变体，防止数据污染和过拟合
支持数值变异、实体替换、句式重组等多种变异策略
"""

import random
import re
import json
import hashlib
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from copy import deepcopy

try:
    from ..models.question import Question, QuestionType, ValidationRule
except ImportError:
    # 直接运行时
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from models.question import Question, QuestionType, ValidationRule


@dataclass
class VariationConfig:
    """变异配置"""
    # 数值变异范围
    date_offset_days: Tuple[int, int] = (-365, 365)  # 日期偏移范围
    amount_variance: float = 0.2  # 金额变异幅度（±20%）
    age_variance: Tuple[int, int] = (-5, 5)  # 年龄变异范围

    # 实体替换池
    name_pool: List[str] = field(default_factory=lambda: [
        "张某", "李某", "王某", "赵某", "刘某", "陈某", "杨某", "黄某",
        "周某", "吴某", "徐某", "孙某", "马某", "胡某", "郭某人", "林某"
    ])

    company_pool: List[str] = field(default_factory=lambda: [
        "平安保险", "太保", "中国人寿", "新华保险", "泰康保险",
        "友邦保险", "太平保险", "人保健康", "阳光保险"
    ])

    city_pool: List[str] = field(default_factory=lambda: [
        "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉",
        "西安", "重庆", "天津", "苏州", "青岛", "厦门", "大连"
    ])

    hospital_pool: List[str] = field(default_factory=lambda: [
        "协和医院", "瑞金医院", "华西医院", "中山医院", "阜外医院",
        "积水潭医院", "301医院", "同济医院", "湘雅医院", "齐鲁医院"
    ])

    disease_pool: Dict[str, List[str]] = field(default_factory=lambda: {
        "癌症": ["肺癌", "胃癌", "肝癌", "乳腺癌", "结肠癌", "食管癌"],
        "心血管疾病": ["急性心梗", "脑中风", "冠心病", "心绞痛"],
        "意外": ["交通事故", "跌倒摔伤", "高空坠物", "运动受伤"]
    })

    # 变异策略开关
    enable_date_variation: bool = True
    enable_amount_variation: bool = True
    enable_name_replacement: bool = True
    enable_company_replacement: bool = True
    enable_sentence_restructure: bool = True


class VariationEngine:
    """
    题目变异引擎

    变异原则：
    1. 保持题目逻辑不变
    2. 保持验证规则有效性
    3. 保持难度不变
    4. 保持ground_truth可计算
    """

    def __init__(self, config: VariationConfig = None, seed: Optional[int] = None):
        self.config = config or VariationConfig()
        self.seed = seed or random.randint(0, 2**32)
        self.rng = random.Random(self.seed)

        # 实体映射表（保证同一次变异中同一实体映射到同一替换）
        self.entity_map: Dict[str, str] = {}

    def _get_consistent_mapping(self, original: str, pool: List[str]) -> str:
        """获取一致的实体映射"""
        if original not in self.entity_map:
            # 使用hash保证相同seed产生相同映射
            hash_input = f"{self.seed}_{original}"
            hash_val = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            idx = hash_val % len(pool)
            self.entity_map[original] = pool[idx]
        return self.entity_map[original]

    def _extract_dates(self, text: str) -> List[Tuple[str, datetime]]:
        """从文本中提取日期"""
        dates = []

        # 匹配 "2024年1月1日" 格式
        pattern1 = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
        for match in re.finditer(pattern1, text):
            try:
                date = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                dates.append((match.group(0), date))
            except ValueError:
                continue

        # 匹配 "2024-01-01" 格式
        pattern2 = r'(\d{4})-(\d{2})-(\d{2})'
        for match in re.finditer(pattern2, text):
            try:
                date = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                dates.append((match.group(0), date))
            except ValueError:
                continue

        return dates

    def _extract_amounts(self, text: str) -> List[Tuple[str, float]]:
        """从文本中提取金额"""
        amounts = []

        # 匹配 "10,000元" 或 "10000元" 或 "1万元"
        patterns = [
            r'(\d{1,3}(?:,\d{3})+)(?:\s*)元',
            r'(\d+)(?:\s*)元',
            r'(\d+\.?\d*)万(?:元)?'
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text):
                try:
                    num_str = match.group(1).replace(',', '')
                    if '万' in match.group(0) or '万元' in match.group(0):
                        value = float(num_str) * 10000
                    else:
                        value = float(num_str)
                    amounts.append((match.group(0), value))
                except ValueError:
                    continue

        return amounts

    def _extract_ages(self, text: str) -> List[Tuple[str, int]]:
        """从文本中提取年龄"""
        ages = []
        pattern = r'(\d{1,3})岁'
        for match in re.finditer(pattern, text):
            try:
                age = int(match.group(1))
                if 0 <= age <= 120:  # 合理的年龄范围
                    ages.append((match.group(0), age))
            except ValueError:
                continue
        return ages

    def _extract_names(self, text: str) -> List[str]:
        """提取中文人名（X某 或 XX 格式）"""
        names = []
        # 匹配 "X某" 格式
        pattern1 = r'[李王张刘陈杨黄赵周吴徐孙马胡郭林][某]'
        names.extend(re.findall(pattern1, text))
        return list(set(names))

    def _extract_companies(self, text: str) -> List[str]:
        """提取保险公司名称"""
        companies = []
        for company in self.config.company_pool:
            if company in text:
                companies.append(company)
        return companies

    def _extract_diseases(self, text: str) -> List[Tuple[str, str]]:
        """提取疾病名称及其类别"""
        diseases = []
        for category, disease_list in self.config.disease_pool.items():
            for disease in disease_list:
                if disease in text:
                    diseases.append((disease, category))
        return diseases

    def _generate_date_offset(self, original: datetime) -> datetime:
        """生成日期偏移"""
        min_days, max_days = self.config.date_offset_days
        offset = self.rng.randint(min_days, max_days)
        return original + timedelta(days=offset)

    def _generate_amount_variance(self, original: float) -> float:
        """生成金额变异"""
        variance = self.rng.uniform(-self.config.amount_variance, self.config.amount_variance)
        return round(original * (1 + variance))

    def _generate_age_variance(self, original: int) -> int:
        """生成年龄变异"""
        min_var, max_var = self.config.age_variance
        variance = self.rng.randint(min_var, max_var)
        return max(0, min(120, original + variance))

    def _format_date(self, date: datetime) -> str:
        """格式化日期"""
        return f"{date.year}年{date.month}月{date.day}日"

    def _format_amount(self, amount: float) -> str:
        """格式化金额"""
        if amount >= 10000:
            return f"{amount/10000:.1f}万元"
        else:
            return f"{int(amount)}元"

    def _restructure_sentence(self, text: str) -> str:
        """句式重组 - 简单实现：调整语序"""
        # 将"因...所以..."改为"由于...因此..."
        replacements = [
            ("因为", "由于"),
            ("所以", "因此"),
            ("但是", "然而"),
            ("如果", "若"),
            ("应该", "应当"),
            ("可以", "可"),
        ]

        result = text
        for old, new in replacements:
            if self.rng.random() < 0.3:  # 30%概率替换
                result = result.replace(old, new)

        return result

    def _update_ground_truth_dates(self, ground_truth: Dict, date_mapping: Dict[str, str]) -> Dict:
        """更新ground_truth中的日期相关字段"""
        new_gt = deepcopy(ground_truth)

        # 更新calculation_days（如果存在）
        if 'calculation_days' in new_gt:
            # 重新计算天数
            offset = self.rng.randint(-10, 10)
            new_gt['calculation_days'] = max(0, new_gt['calculation_days'] + offset)

        return new_gt

    def _update_ground_truth_amounts(self, ground_truth: Dict, amount_mapping: Dict[float, float]) -> Dict:
        """更新ground_truth中的金额相关字段"""
        new_gt = deepcopy(ground_truth)

        # 递归处理字典
        def update_amounts_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (int, float)) and key in ['refund_amount', 'max_loan_amount', 'result', 'company_a_payment', 'company_b_payment']:
                        # 应用相同的变异比例
                        if value in amount_mapping:
                            obj[key] = amount_mapping[value]
                        else:
                            # 使用相同的变异因子
                            variance = self.rng.uniform(-self.config.amount_variance, self.config.amount_variance)
                            obj[key] = round(value * (1 + variance))
                    elif isinstance(value, (dict, list)):
                        update_amounts_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    update_amounts_recursive(item)

        update_amounts_recursive(new_gt)
        return new_gt

    def _update_validation_rules(self, rules: ValidationRule, content_changes: Dict) -> ValidationRule:
        """更新验证规则以适应变异后的题目"""
        new_rules = deepcopy(rules)

        # 更新关键词验证
        if new_rules.must_contain_keywords:
            # 更新日期相关关键词
            if 'date_mapping' in content_changes:
                for old_date, new_date in content_changes['date_mapping'].items():
                    new_rules.must_contain_keywords = [
                        kw.replace(old_date, new_date) if isinstance(kw, str) else kw
                        for kw in new_rules.must_contain_keywords
                    ]

        return new_rules

    def generate_variation(self, question: Question, variation_index: int = 0) -> Question:
        """
        生成题目变体

        Args:
            question: 原始题目
            variation_index: 变异索引（用于生成不同的变体）

        Returns:
            变异后的新题目
        """
        # 重置实体映射表
        self.entity_map = {}

        # 使用variation_index调整随机种子
        effective_seed = self.seed + variation_index * 1000
        self.rng = random.Random(effective_seed)

        # 创建题目副本
        new_question = deepcopy(question)

        # 生成新的题目ID
        new_question.question_id = f"{question.question_id}_var{variation_index}"
        new_question.is_variant = True
        new_question.parent_id = question.question_id
        new_question.variant_seed = effective_seed
        new_question.created_at = datetime.now().isoformat()

        # 记录所有变更
        content_changes = {}

        # 1. 变异content
        new_content = question.content

        # 日期变异
        if self.config.enable_date_variation:
            dates = self._extract_dates(new_content)
            date_mapping = {}
            for original_str, original_date in dates:
                new_date = self._generate_date_offset(original_date)
                new_date_str = self._format_date(new_date)
                date_mapping[original_str] = new_date_str
                new_content = new_content.replace(original_str, new_date_str, 1)
            content_changes['date_mapping'] = date_mapping

        # 金额变异
        if self.config.enable_amount_variation:
            amounts = self._extract_amounts(new_content)
            amount_mapping = {}
            for original_str, original_amount in amounts:
                new_amount = self._generate_amount_variance(original_amount)
                amount_mapping[original_amount] = new_amount
                # 保留原始格式
                if '万' in original_str:
                    new_amount_str = f"{new_amount/10000:.1f}万元"
                else:
                    new_amount_str = f"{int(new_amount)}元"
                new_content = new_content.replace(original_str, new_amount_str, 1)
            content_changes['amount_mapping'] = amount_mapping

        # 年龄变异
        ages = self._extract_ages(new_content)
        for original_str, original_age in ages:
            new_age = self._generate_age_variance(original_age)
            new_age_str = f"{new_age}岁"
            new_content = new_content.replace(original_str, new_age_str, 1)

        # 人名替换
        if self.config.enable_name_replacement:
            names = self._extract_names(new_content)
            for name in names:
                new_name = self._get_consistent_mapping(name, self.config.name_pool)
                new_content = new_content.replace(name, new_name)

        # 保险公司替换
        if self.config.enable_company_replacement:
            companies = self._extract_companies(new_content)
            for company in companies:
                new_company = self._get_consistent_mapping(company, self.config.company_pool)
                new_content = new_content.replace(company, new_company)

        # 句式重组
        if self.config.enable_sentence_restructure:
            new_content = self._restructure_sentence(new_content)

        new_question.content = new_content

        # 2. 变异context（如果有）
        if question.context:
            new_context = question.context

            # 应用相同的替换
            if 'date_mapping' in content_changes:
                for old_date, new_date in content_changes['date_mapping'].items():
                    new_context = new_context.replace(old_date, new_date)

            names = self._extract_names(new_context)
            for name in names:
                new_name = self._get_consistent_mapping(name, self.config.name_pool)
                new_context = new_context.replace(name, new_name)

            companies = self._extract_companies(new_context)
            for company in companies:
                new_company = self._get_consistent_mapping(company, self.config.company_pool)
                new_context = new_context.replace(company, new_company)

            new_question.context = new_context

        # 3. 更新ground_truth
        if question.ground_truth:
            new_gt = question.ground_truth

            if 'date_mapping' in content_changes:
                new_gt = self._update_ground_truth_dates(new_gt, content_changes['date_mapping'])

            if 'amount_mapping' in content_changes:
                new_gt = self._update_ground_truth_amounts(new_gt, content_changes['amount_mapping'])

            # 更新关键词相关字段
            if 'reasoning' in new_gt and isinstance(new_gt['reasoning'], str):
                if 'date_mapping' in content_changes:
                    for old_date, new_date in content_changes['date_mapping'].items():
                        new_gt['reasoning'] = new_gt['reasoning'].replace(old_date, new_date)

            new_question.ground_truth = new_gt

        # 4. 更新验证规则
        new_question.validation_rules = self._update_validation_rules(
            question.validation_rules,
            content_changes
        )

        # 5. 更新标签
        new_question.tags = question.tags + ["variant", f"seed_{effective_seed}"]

        return new_question

    def generate_variations(self, question: Question, count: int) -> List[Question]:
        """
        批量生成多个变体

        Args:
            question: 原始题目
            count: 变体数量

        Returns:
            变体列表（不包含原始题目）
        """
        variations = []
        for i in range(count):
            var = self.generate_variation(question, variation_index=i + 1)
            variations.append(var)
        return variations

    def generate_question_set_variations(
        self,
        questions: List[Question],
        variations_per_question: int = 3
    ) -> List[Question]:
        """
        为题集中的每道题生成变体

        Args:
            questions: 原始题集
            variations_per_question: 每道题的变体数量

        Returns:
            包含原题和所有变体的完整列表
        """
        all_questions = list(questions)  # 包含原题

        for question in questions:
            variations = self.generate_variations(question, variations_per_question)
            all_questions.extend(variations)

        return all_questions


def create_variant_set(
    source_set_path: str,
    output_path: str,
    variations_per_question: int = 3,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    从现有题集创建变体题集（工具函数）

    Args:
        source_set_path: 源题集文件路径
        output_path: 输出文件路径
        variations_per_question: 每道题的变体数量
        seed: 随机种子

    Returns:
        生成的题集统计信息
    """
    import os

    # 加载源题集
    with open(source_set_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 解析题目
    questions = [Question(**q) for q in data['questions']]

    # 创建变异引擎
    engine = VariationEngine(seed=seed)

    # 生成变体
    all_questions = engine.generate_question_set_variations(
        questions,
        variations_per_question
    )

    # 构建输出
    output_data = {
        "metadata": {
            **data.get('metadata', {}),
            "variant_of": data.get('metadata', {}).get('set_id', 'unknown'),
            "variation_config": {
                "variations_per_question": variations_per_question,
                "seed": seed,
                "total_variants": len(all_questions) - len(questions)
            }
        },
        "questions": [q.model_dump() for q in all_questions]
    }

    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    return {
        "source_questions": len(questions),
        "total_questions": len(all_questions),
        "variants_generated": len(all_questions) - len(questions),
        "output_path": output_path
    }


def generate_paraphrase_variations(text: str, count: int = 3) -> List[str]:
    """
    生成文本的改写变体（简单的同义词替换）

    Args:
        text: 原始文本
        count: 变体数量

    Returns:
        改写后的文本列表
    """
    # 同义词映射表
    synonyms = {
        "投保人": ["保单持有人", "要保人"],
        "被保险人": ["受保人", "保险对象"],
        "受益人": ["保险金受领人"],
        "保险金": ["理赔金", "赔付金"],
        "保险责任": ["承保范围", "保障内容"],
        "免赔额": ["起付线", "自负额"],
        "等待期": ["观察期", "免责期"],
        "犹豫期": ["冷静期", "反悔期"],
        "解除合同": ["退保", "终止合同"],
        "给付": ["赔付", "支付"],
    }

    variations = []
    rng = random.Random()

    for i in range(count):
        new_text = text
        for word, alternatives in synonyms.items():
            if word in new_text and rng.random() < 0.5:
                new_text = new_text.replace(word, rng.choice(alternatives), 1)
        variations.append(new_text)

    return variations
