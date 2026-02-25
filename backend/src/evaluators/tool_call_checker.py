"""
工具调用验证评分器
验证Agent是否正确调用了工具
"""

from typing import Dict, Any, Optional, List

from .base import BaseEvaluator
from models.evaluation import ValidationResult
from models.question import ValidationRule


class ToolCallChecker(BaseEvaluator):
    """
    工具调用验证评分器

    验证:
    - 是否调用了必需的工具
    - 工具调用顺序是否正确
    - 工具参数是否正确
    """

    def __init__(
        self,
        rule: ValidationRule,
        required_tools: Optional[List[str]] = None,
        tool_sequence: Optional[List[str]] = None,
        strict_sequence: bool = False,
        param_checks: Optional[List[Dict]] = None
    ):
        super().__init__(rule)
        self.required_tools = required_tools or rule.required_tools or []
        self.tool_sequence = tool_sequence or []
        self.strict_sequence = strict_sequence or rule.tool_sequence_strict
        self.param_checks = param_checks or []

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict]] = None
    ) -> ValidationResult:
        """
        验证工具调用

        Args:
            agent_output: Agent输出文本
            parsed_output: 解析后的输出
            tool_calls: 工具调用记录（从AgentResponse中获取）
        """
        details = {
            "required_tools": self.required_tools,
            "tools_called": [],
            "missing_tools": [],
            "sequence_correct": True,
            "param_checks": [],
            "tool_calls": tool_calls or []
        }

        # 如果没有提供tool_calls，尝试从输出中提取
        if not tool_calls:
            tool_calls = self._extract_tool_calls(agent_output, parsed_output)

        details["tools_called"] = [tc.get("function", {}).get("name", tc.get("name", "")) for tc in tool_calls]

        score = 100.0
        messages = []

        # 1. 检查必需工具是否都被调用
        if self.required_tools:
            called_tool_names = set(details["tools_called"])
            required_tool_names = set(self.required_tools)

            details["missing_tools"] = list(required_tool_names - called_tool_names)

            if details["missing_tools"]:
                score -= len(details["missing_tools"]) * 25.0
                messages.append(f"未调用必需工具: {', '.join(details['missing_tools'])}")

        # 2. 检查调用顺序
        if self.tool_sequence and self.strict_sequence:
            actual_sequence = details["tools_called"]
            expected_sequence = self.tool_sequence

            if actual_sequence != expected_sequence:
                details["sequence_correct"] = False
                score -= 30.0
                messages.append("工具调用顺序不正确")

        # 3. 检查参数
        if self.param_checks:
            for check in self.param_checks:
                tool_name = check.get("tool")
                param_name = check.get("param")
                expected_value = check.get("expected")

                check_result = {
                    "tool": tool_name,
                    "param": param_name,
                    "expected": expected_value,
                    "actual": None,
                    "passed": False
                }

                # 查找对应的工具调用
                for tc in tool_calls:
                    tc_name = tc.get("function", {}).get("name", tc.get("name", ""))
                    if tc_name == tool_name:
                        args = tc.get("function", {}).get("arguments", {})
                        if isinstance(args, str):
                            import json
                            try:
                                args = json.loads(args)
                            except:
                                args = {}

                        actual = args.get(param_name)
                        check_result["actual"] = actual

                        if actual == expected_value:
                            check_result["passed"] = True
                        break

                if not check_result["passed"]:
                    score -= 10.0

                details["param_checks"].append(check_result)

        passed = score >= 60.0 and not details["missing_tools"]

        if not messages:
            message = "工具调用验证通过"
        else:
            message = "; ".join(messages)

        return ValidationResult(
            rule_type="tool_call_check",
            passed=passed,
            score=max(0.0, score),
            max_score=100.0,
            message=message,
            details=details
        )

    def _extract_tool_calls(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]]
    ) -> List[Dict]:
        """
        从输出中提取工具调用记录
        """
        tool_calls = []

        # 从parsed_output中提取
        if parsed_output:
            if "tool_calls" in parsed_output:
                return parsed_output["tool_calls"]

        # 从JSON中提取
        json_data = self._safe_json_parse(agent_output)
        if json_data and "tool_calls" in json_data:
            return json_data["tool_calls"]

        return tool_calls
