"""
保险条款解析器
从爬取的文本中提取结构化信息
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import jieba
    import jieba.posseg as pseg
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    jieba = None
    pseg = None


class ClauseType(str, Enum):
    """条款类型"""
    INSURANCE_LIABILITY = "保险责任"
    EXCLUSION = "责任免除"
    CLAIM = "理赔申请"
    WAITING_PERIOD = "等待期"
    COOLING_OFF = "犹豫期"
    PREMIUM = "保险费"
    POLICY_LOAN = "保单贷款"
    SURRENDER = "解除合同"
    BENEFICIARY = "受益人"
    GENERAL = "一般条款"


@dataclass
class ClauseSection:
    """条款章节"""
    title: str
    clause_type: ClauseType
    content: str
    article_number: Optional[str] = None
    keywords: List[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class InsuranceClause:
    """解析后的保险条款"""
    product_name: str
    company: str
    clause_type: str  # 产品类型：重疾险/医疗险/意外险等
    sections: List[ClauseSection]
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ClauseParser:
    """
    保险条款解析器
    从原始文本中提取结构化条款信息
    """

    # 条款类型关键词映射
    TYPE_KEYWORDS = {
        ClauseType.INSURANCE_LIABILITY: [
            "保险责任", "我们保什么", "保障范围", "给付条件"
        ],
        ClauseType.EXCLUSION: [
            "责任免除", "我们不保", "除外责任", "免责条款"
        ],
        ClauseType.CLAIM: [
            "保险金申请", "理赔", "如何领取保险金", "保险金给付"
        ],
        ClauseType.WAITING_PERIOD: [
            "等待期", "观察期", "免责期"
        ],
        ClauseType.COOLING_OFF: [
            "犹豫期", "冷静期", "反悔期", "合同撤回"
        ],
        ClauseType.PREMIUM: [
            "保险费", "缴费", "保险费的交纳", "宽限期"
        ],
        ClauseType.POLICY_LOAN: [
            "保单贷款", "现金价值", "保单借款"
        ],
        ClauseType.SURRENDER: [
            "解除合同", "退保", "合同终止", "现金价值退还"
        ],
        ClauseType.BENEFICIARY: [
            "受益人", "保险金受益人", "受益人指定"
        ],
    }

    def __init__(self):
        # 加载保险领域词典
        self._load_insurance_dict()

    def _load_insurance_dict(self):
        """加载保险专业词汇"""
        if not JIEBA_AVAILABLE:
            return

        insurance_terms = [
            "保险责任", "责任免除", "等待期", "犹豫期", "宽限期",
            "现金价值", "保单贷款", "减额交清", "受益人", "投保人",
            "被保险人", "保险金额", "保险费", "保险期间", "保险事故",
            "重大疾病", "轻度疾病", "意外伤残", "住院医疗", "门诊手术",
            "特定疾病", "恶性肿瘤", "急性心肌梗死", "脑中风后遗症"
        ]
        for term in insurance_terms:
            jieba.add_word(term, freq=1000)

    def parse(self, text: str, product_name: str = "", company: str = "") -> InsuranceClause:
        """
        解析保险条款文本

        Args:
            text: 原始条款文本
            product_name: 产品名称
            company: 保险公司

        Returns:
            结构化条款对象
        """
        # 识别产品类型
        clause_type = self._identify_clause_type(text, product_name)

        # 分章节解析
        sections = self._split_sections(text)

        return InsuranceClause(
            product_name=product_name,
            company=company,
            clause_type=clause_type,
            sections=sections,
            metadata={
                "total_sections": len(sections),
                "parsed_at": None
            }
        )

    def _identify_clause_type(self, text: str, product_name: str) -> str:
        """识别保险条款类型"""
        combined_text = f"{product_name} {text[:1000]}"

        type_keywords = {
            "重疾险": ["重大疾病", "重疾", "轻症", "中症"],
            "医疗险": ["医疗保险", "住院", "门诊", "医疗费用"],
            "意外险": ["意外伤害", "意外伤残", "意外医疗"],
            "寿险": ["身故", "全残", "人寿保险"],
            "年金险": ["年金", "生存金", "养老金"],
            "防癌险": ["癌症", "恶性肿瘤"],
        }

        scores = {}
        for ptype, keywords in type_keywords.items():
            score = sum(1 for kw in keywords if kw in combined_text)
            if score > 0:
                scores[ptype] = score

        if scores:
            return max(scores, key=scores.get)

        return "未知类型"

    def _split_sections(self, text: str) -> List[ClauseSection]:
        """将条款文本分割为章节"""
        sections = []

        # 识别章节标题模式
        # 支持："第X条"、"X."、"X、"、"第X章"等格式
        section_patterns = [
            r'第[一二三四五六七八九十\d]+条[^\n]*',  # 第X条
            r'第[一二三四五六七八九十\d]+章[^\n]*',  # 第X章
            r'^[\d一二三四五六七八九十]+[\.、][^\n]*',  # X. 或 X、
        ]

        # 尝试找到所有章节边界
        boundaries = []
        for pattern in section_patterns:
            for match in re.finditer(pattern, text, re.MULTILINE):
                boundaries.append((match.start(), match.end(), match.group()))

        # 按位置排序
        boundaries.sort(key=lambda x: x[0])

        # 提取各章节内容
        if boundaries:
            for i, (start, end, title) in enumerate(boundaries):
                # 章节内容从标题结束到下一章节开始
                content_start = end
                content_end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
                content = text[content_start:content_end].strip()

                # 识别条款类型
                clause_type = self._identify_section_type(title, content)

                # 提取关键词
                keywords = self._extract_keywords(content)

                sections.append(ClauseSection(
                    title=title.strip(),
                    clause_type=clause_type,
                    content=content[:2000],  # 限制长度
                    article_number=self._extract_article_number(title),
                    keywords=keywords
                ))

        # 如果没有识别到章节，整体作为一个章节
        if not sections:
            sections.append(ClauseSection(
                title="全文",
                clause_type=ClauseType.GENERAL,
                content=text[:5000],
                keywords=self._extract_keywords(text)
            ))

        return sections

    def _identify_section_type(self, title: str, content: str) -> ClauseType:
        """识别章节类型"""
        combined = f"{title} {content[:200]}"

        scores = {}
        for stype, keywords in self.TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > 0:
                scores[stype] = score

        if scores:
            return max(scores, key=scores.get)

        return ClauseType.GENERAL

    def _extract_article_number(self, title: str) -> Optional[str]:
        """提取条款编号"""
        patterns = [
            r'第([一二三四五六七八九十\d]+)条',
            r'第([一二三四五六七八九十\d]+)章',
            r'^([\d一二三四五六七八九十]+)[\.、]'
        ]

        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1)

        return None

    def _extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        if not JIEBA_AVAILABLE:
            # 简单的关键词提取（不使用jieba）
            # 返回保险相关术语
            insurance_terms = [
                "保险责任", "责任免除", "等待期", "犹豫期", "宽限期",
                "现金价值", "保单贷款", "受益人", "投保人", "被保险人",
                "保险金额", "保险费", "理赔", "重疾", "意外"
            ]
            found = [t for t in insurance_terms if t in text]
            return found[:top_k]

        # 使用jieba进行词性标注，提取名词和动词
        words = pseg.cut(text)

        # 过滤停用词和短词
        keywords = []
        for word, flag in words:
            if len(word) >= 2 and flag in ['n', 'v', 'ns', 'nt', 'nz']:
                keywords.append(word)

        # 统计词频
        from collections import Counter
        word_counts = Counter(keywords)

        return [w for w, c in word_counts.most_common(top_k)]

    def extract_key_dates(self, text: str) -> List[Dict]:
        """
        提取关键日期信息

        Returns:
            日期信息列表，包含日期值和说明
        """
        dates = []

        # 模式匹配
        patterns = [
            (r'(\d+)日?的?等待期', 'waiting_period_days'),
            (r'等待期为?(\d+)日?', 'waiting_period_days'),
            (r'(\d+)日?的?犹豫期', 'cooling_off_days'),
            (r'犹豫期为?(\d+)日?', 'cooling_off_days'),
            (r'(\d+)日?的?宽限期', 'grace_period_days'),
            (r'宽限期为?(\d+)日?', 'grace_period_days'),
        ]

        for pattern, date_type in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                days = match.group(1)
                dates.append({
                    'type': date_type,
                    'days': int(days),
                    'context': match.group(0)
                })

        return dates

    def extract_coverage_amounts(self, text: str) -> List[Dict]:
        """提取保额信息"""
        amounts = []

        # 匹配金额模式
        pattern = r'(基本)?保险金额(?:为)?(\d+(?:,\d{3})*)(?:元|万元)?'

        for match in re.finditer(pattern, text):
            amounts.append({
                'type': 'basic_coverage',
                'amount': match.group(2).replace(',', ''),
                'unit': '元',
                'context': match.group(0)
            })

        return amounts

    def extract_exclusions(self, text: str) -> List[str]:
        """提取责任免除条款"""
        exclusions = []

        # 查找责任免除部分
        exclusion_section = self._find_section_by_type(text, ClauseType.EXCLUSION)
        if exclusion_section:
            # 提取列举项
            items = re.findall(r'[（(]([一二三四五六七八九十\d]+)[）)]([^；。]+)', exclusion_section)
            for _, item in items:
                exclusions.append(item.strip())

        return exclusions

    def _find_section_by_type(self, text: str, clause_type: ClauseType) -> Optional[str]:
        """查找特定类型的章节内容"""
        sections = self._split_sections(text)
        for section in sections:
            if section.clause_type == clause_type:
                return section.content
        return None

    def generate_question_suggestions(self, clause: InsuranceClause) -> List[Dict]:
        """
        基于条款内容生成评测题目建议

        Returns:
            题目建议列表
        """
        suggestions = []

        for section in clause.sections:
            # 根据章节类型生成不同类型的题目建议

            if section.clause_type == ClauseType.WAITING_PERIOD:
                # 等待期题目
                dates = self.extract_key_dates(section.content)
                for date in dates:
                    suggestions.append({
                        'type': 'waiting_period_calculation',
                        'dimension': 'knowledge',
                        'suggested_question': f"客户投保后第{date['days']-10}天确诊重疾，是否理赔？",
                        'key_point': f'等待期为{date["days"]}日',
                        'source_section': section.title
                    })

            elif section.clause_type == ClauseType.EXCLUSION:
                # 责任免除题目
                exclusions = self.extract_exclusions(section.content)
                if exclusions:
                    suggestions.append({
                        'type': 'exclusion_identification',
                        'dimension': 'knowledge',
                        'suggested_question': "以下哪种情况属于责任免除范围？",
                        'options': exclusions[:4] if len(exclusions) >= 4 else exclusions,
                        'source_section': section.title
                    })

            elif section.clause_type == ClauseType.CLAIM:
                # 理赔流程题目
                suggestions.append({
                    'type': 'claim_process',
                    'dimension': 'knowledge',
                    'suggested_question': "申请理赔需要提供哪些材料？",
                    'key_points': section.keywords,
                    'source_section': section.title
                })

        return suggestions


# 便捷函数
def parse_clause(text: str, product_name: str = "", company: str = "") -> InsuranceClause:
    """便捷解析函数"""
    parser = ClauseParser()
    return parser.parse(text, product_name, company)


def extract_structured_data(text: str) -> Dict:
    """从条款文本提取结构化数据"""
    parser = ClauseParser()
    clause = parser.parse(text)

    # 提取所有结构化信息
    full_text = " ".join([s.content for s in clause.sections])

    return {
        "product_type": clause.clause_type,
        "sections_count": len(clause.sections),
        "key_dates": parser.extract_key_dates(full_text),
        "coverage_amounts": parser.extract_coverage_amounts(full_text),
        "exclusions": parser.extract_exclusions(full_text),
        "question_suggestions": parser.generate_question_suggestions(clause),
        "section_types": [s.clause_type.value for s in clause.sections]
    }
