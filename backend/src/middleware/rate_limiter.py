"""
限流中间件
防止 API 被恶意请求
"""

import time
from collections import defaultdict
from typing import Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """
    基于内存的限流器
    使用滑动窗口算法
    """

    def __init__(self, max_requests: int = 3, window_seconds: int = 86400):
        """
        初始化限流器

        Args:
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口（秒），默认 24 小时
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    def _cleanup(self, key: str):
        """清理过期的请求记录"""
        now = time.time()
        cutoff = now - self.window_seconds
        self.requests[key] = [t for t in self.requests[key] if t > cutoff]

    def is_allowed(self, key: str) -> bool:
        """
        检查请求是否允许

        Args:
            key: 限流键（如 IP 地址或邮箱）

        Returns:
            True 表示允许，False 表示被限流
        """
        self._cleanup(key)
        return len(self.requests[key]) < self.max_requests

    def record_request(self, key: str):
        """记录一次请求"""
        self._cleanup(key)
        self.requests[key].append(time.time())

    def get_remaining(self, key: str) -> int:
        """获取剩余请求次数"""
        self._cleanup(key)
        return max(0, self.max_requests - len(self.requests[key]))

    def get_reset_time(self, key: str) -> float:
        """获取限流重置时间（秒）"""
        if not self.requests[key]:
            return 0
        return self.requests[key][0] + self.window_seconds - time.time()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    限流中间件
    """

    def __init__(self, app, max_requests: int = 3, window_seconds: int = 86400):
        super().__init__(app)
        self.limiter = RateLimiter(max_requests, window_seconds)

    async def dispatch(self, request: Request, call_next):
        # 获取客户端 IP
        client_ip = request.client.host

        # 对于提交 API，使用 IP 作为限流键
        if request.url.path.startswith("/api/v1/submissions"):
            if request.method == "POST":
                if not self.limiter.is_allowed(client_ip):
                    return JSONResponse(
                        status_code=429,
                        content={
                            "success": False,
                            "error": "请求过于频繁，请 24 小时后再试",
                            "retry_after": int(self.limiter.get_reset_time(client_ip))
                        }
                    )
                self.limiter.record_request(client_ip)

        response = await call_next(request)
        return response


def rate_limit_check(ip_address: str, limiter: RateLimiter) -> Optional[JSONResponse]:
    """
    手动限流检查（用于在路由中使用）

    Args:
        ip_address: 客户端 IP
        limiter: 限流器实例

    Returns:
        如果超限返回错误响应，否则返回 None
    """
    if not limiter.is_allowed(ip_address):
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "请求过于频繁，请 24 小时后再试",
                "retry_after": int(limiter.get_reset_time(ip_address))
            }
        )
    return None
