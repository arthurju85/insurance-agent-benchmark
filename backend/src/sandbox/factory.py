"""
Agent 适配器工厂
统一管理 Agent 的创建和适配
"""

from typing import Type, Dict
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.agent import AgentConfig, AgentType
from sandbox.adapter import AgentAdapter
from sandbox.openai_adapter import OpenAIAdapter, AzureOpenAIAdapter
from sandbox.local_adapter import VLLMAdapter


class AdapterFactory:
    """
    Agent 适配器工厂
    统一管理 Agent 的创建和适配
    """

    # 适配器注册表
    _adapters: Dict[AgentType, Type[AgentAdapter]] = {
        AgentType.OPENAI_API: OpenAIAdapter,
        AgentType.OPENAI_COMPATIBLE: OpenAIAdapter,
        AgentType.VLLM: VLLMAdapter,
    }

    @classmethod
    def register_adapter(cls, agent_type: AgentType, adapter_class: Type[AgentAdapter]):
        """注册新的适配器"""
        cls._adapters[agent_type] = adapter_class

    @classmethod
    def get_adapter(cls, config: AgentConfig) -> AgentAdapter:
        """
        根据 Agent 配置获取对应的适配器实例

        Args:
            config: Agent 配置

        Returns:
            适配器实例
        """
        adapter_class = cls._adapters.get(config.agent_type)
        if adapter_class is None:
            # 默认使用 OpenAI 适配器
            adapter_class = OpenAIAdapter
        return adapter_class(config)

    @classmethod
    def list_adapters(cls) -> Dict[str, str]:
        """列出所有已注册的适配器"""
        return {
            type_name: adapter_class.__name__
            for type_name, adapter_class in cls._adapters.items()
        }


# 便捷函数
def get_agent_adapter(config: AgentConfig) -> AgentAdapter:
    """
    获取 Agent 适配器

    Args:
        config: Agent 配置

    Returns:
        适配器实例
    """
    return AdapterFactory.get_adapter(config)


async def test_agent_connection(config: AgentConfig) -> Dict:
    """
    测试 Agent 连接

    Args:
        config: Agent 配置

    Returns:
        测试结果
    """
    import time
    adapter = get_agent_adapter(config)
    start_time = time.time()

    try:
        # 发送简单测试消息
        response = await adapter.chat(
            messages=[{"role": "user", "content": "Hello, this is a connection test."}],
            tools=None
        )
        latency = (time.time() - start_time) * 1000

        return {
            "success": True,
            "latency_ms": round(latency, 2),
            "message": "Connection successful"
        }
    except Exception as e:
        return {
            "success": False,
            "latency_ms": 0,
            "error": str(e)
        }
