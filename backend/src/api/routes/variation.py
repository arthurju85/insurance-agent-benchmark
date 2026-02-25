"""
题目变异相关API路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from ...db.variation_engine import VariationEngine, VariationConfig, create_variant_set
    from ...db.question_repo import get_repository
    from ...models.question import Question
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from db.variation_engine import VariationEngine, VariationConfig, create_variant_set
    from db.question_repo import get_repository
    from models.question import Question

router = APIRouter()


class VariationRequest(BaseModel):
    """生成变体请求"""
    question_id: str
    count: int = 3
    seed: Optional[int] = None
    enable_date_variation: bool = True
    enable_amount_variation: bool = True
    enable_name_replacement: bool = True


class VariationResponse(BaseModel):
    """变体生成响应"""
    original_id: str
    variations_generated: int
    variations: List[dict]


class BatchVariationRequest(BaseModel):
    """批量生成变体请求"""
    set_id: str
    variations_per_question: int = 3
    seed: Optional[int] = None


@router.post("/generate", response_model=VariationResponse)
async def generate_variations(request: VariationRequest):
    """
    为指定题目生成变体
    """
    # 获取原题
    repo = get_repository()
    question = repo.get_question(request.question_id)

    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 创建变异配置
    config = VariationConfig(
        enable_date_variation=request.enable_date_variation,
        enable_amount_variation=request.enable_amount_variation,
        enable_name_replacement=request.enable_name_replacement
    )

    # 生成变体
    engine = VariationEngine(config=config, seed=request.seed)
    variations = engine.generate_variations(question, count=request.count)

    return {
        "original_id": request.question_id,
        "variations_generated": len(variations),
        "variations": [v.model_dump() for v in variations]
    }


@router.post("/generate-set")
async def generate_set_variations(request: BatchVariationRequest):
    """
    为题集批量生成变体
    """
    repo = get_repository()
    question_set = repo.get_question_set(request.set_id)

    if not question_set:
        raise HTTPException(status_code=404, detail="题集不存在")

    # 获取所有题目
    questions = []
    for qid in question_set.questions:
        q = repo.get_question(qid)
        if q:
            questions.append(q)

    # 生成变体
    engine = VariationEngine(seed=request.seed)
    all_questions = engine.generate_question_set_variations(
        questions,
        variations_per_question=request.variations_per_question
    )

    # 统计
    originals = [q for q in all_questions if not q.is_variant]
    variants = [q for q in all_questions if q.is_variant]

    return {
        "set_id": request.set_id,
        "original_count": len(originals),
        "variant_count": len(variants),
        "total_count": len(all_questions),
        "variations_per_question": request.variations_per_question,
        "sample_variants": [v.model_dump() for v in variants[:3]]  # 返回前3个作为示例
    }


@router.get("/{question_id}/variants")
async def list_variants(question_id: str):
    """
    列出某道题的所有变体
    """
    repo = get_repository()

    # 加载所有题目
    all_questions = repo.load_all_questions()

    # 找到原题
    original = next((q for q in all_questions if q.question_id == question_id), None)
    if not original:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 找到所有变体
    variants = [
        q for q in all_questions
        if q.is_variant and q.parent_id == question_id
    ]

    return {
        "original": original.model_dump(),
        "variants": [v.model_dump() for v in variants],
        "total_variants": len(variants)
    }


@router.post("/preview")
async def preview_variation(question_id: str):
    """
    预览单道题的变体效果（不保存）
    """
    repo = get_repository()
    question = repo.get_question(question_id)

    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 生成一个预览变体
    engine = VariationEngine(seed=42)
    preview = engine.generate_variation(question, variation_index=1)

    return {
        "original": {
            "id": question.question_id,
            "content": question.content[:200] + "..." if len(question.content) > 200 else question.content,
            "ground_truth": question.ground_truth
        },
        "preview": {
            "id": preview.question_id,
            "content": preview.content[:200] + "..." if len(preview.content) > 200 else preview.content,
            "ground_truth": preview.ground_truth,
            "changes": {
                "dates_changed": True,
                "amounts_changed": True,
                "names_changed": True
            }
        }
    }
