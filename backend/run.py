"""
启动脚本
"""

import uvicorn
import os


def main():
    """启动API服务"""
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    print(f"启动保险智能体评测系统 API 服务...")
    print(f"访问地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")

    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    main()
