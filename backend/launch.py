#!/usr/bin/env python3
"""
简化版启动脚本 - 处理所有导入问题
"""

import sys
import os

# 添加必要的路径
backend_dir = '/Users/arthur/Apps/Projects/insurance-agent-benchmark/backend'
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, backend_dir)

print("=" * 60)
print("🚀 保险智能体评测系统 - 后端服务")
print("=" * 60)
print()

# 设置环境变量
os.environ['PYTHONPATH'] = src_dir + ':' + os.environ.get('PYTHONPATH', '')

# 尝试启动
try:
    print("正在加载数据模块...")
    from db.database import get_database
    from db.question_repo import get_repository
    print("✅ 数据模块加载成功")

    print("正在加载题库...")
    repo = get_repository()
    stats = repo.get_statistics()
    print(f"✅ 题库加载完成: {stats}")

    print("正在加载数据库...")
    db = get_database()
    db_stats = db.get_statistics()
    print(f"✅ 数据库初始化完成: {db_stats}")

    print()
    print("=" * 60)
    print("📝 系统状态")
    print("=" * 60)
    print(f"题目总数: {stats.get('total_questions', 0)}")
    print(f"评测总数: {db_stats.get('total_evaluations', 0)}")
    print(f"Agent数: {db_stats.get('total_agents', 0)}")
    print()
    print("=" * 60)
    print("✨ 所有模块加载成功！")
    print("=" * 60)
    print()

except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 启动服务器
print("正在启动 Uvicorn 服务器...")
print("访问地址: http://localhost:8000")
print("API文档: http://localhost:8000/docs")
print()

import uvicorn
uvicorn.run(
    "api.main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    app_dir=src_dir
)
