"""
评分器工厂
根据题目类型自动选择合适的评分器
"""

from typing import List, Type, Dict, Any, Optional

from .base import BaseEvaluator
from .keyword_checker import KeywordChecker, RegexChecker
from .numeric_checker import NumericChecker, MultiNumericChecker
from .schema_validator import SchemaValidator, FieldTypeChecker
from .logic_engine import ConclusionChecker, LogicRuleEngine
from .tool_call_checker import ToolCallChecker

from models.question import Question, QuestionType, QuestionDimension, ValidationRule


class EvaluatorFactory:
    """
    评分器工厂
    根据题目配置自动创建评分器组合
    """

    @classmethod
    def create_evaluators(cls, question: Question) -> List[BaseEvaluator]:
        """
        根据题目创建评分器列表

        Args:
            question: 评测题目

        Returns:
            List[BaseEvaluator]: 评分器列表
        """
        evaluators = []
        rule = question.validation_rules

        # 1. Schema验证（如果配置了输出格式）
        if question.expected_schema:
            evaluators.append(SchemaValidator(
                rule=rule,
                schema=question.expected_schema.schema_definition,
                required_fields=question.expected_schema.required_fields
            ))

        # 2. 关键词检查
        if rule.must_contain_keywords or rule.prohibited_keywords or rule.must_contain_any:
            evaluators.append(KeywordChecker(
                rule=rule,
                must_contain=rule.must_contain_keywords,
                must_contain_any=rule.must_contain_any,
                prohibited=rule.prohibited_keywords
            ))

        # 3. 结论验证
        if rule.conclusion_exact_match or rule.conclusion_must_be_one_of:
            evaluators.append(ConclusionChecker(
                rule=rule,
                expected_conclusion=rule.conclusion_exact_match,
                allowed_conclusions=rule.conclusion_must_be_one_of
            ))

        # 4. 数值检查
        if rule.numeric_path:
            if question.ground_truth and "result" in question.ground_truth:
                evaluators.append(NumericChecker(
                    rule=rule,
                    expected_value=question.ground_truth.get("result"),
                    tolerance=rule.numeric_tolerance,
                    tolerance_type=rule.numeric_tolerance_type,
                    numeric_path=rule.numeric_path
                ))

        # 5. 工具调用检查
        if rule.required_tools:
            evaluators.append(ToolCallChecker(
                rule=rule,
                required_tools=rule.required_tools,
                strict_sequence=rule.tool_sequence_strict
            ))

        # 6. 合规检查（合规类题目默认添加）
        if question.dimension == QuestionDimension.COMPLIANCE:
            evaluators.append(ComplianceChecker(rule=rule))

        # 如果没有配置任何评分器，默认使用关键词检查
        if not evaluators:
            evaluators.append(KeywordChecker(rule=rule))

        return evaluators

    @classmethod
    def evaluate_question(
        cls,
        question: Question,
        agent_output: str,
        parsed_output: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        对单题进行评分

        Returns:
            {
                "score": float,
                "max_score": float,
                "passed": bool,
                "validation_results": List[ValidationResult],
                "details": Dict
            }
        """
        evaluators = cls.create_evaluators(question)

        validation_results = []
        total_score = 0.0
        total_weight = 0.0

        for evaluator in evaluators:
            # 对于ToolCallChecker，传入tool_calls
            if isinstance(evaluator, ToolCallChecker):
                result = evaluator.evaluate(agent_output, parsed_output, tool_calls)
            else:
                result = evaluator.evaluate(agent_output, parsed_output)

            validation_results.append(result)
            total_score += result.score
            total_weight += result.max_score

        # 计算最终得分
        if total_weight > 0:
            final_score = (total_score / total_weight) * question.score
        else:
            final_score = 0.0

        # 判断是否通过（所有验证都通过才算通过）
        passed = all(r.passed for r in validation_results)

        return {
            "score": final_score,
            "max_score": question.score,
            "passed": passed,
            "validation_results": validation_results,
            "details": {
                "evaluator_count": len(evaluators),
                "passed_count": sum(1 for r in validation_results if r.passed),
                "failed_count": sum(1 for r in validation_results if not r.passed)
            }
        }
