"""
本地模型适配器
支持通过transformers或vLLM加载的本地模型
"""

import time
from typing import AsyncIterator, Optional, Dict, Any, List

from .adapter import AgentAdapter, AgentResponse, AgentError
from models.agent import AgentConfig


class LocalModelAdapter(AgentAdapter):
    """
    本地模型适配器（预留接口）
    实际实现需要根据具体的本地模型部署方式
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._model = None
        self._tokenizer = None

    async def load_model(self):
        """
        加载本地模型
        子类需要实现具体的加载逻辑
        """
        raise NotImplementedError("子类必须实现load_model方法")

    async def invoke(
        self,
        prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs
    ) -> AgentResponse:
        """
        调用本地模型
        """
        if self._model is None:
            await self.load_model()

        # 构建提示词
        full_prompt = self._build_prompt(prompt)

        start_time = time.time()

        try:
            # 子类实现具体的推理逻辑
            output = await self._generate(full_prompt, **kwargs)
        except Exception as e:
            raise AgentError(f"本地模型推理失败: {str(e)}", error_type="inference_failed") from e

        latency_ms = (time.time() - start_time) * 1000

        return AgentResponse(
            content=output,
            latency_ms=latency_ms,
            finish_reason="stop"
        )

    def _build_prompt(self, user_prompt: str) -> str:
        """
        构建完整提示词（包含system prompt）
        """
        if self.config.system_prompt:
            return f"{self.config.system_prompt}\n\n用户：{user_prompt}\n\n助手："
        return user_prompt

    async def _generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本（子类实现）
        """
        raise NotImplementedError("子类必须实现_generate方法")

    async def invoke_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """
        流式生成（子类实现）
        """
        raise NotImplementedError("子类必须实现invoke_stream方法")

    async def close(self):
        """释放模型资源"""
        self._model = None
        self._tokenizer = None


class VLLMAdapter(LocalModelAdapter):
    """
    vLLM部署的模型适配器
    通过HTTP API调用vLLM服务
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        import httpx
        self.client = httpx.AsyncClient(
            base_url=config.base_url or "http://localhost:8000/v1",
            timeout=config.timeout
        )

    async def load_model(self):
        """vLLM通过服务启动时加载，无需显式加载"""
        pass

    async def _generate(self, prompt: str, **kwargs) -> str:
        """调用vLLM API"""
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
        }

        response = await self.client.post("/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["text"]

    async def invoke(self, prompt: str, **kwargs) -> AgentResponse:
        """
        适配vLLM的API格式（与OpenAI略有不同）
        """
        messages = self._build_messages(prompt, kwargs.get("system_prompt"))

        # vLLM支持OpenAI格式的chat completions
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        start_time = time.time()

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()

        latency_ms = (time.time() - start_time) * 1000

        data = response.json()
        choice = data["choices"][0]

        return AgentResponse(
            content=choice["message"]["content"],
            usage=data.get("usage"),
            latency_ms=latency_ms,
            finish_reason=choice.get("finish_reason"),
            raw_response=data if kwargs.get("return_raw") else None
        )

    async def invoke_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """流式调用vLLM"""
        messages = self._build_messages(prompt, kwargs.get("system_prompt"))

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": True
        }

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()

            import json
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
        await self.client.aclose()
