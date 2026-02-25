"""
Agent configuration and response models
支持多种Agent接入方式：OpenAI API、本地模型、Docker容器
"""

from enum import Enum
from typing import Optional, Dict, Any, List, AsyncIterator
from pydantic import BaseModel, Field, HttpUrl


class AgentType(str, Enum):
    """Agent类型"""
    OPENAI_API = "openai_api"          # OpenAI API格式
    OPENAI_COMPATIBLE = "openai_compatible"  # 兼容OpenAI格式的第三方API
    LOCAL_TRANSFORMERS = "local_transformers"  # 本地transformers模型
    VLLM = "vllm"                      # vLLM部署
    DOCKER = "docker"                  # Docker容器（预留）


class AgentConfig(BaseModel):
    """Agent配置模型"""
    id: str = Field(..., description="Agent唯一标识")
    name: str = Field(..., description="Agent显示名称")
    version: str = Field(default="1.0", description="版本号")
    vendor: str = Field(..., description="厂商名称")

    # 连接配置
    agent_type: AgentType = Field(default=AgentType.OPENAI_API)
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    model: str = Field(default="gpt-4", description="模型名称")

    # 生成参数
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=2048, ge=1)
    top_p: Optional[float] = Field(default=1.0, ge=0, le=1)

    # 系统提示词
    system_prompt: Optional[str] = Field(
        default=None,
        description="系统提示词，用于设定Agent角色和行为"
    )

    # 高级配置
    timeout: int = Field(default=60, description="单次调用超时时间（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: float = Field(default=1.0, description="重试间隔（秒）")

    # 工具配置（支持Function Calling）
    tools: Optional[List[Dict[str, Any]]] = Field(default=None)
    tool_choice: Optional[str] = Field(default=None)

    # 元数据
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "pingan-agent-v1",
                "name": "平安保险智能体",
                "version": "1.0.0",
                "vendor": "平安保险",
                "agent_type": "openai_api",
                "base_url": "https://api.example.com/v1",
                "api_key": "sk-...",
                "model": "gpt-4",
                "temperature": 0.3,
                "system_prompt": "你是一位专业的保险顾问..."
            }
        }


class ToolCall(BaseModel):
    """工具调用记录"""
    id: str
    type: str = "function"
    function: Dict[str, Any]  # {name: str, arguments: str}


class AgentResponse(BaseModel):
    """Agent响应模型"""
    content: str = Field(..., description="响应文本内容")
    tool_calls: Optional[List[ToolCall]] = Field(default=None)
    usage: Optional[Dict[str, int]] = Field(default=None)  # {prompt_tokens, completion_tokens, total_tokens}
    latency_ms: float = Field(..., description="响应延迟（毫秒）")
    finish_reason: Optional[str] = Field(default=None)
    raw_response: Optional[Dict[str, Any]] = Field(default=None, description="原始响应（调试用）")


class AgentStatus(BaseModel):
    """Agent状态"""
    id: str
    name: str
    status: str = Field(..., description="online/offline/error")
    last_ping: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)


# 预定义的保险Agent系统提示词模板
INSURANCE_AGENT_TEMPLATE = """你是一位专业的保险顾问，具备以下能力：
1. 深入理解各类保险产品（寿险、重疾险、医疗险、意外险、年金险等）
2. 熟悉保险条款，能准确解释免责条款和理赔条件
3. 具备风险评估能力，能根据客户情况推荐合适的保险方案
4. 严格遵守合规要求，不夸大收益，不隐瞒风险
5. 善于倾听客户需求，提供个性化的保险建议

在回答问题时，请：
- 使用专业但易懂的语言
- 如涉及具体产品，请说明条款细节
- 如涉及保费计算，请展示计算过程
- 如涉及理赔判断，请说明法律依据
- 严格遵守保险销售合规要求
"""


def create_agent_config(
    agent_id: str,
    name: str,
    vendor: str,
    base_url: str,
    api_key: str,
    model: str = "gpt-4",
    **kwargs
) -> AgentConfig:
    """快速创建Agent配置的工厂函数"""
    return AgentConfig(
        id=agent_id,
        name=name,
        vendor=vendor,
        base_url=base_url,
        api_key=api_key,
        model=model,
        system_prompt=INSURANCE_AGENT_TEMPLATE,
        **kwargs
    )
