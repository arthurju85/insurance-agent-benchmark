"""
排行榜相关API路由
"""

from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel

import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from db.database import get_database
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from db.database import get_database

router = APIRouter()


class LeaderboardEntryResponse(BaseModel):
    """排行榜条目响应"""
    rank: int
    agent_id: str
    agent_name: str
    vendor: str
    version: str
    agent_type: str
    overall_score: float
    overall_percentage: float
    knowledge_score: float
    understanding_score: float
    reasoning_score: float
    compliance_score: float
    tools_score: float
    change: float
    evaluation_date: str


class LeaderboardResponse(BaseModel):
    """排行榜响应"""
    leaderboard_id: str
    name: str
    evaluation_date: str
    total_agents: int
    entries: List[LeaderboardEntryResponse]


@router.get("/current", response_model=LeaderboardResponse)
async def get_current_leaderboard(
    month: Optional[str] = None,
    agent_type: Optional[str] = None
):
    """
    获取当前排行榜
    如果数据库中有数据则返回，否则返回模拟数据
    """
    db = get_database()

    # 尝试从数据库获取
    if month:
        leaderboard = db.get_leaderboard(month)
    else:
        leaderboard = db.get_latest_leaderboard()

    if leaderboard:
        entries = leaderboard.get('entries', [])

        # 按agent_type筛选
        if agent_type and agent_type != "all":
            entries = [e for e in entries if e.get('agent_type') == agent_type]

        return {
            "leaderboard_id": leaderboard['leaderboard_id'],
            "name": leaderboard['name'],
            "evaluation_date": leaderboard['evaluation_date'],
            "total_agents": len(entries),
            "entries": entries
        }

    # 返回模拟数据（首次运行或数据库为空）
    mock_entries = [
        {
            "rank": 1,
            "agent_id": "pingan-a",
            "agent_name": "平安Agent-A",
            "vendor": "平安保险",
            "version": "v3.2",
            "agent_type": "insurer",
            "overall_score": 924.0,
            "overall_percentage": 92.4,
            "knowledge_score": 95.2,
            "understanding_score": 91.8,
            "reasoning_score": 88.5,
            "compliance_score": 94.1,
            "tools_score": 92.3,
            "change": 2.1,
            "evaluation_date": month or "2026-01"
        },
        {
            "rank": 2,
            "agent_id": "cpic-b",
            "agent_name": "太保Agent-B",
            "vendor": "太保",
            "version": "v2.8",
            "agent_type": "insurer",
            "overall_score": 897.0,
            "overall_percentage": 89.7,
            "knowledge_score": 91.3,
            "understanding_score": 90.2,
            "reasoning_score": 85.1,
            "compliance_score": 92.8,
            "tools_score": 89.1,
            "change": -0.5,
            "evaluation_date": month or "2026-01"
        }
    ]

    return {
        "leaderboard_id": "lb_2026_01",
        "name": "2026年1月排行榜",
        "evaluation_date": month or "2026-01",
        "total_agents": len(mock_entries),
        "entries": mock_entries
    }


@router.get("/history/{agent_id}")
async def get_agent_history(agent_id: str):
    """
    获取Agent历史表现
    """
    db = get_database()

    # 从数据库获取趋势
    trend = db.get_evaluation_trend(agent_id, months=6)

    if trend:
        return {
            "agent_id": agent_id,
            "history": [
                {"month": t['month'], "score": t['avg_score']}
                for t in trend
            ]
        }

    # 返回模拟数据
    return {
        "agent_id": agent_id,
        "history": [
            {"month": "2025-08", "score": 85.1},
            {"month": "2025-09", "score": 87.3},
            {"month": "2025-10", "score": 88.9},
            {"month": "2025-11", "score": 90.2},
            {"month": "2025-12", "score": 90.3},
            {"month": "2026-01", "score": 92.4}
        ]
    }
