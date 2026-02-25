#!/bin/bash

cd "$(dirname "$0")"

export PYTHONPATH=/Users/arthur/Apps/Projects/insurance-agent-benchmark/backend/src:$PYTHONPATH

echo "正在启动保险智能体评测系统后端服务..."
echo "Python路径: $PYTHONPATH"
echo ""

python3 -c "
import sys
sys.path.insert(0, '/Users/arthur/Apps/Projects/insurance-agent-benchmark/backend/src')

# 先预加载所有模块以检查导入
print('预加载模块...')
from db.database import get_database
from db.question_repo import get_repository
print('✅ 数据模块加载成功')

from api.main import app
print('✅ API模块加载成功')

print('')
print('启动服务器...')
"

if [ $? -eq 0 ]; then
    echo "模块检查通过，启动 uvicorn..."
    python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --app-dir /Users/arthur/Apps/Projects/insurance-agent-benchmark/backend/src
else
    echo "模块加载失败"
fi
