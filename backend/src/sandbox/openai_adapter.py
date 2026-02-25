"""
OpenAI API格式Agent适配器
支持OpenAI官方API及兼容格式的第三方API（Azure、DeepSeek等）
"""

import json
import time
from typing import AsyncIterator, Optional, Dict, Any, List

import httpx

from .adapter import AgentAdapter, AgentResponse, AgentError, AgentTimeoutError, AgentAPIError
from models.agent import AgentConfig


class OpenAIAdapter(AgentAdapter):
    """
    OpenAI API格式适配器
    支持：OpenAI官方、Azure OpenAI、DeepSeek、Moonshot等兼容OpenAI格式的API
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.client = httpx.AsyncClient(
            base_url=config.base_url or "https://api.openai.com/v1",
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=config.timeout
        )

    async def invoke(
        self,
        prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AgentResponse:
        """
        调用OpenAI API
        """
        messages = self._build_messages(prompt, system_prompt)

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
        }

        # 工具调用
        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice

        start_time = time.time()

        try:
            response = await self.client.post(
                "/chat/completions",
                json=payload
            )
            response.raise_for_status()
        except httpx.TimeoutException as e:
            raise AgentTimeoutError(self.config.timeout) from e
        except httpx.HTTPStatusError as e:
            raise AgentAPIError(e.response.status_code, e.response.text) from e
        except Exception as e:
            raise AgentError(f"请求失败: {str(e)}", error_type="request_failed") from e

        latency_ms = (time.time() - start_time) * 1000

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        return AgentResponse(
            content=message.get("content", ""),
            tool_calls=self._parse_tool_calls(message.get("tool_calls")),
            usage=data.get("usage"),
            latency_ms=latency_ms,
            finish_reason=choice.get("finish_reason"),
            raw_response=data if kwargs.get("return_raw") else None
        )

    async def invoke_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式调用
        """
        messages = self._build_messages(prompt, system_prompt)

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True
        }

        async with self.client.stream(
            "POST",
            "/chat/completions",
            json=payload
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                line = line.strip()
                if not line or line == "data: [DONE]":
                    continue

                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError):
                        continue

    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


class AzureOpenAIAdapter(OpenAIAdapter):
    """
    Azure OpenAI适配器
    Azure的API路径略有不同
    """

    def __init__(self, config: AgentConfig):
        # Azure使用api-key而非Authorization Bearer
        super().__init__(config)
        self.client.headers = {
            "api-key": config.api_key,
            "Content-Type": "application/json"
        }

    async def invoke(self, prompt: str, **kwargs) -> AgentResponse:
        """Azure OpenAI调用"""
        # Azure的路径格式: /openai/deployments/{deployment_name}/chat/completions
        messages = self._build_messages(prompt, kwargs.get("system_prompt"))

        payload = {
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        start_time = time.time()

        deployment = self.config.model  # Azure中使用deployment name作为model

        try:
            response = await self.client.post(
                f"/openai/deployments/{deployment}/chat/completions?api-version=2024-02-01",
                json=payload
            )
            response.raise_for_status()
        except httpx.TimeoutException as e:
            raise AgentTimeoutError(self.config.timeout) from e
        except httpx.HTTPStatusError as e:
            raise AgentAPIError(e.response.status_code, e.response.text) from e

        latency_ms = (time.time() - start_time) * 1000

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        return AgentResponse(
            content=message.get("content", ""),
            tool_calls=self._parse_tool_calls(message.get("tool_calls")),
            usage=data.get("usage"),
            latency_ms=latency_ms,
            finish_reason=choice.get("finish_reason"),
            raw_response=data if kwargs.get("return_raw") else None
        )
