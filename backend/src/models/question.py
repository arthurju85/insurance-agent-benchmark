"""
评测题目数据模型
支持多种题型：选择题、填空题、计算题、推理题、多轮对话
"""

from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from datetime import datetime


class QuestionDimension(str, Enum):
    """评测维度"""
    KNOWLEDGE = "knowledge"           # 保险业务知识
    UNDERSTANDING = "understanding"   # 客户需求理解
    REASONING = "reasoning"           # 专业推理能力
    COMPLIANCE = "compliance"         # 合规安全
    TOOLS = "tools"                   # 工具调用


class QuestionType(str, Enum):
    """题目类型"""
    SINGLE_CHOICE = "single_choice"   # 单选题
    MULTI_CHOICE = "multi_choice"     # 多选题
    FILL_BLANK = "fill_blank"         # 填空题
    CALCULATION = "calculation"       # 计算题
    CASE_ANALYSIS = "case_analysis"   # 案例分析
    MULTI_TURN = "multi_turn"         # 多轮对话
    TOOL_USE = "tool_use"             # 工具调用


class DifficultyLevel(str, Enum):
    """难度等级"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ValidationRule(BaseModel):
    """
    评分验证规则
    支持多种验证方式的组合
    """
    # 结论验证（适用于案例分析、推理题）
    conclusion_must_be_one_of: Optional[List[str]] = Field(
        default=None,
        description="结论必须是其中一个值"
    )
    conclusion_exact_match: Optional[str] = Field(
        default=None,
        description="结论必须完全匹配"
    )

    # 关键词验证
    must_contain_keywords: Optional[List[str]] = Field(
        default=None,
        description="必须包含的关键词列表"
    )
    must_contain_any: Optional[List[str]] = Field(
        default=None,
        description="必须包含至少一个关键词"
    )
    prohibited_keywords: Optional[List[str]] = Field(
        default=None,
        description="禁止出现的关键词（幻觉检测）"
    )

    # 数值验证（适用于计算题）
    numeric_path: Optional[str] = Field(
        default=None,
        description="数值字段的JSON路径，如'result.premium'"
    )
    numeric_tolerance: Optional[float] = Field(
        default=1.0,
        description="数值容忍误差（元或百分比）"
    )
    numeric_tolerance_type: str = Field(
        default="absolute",
        description="误差类型：absolute绝对值/relative相对值"
    )

    # 工具调用验证
    required_tools: Optional[List[str]] = Field(
        default=None,
        description="必须调用的工具列表"
    )
    tool_sequence_strict: bool = Field(
        default=False,
        description="是否严格要求工具调用顺序"
    )

    # 多轮对话验证
    required_states: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="必须达到的对话状态"
    )

    # 逻辑验证（复杂规则）
    custom_logic: Optional[str] = Field(
        default=None,
        description="自定义验证逻辑（Python表达式）"
    )


class ExpectedOutputSchema(BaseModel):
    """
    期望输出格式定义
    用于强制Agent输出结构化数据
    """
    schema_type: str = Field(default="json", description="输出格式：json/text")
    schema_definition: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema定义"
    )
    required_fields: List[str] = Field(
        default_factory=list,
        description="必须包含的字段"
    )
    output_instructions: Optional[str] = Field(
        default=None,
        description="输出格式说明（附加到prompt中）"
    )


class Question(BaseModel):
    """
    评测题目模型
    """
    # 基础信息
    question_id: str = Field(..., description="题目唯一标识")
    dimension: QuestionDimension = Field(..., description="所属维度")
    question_type: QuestionType = Field(..., description="题目类型")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)

    # 题目内容
    title: Optional[str] = Field(default=None, description="题目标题")
    description: Optional[str] = Field(default=None, description="题目描述")
    content: str = Field(..., description="题目正文（给Agent的输入）")
    context: Optional[str] = Field(
        default=None,
        description="上下文信息（如条款原文、案例背景）"
    )

    # 输出规范
    expected_schema: Optional[ExpectedOutputSchema] = Field(
        default=None,
        description="期望输出格式"
    )

    # 评分规则
    validation_rules: ValidationRule = Field(
        default_factory=ValidationRule,
        description="评分验证规则"
    )

    # 标准答案
    ground_truth: Optional[Dict[str, Any]] = Field(
        default=None,
        description="标准答案"
    )

    # 评分权重
    score: float = Field(default=100.0, description="本题满分")
    partial_score_rules: Optional[Dict[str, float]] = Field(
        default=None,
        description="部分得分规则，如{'conclusion': 60, 'reasoning': 40}"
    )

    # 元数据
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = Field(default=None, description="题目来源")
    version: str = Field(default="1.0")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(default=None)

    # 变异相关
    is_variant: bool = Field(default=False, description="是否为变异题")
    parent_id: Optional[str] = Field(default=None, description="母题ID")
    variant_seed: Optional[int] = Field(default=None, description="变异随机种子")

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "INS-REA-001",
                "dimension": "reasoning",
                "question_type": "case_analysis",
                "difficulty": "medium",
                "title": "等待期理赔判断",
                "content": "客户于2024年1月1日投保重疾险，2024年3月15日（非意外）确诊肺癌。请给出理赔结论。",
                "context": "条款：本合同生效之日起90日内为等待期，等待期内因非意外原因确诊重疾，退还保费，合同终止。",
                "expected_schema": {
                    "schema_type": "json",
                    "schema_definition": {
                        "type": "object",
                        "properties": {
                            "conclusion": {"type": "string", "enum": ["赔付", "拒赔", "退还保费"]},
                            "reasoning": {"type": "string"},
                            "legal_basis": {"type": "string"}
                        },
                        "required": ["conclusion", "reasoning"]
                    }
                },
                "validation_rules": {
                    "conclusion_must_be_one_of": ["退还保费", "拒赔"],
                    "must_contain_keywords": ["等待期", "90日"],
                    "numeric_path": "calculation_days",
                    "numeric_tolerance": 0
                },
                "ground_truth": {
                    "conclusion": "退还保费",
                    "calculation_days": 74,
                    "reasoning": "确诊时间在等待期（90日）内"
                },
                "score": 100,
                "tags": ["等待期", "重疾险", "理赔判断"]
            }
        }


class QuestionSet(BaseModel):
    """题目集合"""
    set_id: str = Field(..., description="集合ID")
    name: str = Field(..., description="集合名称")
    description: Optional[str] = Field(default=None)
    questions: List[str] = Field(..., description="题目ID列表")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # 统计信息
    total_score: float = Field(default=0.0)
    dimension_distribution: Optional[Dict[str, int]] = Field(default=None)
    difficulty_distribution: Optional[Dict[str, int]] = Field(default=None)


def create_calculation_question(
    question_id: str,
    content: str,
    expected_result: float,
    tolerance: float = 1.0,
    **kwargs
) -> Question:
    """快速创建计算题的工厂函数"""
    return Question(
        question_id=question_id,
        dimension=QuestionDimension.REASONING,
        question_type=QuestionType.CALCULATION,
        content=content,
        expected_schema=ExpectedOutputSchema(
            schema_type="json",
            schema_definition={
                "type": "object",
                "properties": {
                    "result": {"type": "number"},
                    "calculation_process": {"type": "string"}
                },
                "required": ["result"]
            },
            required_fields=["result"]
        ),
        validation_rules=ValidationRule(
            numeric_path="result",
            numeric_tolerance=tolerance,
            numeric_tolerance_type="absolute"
        ),
        ground_truth={"result": expected_result},
        **kwargs
    )


def create_compliance_question(
    question_id: str,
    user_input: str,
    must_avoid: List[str],
    must_include: Optional[List[str]] = None,
    **kwargs
) -> Question:
    """快速创建合规测试题的工厂函数"""
    return Question(
        question_id=question_id,
        dimension=QuestionDimension.COMPLIANCE,
        question_type=QuestionType.CASE_ANALYSIS,
        content=user_input,
        validation_rules=ValidationRule(
            prohibited_keywords=must_avoid,
            must_contain_keywords=must_include or []
        ),
        ground_truth={
            "should_refuse": True,
            "must_avoid": must_avoid,
            "must_include": must_include or []
        },
        **kwargs
    )
