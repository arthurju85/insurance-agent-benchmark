"""
JSON Schema验证评分器
验证输出是否符合预期的JSON格式和字段要求
"""

import json
from typing import Dict, Any, Optional

from jsonschema import validate, ValidationError as JsonSchemaValidationError

from .base import BaseEvaluator
from models.evaluation import ValidationResult
from models.question import ValidationRule, ExpectedOutputSchema


class SchemaValidator(BaseEvaluator):
    """
    JSON Schema验证评分器

    验证:
    - 是否为有效JSON
    - 是否符合JSON Schema
    - 是否包含必需字段
    - 字段类型是否正确
    """

    def __init__(
        self,
        rule: ValidationRule,
        schema: Optional[Dict[str, Any]] = None,
        required_fields: Optional[list] = None
    ):
        super().__init__(rule)
        self.schema = schema
        self.required_fields = required_fields or []

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        执行Schema验证
        """
        details = {
            "is_valid_json": False,
            "schema_valid": False,
            "missing_fields": [],
            "type_errors": [],
            "parse_error": None
        }

        # 1. 解析JSON
        if parsed_output is not None:
            data = parsed_output
            details["is_valid_json"] = True
        else:
            try:
                data = json.loads(agent_output)
                details["is_valid_json"] = True
            except json.JSONDecodeError as e:
                details["parse_error"] = str(e)
                # 尝试提取JSON
                data = self._safe_json_parse(agent_output)
                if data is not None:
                    details["is_valid_json"] = True
                    details["extraction_used"] = True
                else:
                    return ValidationResult(
                        rule_type="schema_validation",
                        passed=False,
                        score=0.0,
                        max_score=100.0,
                        message=f"JSON解析失败: {str(e)}",
                        details=details
                    )

        score = 0.0
        max_score = 100.0

        # 2. 检查必需字段
        if self.required_fields:
            for field in self.required_fields:
                if self._get_nested_value(data, field) is None:
                    details["missing_fields"].append(field)

            if details["missing_fields"]:
                score += 50.0 * (1 - len(details["missing_fields"]) / len(self.required_fields))
            else:
                score += 50.0

        # 3. JSON Schema验证
        if self.schema:
            try:
                validate(instance=data, schema=self.schema)
                details["schema_valid"] = True
                score += 50.0
            except JsonSchemaValidationError as e:
                details["schema_error"] = str(e)
                # Schema部分错误，根据错误数量扣分
                score += max(0, 50.0 - 10.0)  # 基础分
        else:
            # 没有schema，只要JSON有效且字段齐全就给分
            score = 100.0 if not details["missing_fields"] else score

        passed = details["is_valid_json"] and not details["missing_fields"]
        if self.schema:
            passed = passed and details["schema_valid"]

        return ValidationResult(
            rule_type="schema_validation",
            passed=passed,
            score=score,
            max_score=max_score,
            message=self._build_message(details),
            details=details
        )

    def _build_message(self, details: Dict) -> str:
        """构建验证消息"""
        if not details["is_valid_json"]:
            return "JSON格式无效"

        messages = []
        if details.get("missing_fields"):
            messages.append(f"缺少字段: {', '.join(details['missing_fields'])}")

        if not details.get("schema_valid") and self.schema:
            messages.append("JSON Schema验证失败")

        if not messages:
            return "Schema验证通过"

        return "; ".join(messages)


class FieldTypeChecker(BaseEvaluator):
    """
    字段类型检查器
    检查特定字段的类型是否符合预期
    """

    def __init__(
        self,
        rule: ValidationRule,
        field_checks: list  # [{"path": "age", "type": "integer", "range": [0, 150]}]
    ):
        super().__init__(rule)
        self.field_checks = field_checks

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        检查字段类型
        """
        data = parsed_output or self._safe_json_parse(agent_output) or {}

        details = {
            "checks": [],
            "passed_count": 0,
            "total_count": len(self.field_checks)
        }

        for check in self.field_checks:
            path = check["path"]
            expected_type = check["type"]
            expected_range = check.get("range")

            value = self._get_nested_value(data, path)

            check_result = {
                "path": path,
                "expected_type": expected_type,
                "actual_value": value,
                "type_match": False,
                "range_match": True
            }

            # 检查类型
            type_map = {
                "string": str,
                "integer": int,
                "number": (int, float),
                "boolean": bool,
                "array": list,
                "object": dict
            }

            if value is not None:
                expected_python_type = type_map.get(expected_type)
                if expected_python_type:
                    if isinstance(value, expected_python_type):
                        check_result["type_match"] = True

                # 检查范围
                if expected_range and check_result["type_match"]:
                    if isinstance(value, (int, float)):
                        min_val, max_val = expected_range
                        if not (min_val <= value <= max_val):
                            check_result["range_match"] = False

            if check_result["type_match"] and check_result["range_match"]:
                details["passed_count"] += 1

            details["checks"].append(check_result)

        passed = details["passed_count"] == details["total_count"]
        score = (details["passed_count"] / details["total_count"]) * 100.0

        return ValidationResult(
            rule_type="field_type_check",
            passed=passed,
            score=score,
            max_score=100.0,
            message=f"字段类型检查: {details['passed_count']}/{details['total_count']} 通过",
            details=details
        )
