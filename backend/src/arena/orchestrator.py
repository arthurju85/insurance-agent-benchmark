"""
竞技调度引擎
管理Arena的完整流程：客户生成、Agent分配、对战、计分
"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .customer_simulator import (
    VirtualCustomer, CustomerStatus, CustomerTag,
    generate_random_customer, get_customer_by_tag
)
from ..models.agent import AgentConfig


class ArenaStatus(str, Enum):
    """竞技场状态"""
    IDLE = "idle"              # 空闲
    PREPARING = "preparing"    # 准备中
    RUNNING = "running"        # 进行中
    PAUSED = "paused"          # 暂停
    FINISHED = "finished"      # 已结束


@dataclass
class ArenaConfig:
    """竞技场配置"""
    session_duration_hours: float = 24.0           # 竞技时长
    customer_generation_interval: tuple = (30, 120)  # 客户生成间隔（秒）
    max_concurrent_customers: int = 20             # 最大并发客户数
    max_agents_per_customer: int = 3               # 每个客户最多几个Agent竞争
    enable_competition: bool = True                # 是否启用竞争模式

    # 计分权重
    gmv_weight: float = 0.5                        # 成交额权重
    conversion_weight: float = 0.3                 # 转化率权重
    compliance_weight: float = 0.2                 # 合规分权重


@dataclass
class AgentArenaStats:
    """Agent在竞技场中的统计"""
    agent_id: str
    agent_name: str

    # 业绩
    total_gmv: float = 0.0
    deal_count: int = 0
    reject_count: int = 0
    lost_count: int = 0

    # 客户
    customers_served: int = 0
    customers_converted: int = 0

    # 合规
    compliance_violations: int = 0
    compliance_score: float = 100.0

    # 效率
    avg_response_time: float = 0.0
    total_response_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        conversion_rate = (
            self.customers_converted / self.customers_served * 100
            if self.customers_served > 0 else 0
        )

        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "total_gmv": self.total_gmv,
            "deal_count": self.deal_count,
            "reject_count": self.reject_count,
            "lost_count": self.lost_count,
            "customers_served": self.customers_served,
            "customers_converted": self.customers_converted,
            "conversion_rate": round(conversion_rate, 1),
            "compliance_score": round(self.compliance_score, 1),
            "avg_response_time": round(self.avg_response_time / 1000, 2) if self.avg_response_time else 0
        }


@dataclass
class ArenaEvent:
    """竞技场事件"""
    event_type: str  # "customer_generated", "deal_closed", "reject", "lost", "compliance_violation"
    timestamp: str
    data: Dict[str, Any]


class ArenaOrchestrator:
    """
    竞技调度器
    管理整个竞技场的生命周期
    """

    def __init__(
        self,
        agents: List[AgentConfig],
        config: ArenaConfig = None
    ):
        self.agents = agents
        self.config = config or ArenaConfig()
        self.status = ArenaStatus.IDLE

        # 客户池
        self.customers: Dict[str, VirtualCustomer] = {}
        self.pending_customers: List[str] = []
        self.serving_customers: Dict[str, List[str]] = {}  # agent_id -> [customer_ids]

        # Agent统计
        self.agent_stats: Dict[str, AgentArenaStats] = {
            agent.id: AgentArenaStats(agent_id=agent.id, agent_name=agent.name)
            for agent in agents
        }

        # 事件历史
        self.events: List[ArenaEvent] = []

        # 时间序列数据（用于图表）
        self.time_series_data: List[Dict[str, Any]] = []

        # 回调
        self.event_callbacks: List[Callable] = []

        # 任务控制
        self._tasks: List[asyncio.Task] = []
        self._stop_event = asyncio.Event()

    def add_event_callback(self, callback: Callable):
        """添加事件回调"""
        self.event_callbacks.append(callback)

    async def start(self):
        """启动竞技场"""
        if self.status == ArenaStatus.RUNNING:
            return

        self.status = ArenaStatus.RUNNING
        self.start_time = datetime.now()
        self._stop_event.clear()

        print(f"🏆 Arena started with {len(self.agents)} agents")
        print(f"   Duration: {self.config.session_duration_hours} hours")
        print(f"   Max concurrent customers: {self.config.max_concurrent_customers}")

        # 启动任务
        self._tasks = [
            asyncio.create_task(self._customer_generation_loop()),
            asyncio.create_task(self._matchmaking_loop()),
            asyncio.create_task(self._time_series_recorder()),
            asyncio.create_task(self._session_timer())
        ]

    async def stop(self):
        """停止竞技场"""
        self.status = ArenaStatus.FINISHED
        self._stop_event.set()

        # 取消所有任务
        for task in self._tasks:
            task.cancel()

        await asyncio.gather(*self._tasks, return_exceptions=True)

        print("🏆 Arena finished")
        self._print_final_stats()

    async def _customer_generation_loop(self):
        """客户生成循环"""
        customer_counter = 0

        while not self._stop_event.is_set():
            try:
                # 检查是否达到最大客户数
                if len(self.customers) >= self.config.max_concurrent_customers:
                    await asyncio.sleep(5)
                    continue

                # 生成随机间隔
                interval = random.randint(
                    self.config.customer_generation_interval[0],
                    self.config.customer_generation_interval[1]
                )

                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=interval
                )
                continue  # 如果收到停止信号

            except asyncio.TimeoutError:
                pass  # 正常超时，继续生成客户

            # 生成客户
            customer_counter += 1
            session_id = f"S{datetime.now().strftime('%H%M%S')}_{customer_counter:04d}"
            customer = generate_random_customer(session_id)

            self.customers[session_id] = customer
            self.pending_customers.append(session_id)

            # 记录事件
            self._emit_event("customer_generated", {
                "customer_id": session_id,
                "customer": customer.to_dict()
            })

            print(f"👤 New customer: {customer.persona.label} ({session_id})")

    async def _matchmaking_loop(self):
        """匹配循环：将客户分配给Agent"""
        while not self._stop_event.is_set():
            await asyncio.sleep(2)

            if not self.pending_customers:
                continue

            # 为每个待处理客户分配Agent
            for customer_id in self.pending_customers[:]:
                customer = self.customers[customer_id]

                # 选择Agent（简单随机选择，可优化为轮询或负载均衡）
                available_agents = [
                    aid for aid in self.agent_stats.keys()
                    if len(self.serving_customers.get(aid, [])) < 5  # 每个Agent最多5个客户
                ]

                if not available_agents:
                    continue

                # 随机选择多个Agent竞争
                num_agents = min(
                    self.config.max_agents_per_customer,
                    len(available_agents)
                )
                selected_agents = random.sample(available_agents, num_agents)

                # 分配客户
                customer.status = CustomerStatus.SERVING
                customer.assigned_agent = selected_agents[0]  # 主Agent

                for agent_id in selected_agents:
                    if agent_id not in self.serving_customers:
                        self.serving_customers[agent_id] = []
                    self.serving_customers[agent_id].append(customer_id)

                    # 更新Agent统计
                    self.agent_stats[agent_id].customers_served += 1

                self.pending_customers.remove(customer_id)

                # 模拟对话和决策
                asyncio.create_task(
                    self._simulate_customer_interaction(customer_id, selected_agents)
                )

    async def _simulate_customer_interaction(self, customer_id: str, agent_ids: List[str]):
        """模拟客户与Agent的交互"""
        customer = self.customers[customer_id]

        # 模拟多轮对话（简化版）
        await asyncio.sleep(random.uniform(10, 30))

        # 做出决策
        decision = customer.make_purchase_decision({
            "premium": random.randint(5000, 50000)
        })

        # 更新统计
        if decision["decision"] == "purchase":
            winner_agent = agent_ids[0]  # 简化：第一个Agent成交
            stats = self.agent_stats[winner_agent]
            stats.total_gmv += decision["amount"]
            stats.deal_count += 1
            stats.customers_converted += 1

            self._emit_event("deal_closed", {
                "customer_id": customer_id,
                "agent_id": winner_agent,
                "amount": decision["amount"],
                "customer_tag": customer.persona.tag.value
            })

            print(f"✅ Deal closed: {customer.persona.label} -> {stats.agent_name} ¥{decision['amount']}")

        elif customer.status == CustomerStatus.BLOCKED:
            for agent_id in agent_ids:
                stats = self.agent_stats[agent_id]
                stats.reject_count += 1
                stats.compliance_violations += 1
                stats.compliance_score = max(0, stats.compliance_score - 10)

            self._emit_event("compliance_violation", {
                "customer_id": customer_id,
                "agents": agent_ids,
                "reason": customer.rejection_reason
            })

            print(f"❌ Compliance violation: {customer.persona.label} - {customer.rejection_reason}")

        else:  # LOST
            for agent_id in agent_ids:
                self.agent_stats[agent_id].lost_count += 1

            self._emit_event("customer_lost", {
                "customer_id": customer_id,
                "agents": agent_ids,
                "reason": decision.get("reason", "Unknown")
            })

            print(f"😞 Customer lost: {customer.persona.label}")

        # 清理
        for agent_id in agent_ids:
            if agent_id in self.serving_customers:
                if customer_id in self.serving_customers[agent_id]:
                    self.serving_customers[agent_id].remove(customer_id)

    async def _time_series_recorder(self):
        """时间序列数据记录"""
        while not self._stop_event.is_set():
            await asyncio.sleep(30)  # 每30秒记录一次

            data_point = {
                "time": datetime.now().strftime("%H:%M"),
                "timestamp": time.time()
            }

            # 记录每个Agent的累计GMV
            for agent_id, stats in self.agent_stats.items():
                data_point[stats.agent_name] = stats.total_gmv

            self.time_series_data.append(data_point)

    async def _session_timer(self):
        """会话计时器"""
        duration_seconds = self.config.session_duration_hours * 3600

        try:
            await asyncio.wait_for(
                self._stop_event.wait(),
                timeout=duration_seconds
            )
        except asyncio.TimeoutError:
            print(f"\n⏰ Session time limit reached ({self.config.session_duration_hours}h)")
            await self.stop()

    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """发送事件"""
        event = ArenaEvent(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data
        )
        self.events.append(event)

        # 调用回调
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Event callback error: {e}")

    def get_current_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "status": self.status.value,
            "agents": len(self.agents),
            "total_customers": len(self.customers),
            "pending_customers": len(self.pending_customers),
            "serving_customers": sum(len(c) for c in self.serving_customers.values()),
            "agent_stats": [s.to_dict() for s in self.agent_stats.values()],
            "time_series": self.time_series_data[-20:]  # 最近20个点
        }

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """获取排行榜"""
        stats_list = list(self.agent_stats.values())

        # 计算综合得分
        for stats in stats_list:
            # 综合得分 = GMV得分 + 转化率得分 + 合规得分
            gmv_score = min(100, stats.total_gmv / 10000)  # 每10万GMV得100分
            conversion_score = (
                stats.customers_converted / stats.customers_served * 100
                if stats.customers_served > 0 else 0
            )

            stats.composite_score = (
                gmv_score * self.config.gmv_weight +
                conversion_score * self.config.conversion_weight +
                stats.compliance_score * self.config.compliance_weight
            )

        # 排序
        sorted_stats = sorted(
            stats_list,
            key=lambda s: s.composite_score,
            reverse=True
        )

        return [
            {
                "rank": i + 1,
                **stats.to_dict(),
                "composite_score": round(stats.composite_score, 1)
            }
            for i, stats in enumerate(sorted_stats)
        ]

    def _print_final_stats(self):
        """打印最终统计"""
        print("\n" + "=" * 50)
        print("📊 FINAL RESULTS")
        print("=" * 50)

        leaderboard = self.get_leaderboard()
        for entry in leaderboard[:5]:
            print(f"{entry['rank']}. {entry['agent_name']}")
            print(f"   GMV: ¥{entry['total_gmv']:,.0f}")
            print(f"   Deals: {entry['deal_count']}")
            print(f"   Conversion: {entry['conversion_rate']}%")
            print(f"   Compliance: {entry['compliance_score']}")
            print(f"   Score: {entry['composite_score']}")
            print()


# 便捷函数
async def run_arena_session(
    agents: List[AgentConfig],
    duration_minutes: float = 60,
    event_callback: Callable = None
) -> ArenaOrchestrator:
    """
    运行竞技场会话

    Args:
        agents: 参与的Agent列表
        duration_minutes: 会话时长（分钟）
        event_callback: 事件回调函数

    Returns:
        ArenaOrchestrator: 完成的竞技会话
    """
    config = ArenaConfig(
        session_duration_hours=duration_minutes / 60,
        customer_generation_interval=(20, 60)  # 测试用，生成更快
    )

    orchestrator = ArenaOrchestrator(agents, config)

    if event_callback:
        orchestrator.add_event_callback(event_callback)

    await orchestrator.start()

    # 等待结束
    while orchestrator.status == ArenaStatus.RUNNING:
        await asyncio.sleep(1)

    return orchestrator
