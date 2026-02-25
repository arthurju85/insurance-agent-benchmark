"""
Agent 管理相关 API 路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.agent import AgentConfig, AgentStatus, AgentType
from sandbox.factory import test_agent_connection
from db.database import get_database

router = APIRouter()
