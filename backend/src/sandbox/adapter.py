"""
Agent 适配基类
定义统一的 Agent 调用接口
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict, Any, List
import sys
import os
import time
import asyncio

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.agent import AgentConfig, AgentResponse, ToolCall


class AgentError(Exception):
    """Agent 调用基础异常"""
    pass


class AgentTimeoutError(AgentError):
    """Agent 调用超时"""
    pass


class AgentAPIError(AgentError):
    """Agent API 错误"""
    pass


class AgentAdapter(ABC):
    """
    Agent 适配器基类
    所有具体 Agent 实现都需要继承此类
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self._session: Optional[Any] = None

    @abstractmethod
    async def invoke(
        self,
        prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs
    ) -> AgentResponse:
        """
        调用 Agent

        Args:
            prompt: 输入提示
            tools: 可用工具列表
            tool_choice: 工具选择策略
            **kwargs: 其他参数

        Returns:
            Agent 响应
        """
        pass

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AgentResponse:
        """
        多轮对话

        Args:
            messages: 对话消息列表
            tools: 可用工具列表
            **kwargs: 其他参数

        Returns:
            Agent 响应
        """
        # 默认实现：将消息转换为 prompt
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        return await self.invoke(last_user_msg, tools, **kwargs)

    async def close(self):
        """关闭会话"""
        if self._session:
            await self._session.close()
            self._session = None
