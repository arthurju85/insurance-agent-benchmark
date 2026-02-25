"""
关键词检查评分器
验证必须包含的关键词和禁止出现的关键词
"""

import re
from typing import Dict, Any, Optional, List

from .base import BaseEvaluator
from models.evaluation import ValidationResult
from models.question import ValidationRule


class KeywordChecker(BaseEvaluator):
    """
    关键词检查评分器

    支持:
    - must_contain_keywords: 必须全部包含的关键词列表
    - must_contain_any: 必须包含至少一个的关键词列表
    - prohibited_keywords: 禁止出现的关键词列表（出现则扣分/判错）
    """

    def __init__(
        self,
        rule: ValidationRule,
        must_contain: Optional[List[str]] = None,
        must_contain_any: Optional[List[str]] = None,
        prohibited: Optional[List[str]] = None,
        case_sensitive: bool = False
    ):
        super().__init__(rule)
        self.must_contain = must_contain or rule.must_contain_keywords or []
        self.must_contain_any = must_contain_any or rule.must_contain_any or []
        self.prohibited = prohibited or rule.prohibited_keywords or []
        self.case_sensitive = case_sensitive

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        执行关键词检查
        """
        text = agent_output if self.case_sensitive else agent_output.lower()

        details = {
            "must_contain_found": [],
            "must_contain_missing": [],
            "must_contain_any_found": [],
            "prohibited_found": []
        }

        # 检查必须包含的关键词
        for keyword in self.must_contain:
            check_word = keyword if self.case_sensitive else keyword.lower()
            if check_word in text:
                details["must_contain_found"].append(keyword)
            else:
                details["must_contain_missing"].append(keyword)

        # 检查must_contain_any（至少包含一个）
        if self.must_contain_any:
            found_any = False
            for keyword in self.must_contain_any:
                check_word = keyword if self.case_sensitive else keyword.lower()
                if check_word in text:
                    details["must_contain_any_found"].append(keyword)
                    found_any = True
                    break

        # 检查禁止出现的关键词
        for keyword in self.prohibited:
            check_word = keyword if self.case_sensitive else keyword.lower()
            if check_word in text:
                details["prohibited_found"].append(keyword)

        # 计算得分
        passed = True
        score = 100.0
        messages = []

        # 必须包含的关键词未全部出现
        if details["must_contain_missing"]:
            passed = False
            missing_count = len(details["must_contain_missing"])
            total_must = len(self.must_contain)
            score *= (total_must - missing_count) / total_must if total_must > 0 else 0
            messages.append(f"缺少关键词: {', '.join(details['must_contain_missing'])}")

        # must_contain_any未满足
        if self.must_contain_any and not details["must_contain_any_found"]:
            passed = False
            score *= 0.5
            messages.append(f"未包含任何关键词（需至少一个）: {', '.join(self.must_contain_any)}")

        # 出现禁止关键词（严重错误，直接判0分）
        if details["prohibited_found"]:
            passed = False
            score = 0
            messages.append(f"出现禁止关键词: {', '.join(details['prohibited_found'])}")

        return ValidationResult(
            rule_type="keyword_check",
            passed=passed,
            score=score,
            max_score=100.0,
            message="; ".join(messages) if messages else "关键词检查通过",
            details=details
        )


class RegexChecker(BaseEvaluator):
    """
    正则表达式检查评分器
    支持复杂模式匹配
    """

    def __init__(
        self,
        rule: ValidationRule,
        required_patterns: Optional[List[str]] = None,
        prohibited_patterns: Optional[List[str]] = None
    ):
        super().__init__(rule)
        self.required_patterns = required_patterns or []
        self.prohibited_patterns = prohibited_patterns or []

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        执行正则检查
        """
        details = {
            "required_matched": [],
            "required_missing": [],
            "prohibited_matched": []
        }

        # 检查必须匹配的模式
        for pattern in self.required_patterns:
            if re.search(pattern, agent_output):
                details["required_matched"].append(pattern)
            else:
                details["required_missing"].append(pattern)

        # 检查禁止匹配的模式
        for pattern in self.prohibited_patterns:
            if re.search(pattern, agent_output):
                details["prohibited_matched"].append(pattern)

        # 计算得分
        passed = True
        score = 100.0
        messages = []

        if details["required_missing"]:
            passed = False
            score *= (len(self.required_patterns) - len(details["required_missing"])) / len(self.required_patterns)
            messages.append(f"未匹配必要模式: {len(details['required_missing'])}个")

        if details["prohibited_matched"]:
            passed = False
            score = 0
            messages.append(f"出现禁止模式: {len(details['prohibited_matched'])}个")

        return ValidationResult(
            rule_type="regex_check",
            passed=passed,
            score=score,
            max_score=100.0,
            message="; ".join(messages) if messages else "正则检查通过",
            details=details
        )
