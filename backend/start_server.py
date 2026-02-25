#!/usr/bin/env python3
"""
启动后端API服务
"""

import sys
import os

# 添加backend/src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 使用绝对导入修复
import api.routes.leaderboard
import api.routes.agent
import api.routes.evaluation
import api.routes.questions
import api.routes.variation
import api.routes.crawler
import api.routes.admin

# 重新导入main
from api.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
