"""
评分器基类
所有评分器都需要继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import re
import json

from models.evaluation import ValidationResult
from models.question import Question, ValidationRule


class BaseEvaluator(ABC):
    """
    评分器基类
    """

    def __init__(self, rule: ValidationRule):
        self.rule = rule

    @abstractmethod
    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        评分方法

        Args:
            agent_output: Agent原始输出文本
            parsed_output: 解析后的结构化输出（如果有）

        Returns:
            ValidationResult: 验证结果
        """
        pass

    def _safe_json_parse(self, text: str) -> Optional[Dict[str, Any]]:
        """
        安全解析JSON
        尝试从文本中提取JSON
        """
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON代码块
        patterns = [
            r'```json\s*(.*?)\s*```',  # Markdown JSON块
            r'```\s*(.*?)\s*```',      # 通用代码块
            r'\{.*\}',                  # 最外层大括号
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1) if pattern != r'\{.*\}' else match.group(0))
                except json.JSONDecodeError:
                    continue

        return None

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        根据路径获取嵌套字典值
        例如: "result.premium" -> data["result"]["premium"]
        """
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value


class CompositeEvaluator(BaseEvaluator):
    """
    组合评分器
    执行多个评分规则并汇总结果
    """

    def __init__(self, rule: ValidationRule, evaluators: List[BaseEvaluator]):
        super().__init__(rule)
        self.evaluators = evaluators

    def evaluate(
        self,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ) -> List[ValidationResult]:
        """
        执行所有评分器
        """
        results = []
        for evaluator in self.evaluators:
            result = evaluator.evaluate(agent_output, parsed_output)
            results.append(result)
        return results
