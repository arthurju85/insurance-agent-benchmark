"""
数值比对评分器
适用于计算题、保费计算等需要精确数值验证的场景
"""

from typing import Dict, Any, Optional
import math

from .base import BaseEvaluator
from models.evaluation import ValidationResult
from models.question import ValidationRule


class NumericChecker(BaseEvaluator):
    """
    数值比对评分器

    支持:
    - 绝对误差容忍（如±1元）
    - 相对误差容忍（如±0.1%）
    - 多数值检查（检查计算过程中的中间值）
    """

    def __init__(
        self,
        rule: ValidationRule,
        expected_value: Optional[float] = None,
        tolerance: Optional[float] = None,
        tolerance_type: str = "absolute",  # "absolute" or "relative"
        numeric_path: Optional[str] = None,
        intermediate_checks: Optional[list] = None
    ):
        super().__init__(rule)
        self.expected_value = expected_value
        self.tolerance = tolerance if tolerance is not None else rule.numeric_tolerance
        self.tolerance_type = tolerance_type or rule.numeric_tolerance_type
        self.numeric_path = numeric_path or rule.numeric_path
        self.intermediate_checks = intermediate_checks or []

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        执行数值比对
        """
        details = {
            "expected": self.expected_value,
            "extracted": None,
            "tolerance": self.tolerance,
            "tolerance_type": self.tolerance_type,
            "within_tolerance": False,
            "extraction_method": None
        }

        # 提取数值
        extracted_value = self._extract_numeric_value(agent_output, parsed_output)
        details["extracted"] = extracted_value

        if extracted_value is None:
            return ValidationResult(
                rule_type="numeric_check",
                passed=False,
                score=0.0,
                max_score=100.0,
                message="未能从输出中提取数值",
                details=details
            )

        # 计算误差
        if self.tolerance_type == "absolute":
            error = abs(extracted_value - self.expected_value)
            within_tolerance = error <= self.tolerance
        else:  # relative
            if self.expected_value == 0:
                within_tolerance = extracted_value == 0
                error = abs(extracted_value)
            else:
                error = abs(extracted_value - self.expected_value) / abs(self.expected_value)
                within_tolerance = error <= self.tolerance

        details["within_tolerance"] = within_tolerance
        details["error"] = error

        if within_tolerance:
            score = 100.0
            message = f"数值正确: {extracted_value} (期望: {self.expected_value}, 误差: {error:.4f})"
        else:
            score = 0.0
            message = f"数值错误: {extracted_value} (期望: {self.expected_value}, 误差: {error:.4f}, 容忍: {self.tolerance})"

        return ValidationResult(
            rule_type="numeric_check",
            passed=within_tolerance,
            score=score,
            max_score=100.0,
            message=message,
            details=details
        )

    def _extract_numeric_value(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]]
    ) -> Optional[float]:
        """
        从输出中提取数值
        优先级: parsed_output > JSON提取 > 文本提取
        """
        # 1. 尝试从parsed_output中提取（如果有指定路径）
        if parsed_output and self.numeric_path:
            value = self._get_nested_value(parsed_output, self.numeric_path)
            if value is not None:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    pass

        # 2. 尝试从agent_output中解析JSON并提取
        if self.numeric_path:
            json_data = self._safe_json_parse(agent_output)
            if json_data:
                value = self._get_nested_value(json_data, self.numeric_path)
                if value is not None:
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        pass

        # 3. 从文本中提取数值（最后手段）
        import re

        # 寻找特定模式，如"结果：1234"、"保费：5000元"等
        patterns = [
            r'(?:结果|答案|保费|金额|计算结果|最终结果)[:：]\s*([\d,]+\.?\d*)',
            r'[=＝]\s*([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*(?:元|块|￥|\$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, agent_output)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue

        return None


class MultiNumericChecker(BaseEvaluator):
    """
    多数值检查器
    检查计算过程中的多个中间值
    """

    def __init__(
        self,
        rule: ValidationRule,
        checks: list  # [{"path": "base_premium", "expected": 5000, "tolerance": 1}]
    ):
        super().__init__(rule)
        self.checks = checks

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        检查多个数值
        """
        json_data = parsed_output or self._safe_json_parse(agent_output) or {}

        details = {
            "checks": [],
            "passed_count": 0,
            "total_count": len(self.checks)
        }

        total_score = 0.0

        for check in self.checks:
            path = check["path"]
            expected = check["expected"]
            tolerance = check.get("tolerance", 1.0)
            tolerance_type = check.get("tolerance_type", "absolute")

            extracted = self._get_nested_value(json_data, path)

            check_result = {
                "path": path,
                "expected": expected,
                "extracted": extracted,
                "passed": False
            }

            if extracted is not None:
                try:
                    extracted_float = float(extracted)
                    if tolerance_type == "absolute":
                        passed = abs(extracted_float - expected) <= tolerance
                    else:
                        passed = abs(extracted_float - expected) / abs(expected) <= tolerance

                    check_result["passed"] = passed
                    if passed:
                        details["passed_count"] += 1
                        total_score += 100.0 / len(self.checks)
                except (ValueError, TypeError):
                    pass

            details["checks"].append(check_result)

        passed = details["passed_count"] == details["total_count"]

        return ValidationResult(
            rule_type="multi_numeric_check",
            passed=passed,
            score=total_score,
            max_score=100.0,
            message=f"数值检查: {details['passed_count']}/{details['total_count']} 通过",
            details=details
        )
