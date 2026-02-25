"""
结论验证评分器
验证Agent的结论是否与标准答案一致
适用于案例分析、判断题等
"""

from typing import Dict, Any, Optional, List

from .base import BaseEvaluator
from models.evaluation import ValidationResult
from models.question import ValidationRule


class ConclusionChecker(BaseEvaluator):
    """
    结论验证评分器

    支持:
    - 精确匹配（conclusion_exact_match）
    - 枚举匹配（conclusion_must_be_one_of）
    - 模糊匹配（包含关键词即算对）
    """

    def __init__(
        self,
        rule: ValidationRule,
        expected_conclusion: Optional[str] = None,
        allowed_conclusions: Optional[List[str]] = None,
        conclusion_path: str = "conclusion",
        case_sensitive: bool = False,
        partial_match: bool = False
    ):
        super().__init__(rule)
        self.expected_conclusion = expected_conclusion or rule.conclusion_exact_match
        self.allowed_conclusions = allowed_conclusions or rule.conclusion_must_be_one_of or []
        self.conclusion_path = conclusion_path
        self.case_sensitive = case_sensitive
        self.partial_match = partial_match

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        验证结论
        """
        details = {
            "expected": self.expected_conclusion or self.allowed_conclusions,
            "extracted": None,
            "match_type": None,
            "match_score": 0.0
        }

        # 提取结论
        extracted = self._extract_conclusion(agent_output, parsed_output)
        details["extracted"] = extracted

        if extracted is None:
            return ValidationResult(
                rule_type="conclusion_check",
                passed=False,
                score=0.0,
                max_score=100.0,
                message="未能提取结论",
                details=details
            )

        # 验证结论
        if self.expected_conclusion:
            # 精确匹配模式
            match = self._compare_conclusions(extracted, self.expected_conclusion)
            details["match_type"] = "exact"
            passed = match
            score = 100.0 if match else 0.0

        elif self.allowed_conclusions:
            # 枚举匹配模式
            matched_conclusion = None
            for allowed in self.allowed_conclusions:
                if self._compare_conclusions(extracted, allowed):
                    matched_conclusion = allowed
                    break

            details["match_type"] = "enum"
            passed = matched_conclusion is not None
            score = 100.0 if passed else 0.0
        else:
            return ValidationResult(
                rule_type="conclusion_check",
                passed=False,
                score=0.0,
                max_score=100.0,
                message="未配置结论验证规则",
                details=details
            )

        message = f"结论{'正确' if passed else '错误'}: {extracted}"
        if not passed:
            message += f" (期望: {self.expected_conclusion or self.allowed_conclusions})"

        return ValidationResult(
            rule_type="conclusion_check",
            passed=passed,
            score=score,
            max_score=100.0,
            message=message,
            details=details
        )

    def _extract_conclusion(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """
        从输出中提取结论
        """
        # 1. 从parsed_output中提取
        if parsed_output:
            conclusion = self._get_nested_value(parsed_output, self.conclusion_path)
            if conclusion is not None:
                return str(conclusion)

        # 2. 从JSON中提取
        json_data = self._safe_json_parse(agent_output)
        if json_data:
            conclusion = self._get_nested_value(json_data, self.conclusion_path)
            if conclusion is not None:
                return str(conclusion)

        # 3. 从文本中提取
        # 寻找常见结论关键词
        import re

        patterns = [
            r'(?:结论|判定|处理意见)[:：]\s*(.+?)(?:\n|$)',
            r'(?:因此|所以|综上)[:，]?\s*(.+?)(?:\n|$)',
            r'(?:理赔结论|核保结论)[:：]\s*(.+?)(?:\n|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, agent_output)
            if match:
                return match.group(1).strip()

        return None

    def _compare_conclusions(self, actual: str, expected: str) -> bool:
        """
        比较两个结论是否匹配
        """
        if not self.case_sensitive:
            actual = actual.lower()
            expected = expected.lower()

        if self.partial_match:
            return expected in actual or actual in expected

        return actual.strip() == expected.strip()


class LogicRuleEngine(BaseEvaluator):
    """
    逻辑规则引擎
    验证推理过程是否符合逻辑规则
    例如：前提A + 前提B → 结论C
    """

    def __init__(
        self,
        rule: ValidationRule,
        logic_rules: list  # [{"if": ["前提1", "前提2"], "then": "结论"}]
    ):
        super().__init__(rule)
        self.logic_rules = logic_rules

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        验证逻辑推理
        """
        text = agent_output.lower()

        details = {
            "rules_checked": [],
            "rules_passed": 0,
            "rules_failed": 0
        }

        for rule in self.logic_rules:
            conditions = rule.get("if", [])
            expected_conclusion = rule.get("then", "")

            rule_result = {
                "conditions": conditions,
                "expected_conclusion": expected_conclusion,
                "conditions_met": True,
                "conclusion_present": False
            }

            # 检查前提条件是否满足
            for condition in conditions:
                if condition.lower() not in text:
                    rule_result["conditions_met"] = False
                    break

            # 如果前提满足，检查结论是否存在
            if rule_result["conditions_met"]:
                if expected_conclusion.lower() in text:
                    rule_result["conclusion_present"] = True
                    details["rules_passed"] += 1
                else:
                    details["rules_failed"] += 1
            else:
                # 前提不满足，这条规则不适用于当前回答
                pass

            details["rules_checked"].append(rule_result)

        total_applicable = details["rules_passed"] + details["rules_failed"]

        if total_applicable == 0:
            score = 100.0  # 没有适用的规则，默认通过
            passed = True
            message = "无适用逻辑规则"
        else:
            score = (details["rules_passed"] / total_applicable) * 100.0
            passed = details["rules_failed"] == 0
            message = f"逻辑规则验证: {details['rules_passed']}/{total_applicable} 通过"

        return ValidationResult(
            rule_type="logic_rule",
            passed=passed,
            score=score,
            max_score=100.0,
            message=message,
            details=details
        )
