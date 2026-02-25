"""
评测结果数据模型
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class EvaluationStatus(str, Enum):
    """评测状态"""
    PENDING = "pending"           # 等待执行
    RUNNING = "running"          # 执行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 执行失败
    TIMEOUT = "timeout"          # 超时


class ValidationResult(BaseModel):
    """单个验证项的结果"""
    rule_type: str = Field(..., description="验证规则类型")
    passed: bool = Field(..., description="是否通过")
    score: float = Field(..., description="该项得分")
    max_score: float = Field(..., description="该项满分")
    message: Optional[str] = Field(default=None, description="验证详情")
    details: Optional[Dict[str, Any]] = Field(default=None, description="详细数据")


class QuestionResult(BaseModel):
    """单题评测结果"""
    question_id: str = Field(..., description="题目ID")
    dimension: str = Field(..., description="所属维度")

    # Agent输出
    agent_output: str = Field(..., description="Agent原始输出")
    parsed_output: Optional[Dict[str, Any]] = Field(
        default=None,
        description="解析后的结构化输出"
    )
    latency_ms: float = Field(..., description="响应延迟")

    # 评分结果
    score: float = Field(..., description="本题得分")
    max_score: float = Field(..., description="本题满分")
    validation_results: List[ValidationResult] = Field(
        default_factory=list,
        description="各项验证结果"
    )

    # 工具调用记录（如适用）
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None)

    # 执行信息
    status: EvaluationStatus = Field(default=EvaluationStatus.COMPLETED)
    error_message: Optional[str] = Field(default=None)
    executed_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class DimensionScore(BaseModel):
    """维度得分"""
    dimension: str = Field(..., description="维度名称")
    score: float = Field(..., description="维度得分")
    max_score: float = Field(..., description="维度满分")
    percentage: float = Field(..., description="百分比得分")
    question_count: int = Field(..., description="题目数量")


class EvaluationResult(BaseModel):
    """
    完整评测结果
    """
    # 基本信息
    evaluation_id: str = Field(..., description="评测ID")
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent名称")
    question_set_id: str = Field(..., description="题目集合ID")

    # 状态
    status: EvaluationStatus = Field(default=EvaluationStatus.PENDING)
    progress: float = Field(default=0.0, ge=0, le=100, description="进度百分比")

    # 详细结果
    question_results: List[QuestionResult] = Field(default_factory=list)

    # 汇总得分
    total_score: float = Field(default=0.0)
    max_total_score: float = Field(default=0.0)
    overall_percentage: float = Field(default=0.0)

    # 各维度得分
    dimension_scores: List[DimensionScore] = Field(default_factory=list)

    # 统计信息
    total_questions: int = Field(default=0)
    completed_questions: int = Field(default=0)
    failed_questions: int = Field(default=0)
    timeout_questions: int = Field(default=0)

    # 耗时统计
    total_latency_ms: float = Field(default=0.0)
    avg_latency_ms: float = Field(default=0.0)

    # 时间戳
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = Field(default=None)
    completed_at: Optional[str] = Field(default=None)

    # 元数据
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(default=None)

    def calculate_summary(self):
        """计算汇总统计"""
        if not self.question_results:
            return

        self.total_questions = len(self.question_results)
        self.completed_questions = sum(
            1 for r in self.question_results
            if r.status == EvaluationStatus.COMPLETED
        )
        self.failed_questions = sum(
            1 for r in self.question_results
            if r.status == EvaluationStatus.FAILED
        )
        self.timeout_questions = sum(
            1 for r in self.question_results
            if r.status == EvaluationStatus.TIMEOUT
        )

        self.total_score = sum(r.score for r in self.question_results)
        self.max_total_score = sum(r.max_score for r in self.question_results)
        self.overall_percentage = (
            self.total_score / self.max_total_score * 100
            if self.max_total_score > 0 else 0
        )

        self.total_latency_ms = sum(r.latency_ms for r in self.question_results)
        self.avg_latency_ms = (
            self.total_latency_ms / self.completed_questions
            if self.completed_questions > 0 else 0
        )

        # 计算各维度得分
        dimension_map = {}
        for r in self.question_results:
            dim = r.dimension
            if dim not in dimension_map:
                dimension_map[dim] = {"score": 0, "max": 0, "count": 0}
            dimension_map[dim]["score"] += r.score
            dimension_map[dim]["max"] += r.max_score
            dimension_map[dim]["count"] += 1

        self.dimension_scores = [
            DimensionScore(
                dimension=dim,
                score=data["score"],
                max_score=data["max"],
                percentage=data["score"] / data["max"] * 100 if data["max"] > 0 else 0,
                question_count=data["count"]
            )
            for dim, data in dimension_map.items()
        ]


class LeaderboardEntry(BaseModel):
    """排行榜条目"""
    rank: int = Field(..., description="排名")
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent名称")
    vendor: str = Field(..., description="厂商")
    version: str = Field(..., description="版本")
    agent_type: str = Field(..., description="Agent类型")

    # 得分
    overall_score: float = Field(..., description="综合得分")
    overall_percentage: float = Field(..., description="综合百分比")

    # 维度得分
    knowledge_score: float = Field(default=0.0)
    understanding_score: float = Field(default=0.0)
    reasoning_score: float = Field(default=0.0)
    compliance_score: float = Field(default=0.0)
    tools_score: float = Field(default=0.0)

    # 趋势
    change: float = Field(default=0.0, description="环比变化")
    history: List[float] = Field(default_factory=list, description="历史得分")

    # 统计
    total_evaluations: int = Field(default=1)
    avg_latency_ms: float = Field(default=0.0)

    # 时间
    evaluation_date: str = Field(..., description="评测日期")


class Leaderboard(BaseModel):
    """排行榜"""
    leaderboard_id: str = Field(..., description="榜单ID")
    name: str = Field(..., description="榜单名称")
    description: Optional[str] = Field(default=None)
    question_set_id: str = Field(..., description="题目集合ID")
    evaluation_date: str = Field(..., description="评测日期")

    entries: List[LeaderboardEntry] = Field(default_factory=list)

    # 统计
    total_agents: int = Field(default=0)
    dimension_weights: Optional[Dict[str, float]] = Field(default=None)

    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
