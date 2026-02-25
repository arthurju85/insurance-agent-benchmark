"""
Agent 提交 API 路由
处理用户/企业提交 Agent 参与排行榜或竞技场的申请
"""

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import re

import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from ..submissions import (
        get_submissions_database,
        AgentSubmission,
        SubmissionStatus,
        AgentType,
        ModelPlatform,
        RateLimitConfig,
        SubmissionCreateRequest,
        SubmissionUpdateRequest,
        SubmissionListResponse
    )
    from ..middleware.rate_limiter import RateLimiter, rate_limit_check
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from submissions import (
        get_submissions_database,
        AgentSubmission,
        SubmissionStatus,
        AgentType,
        ModelPlatform,
        RateLimitConfig,
        SubmissionCreateRequest,
        SubmissionUpdateRequest,
        SubmissionListResponse
    )
    from middleware.rate_limiter import RateLimiter, rate_limit_check

router = APIRouter()

# 限流器配置：24 小时内最多 3 次提交
_submission_limiter = RateLimiter(max_requests=3, window_seconds=86400)


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """验证手机号格式（支持国际格式）"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None


@router.post("/")
async def create_submission(request: Request, submission: SubmissionCreateRequest):
    """
    提交 Agent 申请

    用户/企业提交 Agent 参与排行榜或竞技场评测。
    提交后技术团队将在 5 个工作日内联络。

    **防攻击机制**:
    - 同一 IP 24 小时内最多提交 3 次
    - 同一邮箱 24 小时内最多提交 3 次
    - 需要验证码（可选，待集成）
    """
    # 获取客户端 IP
    client_ip = request.client.host

    # 限流检查
    rate_limit_error = rate_limit_check(client_ip, _submission_limiter)
    if rate_limit_error:
        return rate_limit_error

    # 验证邮箱格式
    if not validate_email(submission.email):
        raise HTTPException(status_code=400, detail="邮箱格式不正确")

    # 验证手机号格式
    if not validate_phone(submission.phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")

    # 验证码检查（预留接口）
    if submission.captcha_token:
        # TODO: 集成 reCAPTCHA 或其他验证码服务
        pass

    # 创建提交
    db = get_submissions_database()

    try:
        agent_submission = AgentSubmission(
            applicant_name=submission.applicant_name,
            company_name=submission.company_name,
            email=submission.email,
            phone=submission.phone,
            agent_name=submission.agent_name,
            agent_type=submission.agent_type,
            model_platform=submission.model_platform,
            api_endpoint=submission.api_endpoint,
            notes=submission.notes
        )

        submission_id = db.create_submission(agent_submission, ip_address=client_ip)

        # 记录限流
        _submission_limiter.record_request(client_ip)
        db.record_rate_limit(client_ip, submission.email)

        return {
            "success": True,
            "submission_id": submission_id,
            "message": "提交成功，技术团队将在 5 个工作日内联络您",
            "remaining": _submission_limiter.get_remaining(client_ip)
        }

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=400,
                detail="该 Agent 已提交过，请勿重复提交"
            )
        raise


@router.get("/")
async def list_submissions(
    status: Optional[str] = Query(None, description="筛选状态：pending/reviewing/approved/rejected"),
    limit: int = Query(100, ge=1, le=500, description="返回数量限制")
):
    """
    获取提交列表（管理员使用）

    支持按状态筛选，默认返回所有提交。
    """
    db = get_submissions_database()

    status_enum = None
    if status:
        try:
            status_enum = SubmissionStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的状态值，可选：pending, reviewing, approved, rejected"
            )

    submissions = db.get_submissions(status=status_enum, limit=limit)

    return {
        "total": len(submissions),
        "submissions": [
            {
                "id": s.id,
                "applicant_name": s.applicant_name,
                "company_name": s.company_name,
                "email": s.email,
                "phone": s.phone,
                "agent_name": s.agent_name,
                "agent_type": s.agent_type.value,
                "model_platform": s.model_platform.value,
                "api_endpoint": s.api_endpoint,
                "status": s.status.value,
                "submitted_at": s.submitted_at,
                "reviewed_at": s.reviewed_at,
                "reviewed_by": s.reviewed_by,
                "review_notes": s.review_notes
            }
            for s in submissions
        ]
    }


@router.get("/{submission_id}")
async def get_submission(submission_id: str):
    """
    获取提交详情（管理员使用）
    """
    db = get_submissions_database()
    submission = db.get_submission(submission_id)

    if not submission:
        raise HTTPException(status_code=404, detail="提交记录不存在")

    return {
        "id": submission.id,
        "applicant_name": submission.applicant_name,
        "company_name": submission.company_name,
        "email": submission.email,
        "phone": submission.phone,
        "agent_name": submission.agent_name,
        "agent_type": submission.agent_type.value,
        "model_platform": submission.model_platform.value,
        "api_endpoint": submission.api_endpoint,
        "notes": submission.notes,
        "status": submission.status.value,
        "submitted_at": submission.submitted_at,
        "reviewed_at": submission.reviewed_at,
        "reviewed_by": submission.reviewed_by,
        "review_notes": submission.review_notes,
        "ip_address": submission.ip_address
    }


@router.put("/{submission_id}")
async def update_submission(submission_id: str, request: SubmissionUpdateRequest):
    """
    更新提交状态（管理员使用）

    审核流程：
    - pending → reviewing: 开始审核
    - reviewing → approved: 审核通过
    - reviewing → rejected: 审核拒绝
    """
    db = get_submissions_database()

    # 检查提交是否存在
    existing = db.get_submission(submission_id)
    if not existing:
        raise HTTPException(status_code=404, detail="提交记录不存在")

    # 更新状态
    success = db.update_submission(
        submission_id,
        status=request.status,
        review_notes=request.review_notes
    )

    if not success:
        raise HTTPException(status_code=400, detail="更新失败")

    return {
        "success": True,
        "submission_id": submission_id,
        "new_status": request.status.value if request.status else existing.status.value,
        "message": "更新成功"
    }


@router.delete("/{submission_id}")
async def delete_submission(submission_id: str):
    """
    删除提交记录（管理员使用）
    """
    db = get_submissions_database()

    success = db.delete_submission(submission_id)

    if not success:
        raise HTTPException(status_code=404, detail="提交记录不存在")

    return {
        "success": True,
        "message": "删除成功"
    }


@router.get("/stats/summary")
async def get_submission_stats():
    """
    获取提交统计信息（管理员使用）
    """
    db = get_submissions_database()
    stats = db.get_statistics()

    return stats


@router.get("/rate-limit/remaining")
async def get_rate_limit_remaining(request: Request):
    """
    获取当前 IP 的剩余提交次数
    """
    client_ip = request.client.host
    db = get_submissions_database()

    # 从数据库获取更准确的限流信息
    remaining = db.get_rate_limit_remaining(client_ip, "")

    return remaining
