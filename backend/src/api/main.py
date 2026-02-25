"""
FastAPI 主应用入口
提供 API 服务
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 添加 src 到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import leaderboard, agent, evaluation, questions, variation, crawler, admin, submissions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时加载题库和数据库
    from db.question_repo import get_repository
    from db.database import get_database

    repo = get_repository()
    stats = repo.get_statistics()
    print(f"题库加载完成：{stats}")

    db = get_database()
    db_stats = db.get_statistics()
    print(f"数据库初始化完成：{db_stats}")

    yield

    # 关闭时清理资源
    print("应用关闭，清理资源")


app = FastAPI(
    title="保险智能体评测系统 API",
    description="Insurance Agent Benchmark API",
    version="1.1.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["排行榜"])
app.include_router(agent.router, prefix="/api/v1/agents", tags=["Agent 管理"])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["评测"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["题库"])
app.include_router(variation.router, prefix="/api/v1/variations", tags=["题目变异"])
app.include_router(crawler.router, prefix="/api/v1/crawler", tags=["数据爬虫"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理员后台"])
app.include_router(submissions.router, prefix="/api/v1/submissions", tags=["Agent 提交"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "保险智能体评测系统 API",
        "version": "1.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    from db.question_repo import get_repository
    repo = get_repository()
    stats = repo.get_statistics()

    return {
        "status": "healthy",
        "questions_loaded": stats.get("total_questions", 0)
    }
