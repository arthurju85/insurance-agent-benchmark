"""
管理员后台API路由
提供题库管理、评测监控、系统管理等功能
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from ..api.admin import (
        QuestionManager, EvaluationMonitor, SystemManager, SubmissionManager, get_admin_dashboard
    )
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from api.admin import (
        QuestionManager, EvaluationMonitor, SystemManager, SubmissionManager, get_admin_dashboard
    )

router = APIRouter()


# ========== 仪表盘 ==========

@router.get("/dashboard")
async def get_dashboard():
    """
    获取管理员仪表盘数据
    """
    return get_admin_dashboard()


# ========== 题目管理 ==========

class QuestionUpdateRequest(BaseModel):
    """题目更新请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    difficulty: Optional[str] = None
    score: Optional[float] = None
    tags: Optional[List[str]] = None


class CreateVariantRequest(BaseModel):
    """创建变体请求"""
    count: int = 3
    seed: Optional[int] = None


class ImportQuestionsRequest(BaseModel):
    """批量导入题目请求"""
    questions: List[dict]
    source: str = "import"


@router.get("/questions")
async def list_questions(
    dimension: Optional[str] = None,
    difficulty: Optional[str] = None,
    is_variant: Optional[bool] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    分页查询题目列表
    """
    manager = QuestionManager()
    return manager.list_questions(
        dimension=dimension,
        difficulty=difficulty,
        is_variant=is_variant,
        keyword=keyword,
        page=page,
        page_size=page_size
    )


@router.get("/questions/{question_id}")
async def get_question_detail(question_id: str):
    """
    获取题目详情
    """
    manager = QuestionManager()
    detail = manager.get_question_detail(question_id)

    if not detail:
        raise HTTPException(status_code=404, detail="题目不存在")

    return detail


@router.put("/questions/{question_id}")
async def update_question(question_id: str, request: QuestionUpdateRequest):
    """
    更新题目
    """
    manager = QuestionManager()
    success = manager.update_question(question_id, request.model_dump(exclude_unset=True))

    if not success:
        raise HTTPException(status_code=404, detail="题目不存在")

    return {"success": True, "message": "题目已更新"}


@router.delete("/questions/{question_id}")
async def delete_question(question_id: str):
    """
    删除题目（软删除）
    """
    manager = QuestionManager()
    success = manager.delete_question(question_id)

    if not success:
        raise HTTPException(status_code=404, detail="题目不存在")

    return {"success": True, "message": "题目已删除"}


@router.post("/questions/{question_id}/variants")
async def create_variants(question_id: str, request: CreateVariantRequest):
    """
    为题⽬生成变体
    """
    manager = QuestionManager()
    variant_ids = manager.create_variants(
        question_id,
        count=request.count,
        seed=request.seed
    )

    if not variant_ids:
        raise HTTPException(status_code=404, detail="题目不存在")

    return {
        "success": True,
        "parent_id": question_id,
        "variants_created": len(variant_ids),
        "variant_ids": variant_ids
    }


@router.post("/questions/import")
async def import_questions(request: ImportQuestionsRequest):
    """
    批量导入题目
    """
    manager = QuestionManager()
    result = manager.import_questions(request.questions, request.source)

    return {
        "success": True,
        **result
    }


# ========== 评测监控 ==========

@router.get("/evaluations/running")
async def get_running_evaluations():
    """
    获取正在运行的评测
    """
    monitor = EvaluationMonitor()
    return monitor.get_running_evaluations()


@router.get("/evaluations/recent")
async def get_recent_evaluations(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(50, ge=1, le=200)
):
    """
    获取最近的评测记录
    """
    monitor = EvaluationMonitor()
    return monitor.get_recent_evaluations(days=days, limit=limit)


@router.get("/evaluations/{evaluation_id}")
async def get_evaluation_detail(evaluation_id: str):
    """
    获取评测详情
    """
    monitor = EvaluationMonitor()
    detail = monitor.get_evaluation_detail(evaluation_id)

    if not detail:
        raise HTTPException(status_code=404, detail="评测不存在")

    return detail


@router.get("/agents/{agent_id}/performance")
async def get_agent_performance(
    agent_id: str,
    months: int = Query(6, ge=1, le=24)
):
    """
    获取Agent性能趋势
    """
    monitor = EvaluationMonitor()
    return monitor.get_agent_performance(agent_id, months)


@router.get("/leaderboard/history")
async def get_leaderboard_history(
    months: int = Query(12, ge=1, le=36)
):
    """
    获取排行榜历史
    """
    monitor = EvaluationMonitor()
    return monitor.get_leaderboard_history(months)


# ========== 系统管理 ==========

@router.get("/system/config")
async def get_system_config():
    """
    获取系统配置
    """
    manager = SystemManager()
    return manager.get_config()


@router.post("/system/backup")
async def backup_data():
    """
    执行数据备份
    """
    manager = SystemManager()
    backup_path = manager.backup_data()

    return {
        "success": True,
        "backup_path": backup_path
    }


@router.get("/system/stats")
async def get_system_stats():
    """
    获取系统统计信息
    """
    manager = SystemManager()
    stats = manager.get_dashboard_stats()

    return {
        "questions": {
            "total": stats.total_questions,
            "by_dimension": stats.questions_by_dimension,
            "by_difficulty": stats.questions_by_difficulty,
            "variants": stats.variant_questions
        },
        "evaluations": {
            "total": stats.total_evaluations,
            "this_week": stats.evaluations_this_week,
            "today": stats.evaluations_today,
            "avg_score": stats.avg_score
        },
        "agents": {
            "registered": stats.registered_agents,
            "active": stats.active_agents
        }
    }


# ========== Agent 提交审核 ==========

@router.get("/submissions")
async def list_submissions(
    status: Optional[str] = Query(None, description="筛选状态：pending/reviewing/approved/rejected"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    分页查询提交列表
    """
    manager = SubmissionManager()
    status_enum = None
    if status:
        try:
            from api.submissions import SubmissionStatus
            status_enum = SubmissionStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的状态值")

    return manager.list_submissions(status=status_enum, page=page, page_size=page_size)


@router.get("/submissions/{submission_id}")
async def get_submission_detail(submission_id: str):
    """
    获取提交详情
    """
    manager = SubmissionManager()
    detail = manager.get_submission_detail(submission_id)

    if not detail:
        raise HTTPException(status_code=404, detail="提交记录不存在")

    return detail


@router.put("/submissions/{submission_id}")
async def update_submission(
    submission_id: str,
    status: str = Query(..., description="目标状态"),
    review_notes: Optional[str] = Query(None, description="审核备注")
):
    """
    更新提交状态
    """
    manager = SubmissionManager()

    try:
        from api.submissions import SubmissionStatus
        status_enum = SubmissionStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态值")

    success = manager.update_submission_status(
        submission_id,
        status=status_enum,
        review_notes=review_notes
    )

    if not success:
        raise HTTPException(status_code=404, detail="提交记录不存在")

    return {"success": True, "new_status": status}


@router.delete("/submissions/{submission_id}")
async def delete_submission(submission_id: str):
    """
    删除提交记录
    """
    manager = SubmissionManager()

    # 先检查是否存在
    detail = manager.get_submission_detail(submission_id)
    if not detail:
        raise HTTPException(status_code=404, detail="提交记录不存在")

    from api.submissions import get_submissions_database
    db = get_submissions_database()
    db.delete_submission(submission_id)

    return {"success": True, "message": "删除成功"}


@router.get("/submissions/stats/summary")
async def get_submission_stats():
    """
    获取提交统计信息
    """
    manager = SubmissionManager()
    return manager.get_statistics()
