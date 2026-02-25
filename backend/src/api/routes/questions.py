"""
题库相关API路由
"""

from fastapi import APIRouter, HTTPException
from typing import List

import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from ...db.question_repo import get_repository
    from ...models.question import Question, QuestionSet
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from db.question_repo import get_repository
    from models.question import Question, QuestionSet

router = APIRouter()


@router.get("/stats")
async def get_question_stats():
    """
    获取题库统计信息
    """
    repo = get_repository()
    return repo.get_statistics()


@router.get("/sets", response_model=List[dict])
async def get_question_sets():
    """
    获取所有题目集合
    """
    repo = get_repository()
    repo.load_all_questions()

    return [
        {
            "set_id": s.set_id,
            "name": s.name,
            "description": s.description,
            "question_count": len(s.questions),
            "total_score": s.total_score
        }
        for s in repo._sets.values()
    ]


@router.get("/sets/{set_id}")
async def get_question_set(set_id: str):
    """
    获取题目集合详情
    """
    repo = get_repository()
    question_set = repo.get_question_set(set_id)

    if not question_set:
        raise HTTPException(status_code=404, detail="题目集合不存在")

    return question_set


@router.get("/questions", response_model=List[dict])
async def get_questions(
    dimension: str = None,
    difficulty: str = None,
    limit: int = 50
):
    """
    获取题目列表
    """
    repo = get_repository()

    if dimension:
        questions = repo.get_questions_by_dimension(dimension)
    elif difficulty:
        questions = repo.get_questions_by_difficulty(difficulty)
    else:
        questions = repo.load_all_questions()

    # 只返回基本信息
    return [
        {
            "question_id": q.question_id,
            "dimension": q.dimension,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
            "title": q.title,
            "score": q.score
        }
        for q in questions[:limit]
    ]


@router.get("/questions/{question_id}")
async def get_question(question_id: str):
    """
    获取题目详情
    """
    repo = get_repository()
    question = repo.get_question(question_id)

    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    return question
