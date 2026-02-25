"""
评测相关API路由
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from models.agent import AgentConfig
    from models.evaluation import EvaluationResult
    from pipeline.evaluator import evaluate_agent
    from ...db.question_repo import get_repository
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from models.agent import AgentConfig
    from models.evaluation import EvaluationResult
    from pipeline.evaluator import evaluate_agent
    from db.question_repo import get_repository

router = APIRouter()


class EvaluateRequest(BaseModel):
    """评测请求"""
    agent_config: AgentConfig
    question_set_id: Optional[str] = "benchmark_v1"
    question_ids: Optional[List[str]] = None
    concurrency: int = 3


class EvaluateResponse(BaseModel):
    """评测响应"""
    evaluation_id: str
    status: str
    result: Optional[EvaluationResult] = None


@router.post("/run", response_model=EvaluateResponse)
async def run_evaluation(request: EvaluateRequest):
    """
    执行评测
    """
    try:
        # 获取题目
        repo = get_repository()

        if request.question_ids:
            questions = [
                repo.get_question(qid)
                for qid in request.question_ids
            ]
            questions = [q for q in questions if q is not None]
        else:
            question_set = repo.get_question_set(request.question_set_id)
            if not question_set:
                raise HTTPException(status_code=404, detail="题目集合不存在")

            questions = [
                repo.get_question(qid)
                for qid in question_set.questions
            ]
            questions = [q for q in questions if q is not None]

        if not questions:
            raise HTTPException(status_code=404, detail="未找到题目")

        # 执行评测
        result = await evaluate_agent(
            agent_config=request.agent_config,
            questions=questions,
            concurrency=request.concurrency
        )

        return EvaluateResponse(
            evaluation_id=result.evaluation_id,
            status=result.status,
            result=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{evaluation_id}")
async def get_evaluation_result(evaluation_id: str):
    """
    获取评测结果
    """
    # TODO: 从数据库获取历史结果
    return {"message": "功能开发中", "evaluation_id": evaluation_id}
