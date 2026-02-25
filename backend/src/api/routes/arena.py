"""
竞技场API路由
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import asyncio
import json

from models.agent import AgentConfig
from ..orchestrator import ArenaOrchestrator, ArenaConfig, run_arena_session
from ..customer_simulator import CustomerTag

router = APIRouter()

# 全局竞技场实例
_current_arena: ArenaOrchestrator = None


@router.get("/status")
async def get_arena_status():
    """
    获取竞技场当前状态
    """
    if _current_arena is None:
        return {
            "status": "idle",
            "message": "竞技场未启动"
        }

    return _current_arena.get_current_state()


@router.get("/leaderboard")
async def get_arena_leaderboard():
    """
    获取竞技场实时排行榜
    """
    if _current_arena is None:
        return {
            "status": "idle",
            "leaderboard": []
        }

    return {
        "status": _current_arena.status.value,
        "leaderboard": _current_arena.get_leaderboard()
    }


@router.post("/start")
async def start_arena(config: Dict[str, Any]):
    """
    启动竞技场

    请求体：
    {
        "agents": [...],  # Agent配置列表
        "duration_minutes": 60,  # 竞技时长
        "config": {...}  # 可选的竞技场配置
    }
    """
    global _current_arena

    if _current_arena and _current_arena.status.value == "running":
        return {
            "success": False,
            "message": "竞技场正在进行中"
        }

    # 解析Agent配置
    agents = [AgentConfig(**a) for a in config.get("agents", [])]

    if len(agents) < 2:
        return {
            "success": False,
            "message": "至少需要2个Agent参与"
        }

    # 创建配置
    arena_config = ArenaConfig(
        session_duration_hours=config.get("duration_minutes", 60) / 60,
        **config.get("config", {})
    )

    # 创建竞技场
    _current_arena = ArenaOrchestrator(agents, arena_config)

    # 后台启动
    asyncio.create_task(_current_arena.start())

    return {
        "success": True,
        "message": f"竞技场已启动，{len(agents)}个Agent参与",
        "session_id": f"arena_{asyncio.get_event_loop().time()}"
    }


@router.post("/stop")
async def stop_arena():
    """
    停止竞技场
    """
    global _current_arena

    if _current_arena is None:
        return {
            "success": False,
            "message": "竞技场未启动"
        }

    await _current_arena.stop()

    return {
        "success": True,
        "message": "竞技场已停止",
        "final_stats": _current_arena.get_leaderboard()
    }


@router.get("/events")
async def get_recent_events(limit: int = 50):
    """
    获取最近的事件
    """
    if _current_arena is None:
        return {"events": []}

    events = _current_arena.events[-limit:]

    return {
        "events": [
            {
                "type": e.event_type,
                "timestamp": e.timestamp,
                "data": e.data
            }
            for e in events
        ]
    }


@router.get("/time-series")
async def get_time_series_data():
    """
    获取时间序列数据（用于折线图）
    """
    if _current_arena is None:
        return {"data": []}

    return {
        "data": _current_arena.time_series_data
    }


@router.websocket("/ws")
async def arena_websocket(websocket: WebSocket):
    """
    WebSocket实时推送

    推送事件类型：
    - customer_generated: 新客户生成
    - deal_closed: 成交
    - compliance_violation: 合规违规
    - customer_lost: 客户流失
    - stats_update: 统计更新
    """
    await websocket.accept()

    if _current_arena is None:
        await websocket.send_json({
            "type": "error",
            "message": "竞技场未启动"
        })
        await websocket.close()
        return

    # 注册事件回调
    async def event_handler(event):
        try:
            await websocket.send_json({
                "type": event.event_type,
                "timestamp": event.timestamp,
                "data": event.data
            })
        except Exception:
            pass

    _current_arena.add_event_callback(event_handler)

    try:
        # 定期发送统计更新
        while _current_arena.status.value == "running":
            await websocket.send_json({
                "type": "stats_update",
                "data": _current_arena.get_current_state()
            })
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


@router.get("/customers")
async def get_active_customers():
    """
    获取活跃客户列表
    """
    if _current_arena is None:
        return {"customers": []}

    customers = []
    for cid, customer in _current_arena.customers.items():
        if customer.status.value in ["pending", "serving"]:
            customers.append(customer.to_dict())

    return {
        "customers": customers,
        "total": len(customers)
    }
