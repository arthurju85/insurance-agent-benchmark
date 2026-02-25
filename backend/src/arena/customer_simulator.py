"""
虚拟客户引擎
模拟真实保险客户的行为、决策和对话
"""

import random
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class CustomerStatus(str, Enum):
    """客户状态"""
    PENDING = "pending"        # 等待分配
    SERVING = "serving"        # 服务中
    CLOSED = "closed"          # 已成交
    LOST = "lost"             # 已流失
    BLOCKED = "blocked"        # 合规拦截


class CustomerTag(str, Enum):
    """客户标签"""
    HIGH_NET_WORTH = "highnet"     # 高净值
    YOUNG_PARENTS = "parents"      # 年轻父母
    ELDERLY = "elderly"            # 退休人群
    HEALTH_ANXIOUS = "health"      # 健康焦虑
    INVESTMENT = "invest"          # 理财导向


@dataclass
class CustomerPersona:
    """客户人设"""
    id: str
    label: str
    tag: CustomerTag
    age: int
    gender: str
    occupation: str
    income: str
    family_status: str

    # 性格特征 (0-1)
    price_sensitivity: float = 0.5
    risk_aversion: float = 0.5
    brand_loyalty: float = 0.5
    decision_speed: float = 0.5

    # 需求偏好
    primary_need: str = ""
    secondary_needs: List[str] = field(default_factory=list)

    # 初始信任度
    initial_trust: float = 0.3

    # 背景故事
    backstory: str = ""


# 预定义客户人设库
CUSTOMER_PERSONAS = [
    CustomerPersona(
        id="C001",
        label="高净值企业家",
        tag=CustomerTag.HIGH_NET_WORTH,
        age=45,
        gender="男",
        occupation="企业主",
        income="500万+/年",
        family_status="已婚，一子一女",
        price_sensitivity=0.2,
        risk_aversion=0.7,
        brand_loyalty=0.8,
        decision_speed=0.4,
        primary_need="资产传承",
        secondary_needs=["税务规划", "债务隔离", "高端医疗"],
        initial_trust=0.4,
        backstory="经营企业20年，希望为家族财富做长远规划，关注财富安全和传承"
    ),
    CustomerPersona(
        id="C002",
        label="新手妈妈",
        tag=CustomerTag.YOUNG_PARENTS,
        age=32,
        gender="女",
        occupation="互联网产品经理",
        income="30-50万/年",
        family_status="已婚，1岁孩子",
        price_sensitivity=0.6,
        risk_aversion=0.8,
        brand_loyalty=0.5,
        decision_speed=0.7,
        primary_need="儿童健康保障",
        secondary_needs=["教育金储备", "家庭医疗保障", "意外险"],
        initial_trust=0.3,
        backstory="刚做妈妈，对孩子健康非常关注，希望给孩子最好的保障"
    ),
    CustomerPersona(
        id="C003",
        label="退休教师",
        tag=CustomerTag.ELDERLY,
        age=62,
        gender="女",
        occupation="退休教师",
        income="15万/年（退休金）",
        family_status="丧偶，独居",
        price_sensitivity=0.8,
        risk_aversion=0.9,
        brand_loyalty=0.7,
        decision_speed=0.3,
        primary_need="医疗保障",
        secondary_needs=["养老金补充", "护理保障"],
        initial_trust=0.2,
        backstory="担心老了生病拖累子女，希望有充足的医疗保障"
    ),
    CustomerPersona(
        id="C004",
        label="健康焦虑白领",
        tag=CustomerTag.HEALTH_ANXIOUS,
        age=28,
        gender="女",
        occupation="自由职业者",
        income="15-25万/年",
        family_status="单身",
        price_sensitivity=0.5,
        risk_aversion=0.9,
        brand_loyalty=0.3,
        decision_speed=0.6,
        primary_need="大病保障",
        secondary_needs=["医疗险", "收入损失补偿"],
        initial_trust=0.25,
        backstory="身边有朋友得重病，对疾病风险非常敏感"
    ),
    CustomerPersona(
        id="C005",
        label="理财导向金融从业者",
        tag=CustomerTag.INVESTMENT,
        age=38,
        gender="男",
        occupation="金融分析师",
        income="60-100万/年",
        family_status="已婚，无孩",
        price_sensitivity=0.3,
        risk_aversion=0.4,
        brand_loyalty=0.4,
        decision_speed=0.5,
        primary_need="资产配置",
        secondary_needs=["稳健收益", "流动性管理", "税优产品"],
        initial_trust=0.35,
        backstory="专业投资人，对收益率和流动性要求高，会仔细比较产品"
    ),
    CustomerPersona(
        id="C006",
        label="二胎爸爸",
        tag=CustomerTag.YOUNG_PARENTS,
        age=35,
        gender="男",
        occupation="工程师",
        income="40-60万/年",
        family_status="已婚，两个孩子",
        price_sensitivity=0.7,
        risk_aversion=0.7,
        brand_loyalty=0.6,
        decision_speed=0.5,
        primary_need="家庭保障",
        secondary_needs=["教育金", "房贷保障", "夫妻互保"],
        initial_trust=0.3,
        backstory="家庭责任重，担心万一出事家人生活无着落"
    ),
    CustomerPersona(
        id="C007",
        label="企业高管",
        tag=CustomerTag.HIGH_NET_WORTH,
        age=52,
        gender="女",
        occupation="上市公司CFO",
        income="200万+/年",
        family_status="离异，一女",
        price_sensitivity=0.1,
        risk_aversion=0.6,
        brand_loyalty=0.7,
        decision_speed=0.6,
        primary_need="财富传承",
        secondary_needs=["高端医疗", "子女教育", "养老社区"],
        initial_trust=0.45,
        backstory="离异后担心财富传承问题，希望给女儿做长远规划"
    ),
    CustomerPersona(
        id="C008",
        label="即将退休医生",
        tag=CustomerTag.ELDERLY,
        age=58,
        gender="男",
        occupation="医生（即将退休）",
        income="30万/年",
        family_status="已婚",
        price_sensitivity=0.5,
        risk_aversion=0.8,
        brand_loyalty=0.8,
        decision_speed=0.4,
        primary_need="退休规划",
        secondary_needs=["医疗险", "护理险", "养老金"],
        initial_trust=0.4,
        backstory="医学背景，对健康风险认知清晰，希望退休后有充足保障"
    ),
]


class VirtualCustomer:
    """
    虚拟客户
    模拟真实客户与Agent的交互和决策过程
    """

    def __init__(self, persona: CustomerPersona, session_id: str):
        self.persona = persona
        self.session_id = session_id
        self.status = CustomerStatus.PENDING
        self.assigned_agent: Optional[str] = None

        # 对话历史
        self.conversation_history: List[Dict[str, str]] = []

        # 动态状态
        self.trust_score = persona.initial_trust
        self.interest_score = 0.0
        self.satisfaction_score = 0.5

        # 需求满足度
        self.needs_addressed: Dict[str, float] = {}

        # 最终决策
        self.final_decision: Optional[str] = None
        self.purchase_amount: float = 0.0
        self.rejection_reason: Optional[str] = None

    def get_opening_message(self) -> str:
        """获取开场白"""
        openings = {
            CustomerTag.HIGH_NET_WORTH: [
                f"我想了解一下{self.persona.primary_need}相关的保险",
                "听说你们有高端客户专享的方案？",
                "我朋友推荐我来咨询一下家庭财富规划"
            ],
            CustomerTag.YOUNG_PARENTS: [
                f"我家{random.choice(['宝宝', '孩子'])}才{random.choice(['1岁', '2岁', '3岁'])}，想给他买份保险",
                "最近想给孩子存教育金，有什么推荐？",
                "孩子经常生病，想买医疗险"
            ],
            CustomerTag.ELDERLY: [
                "我这个年纪还能买保险吗？",
                "主要是想看病有保障",
                "退休了以后想有个保障"
            ],
            CustomerTag.HEALTH_ANXIOUS: [
                "我最近体检有些指标不太好，想买重疾险",
                "身边有人得了大病，想给自己做个保障",
                "有没有那种大病都能保的保险？"
            ],
            CustomerTag.INVESTMENT: [
                "你们这个产品的IRR是多少？",
                "我想比较一下你们和其他公司的年金险",
                "有没有兼顾收益和保障的产品？"
            ]
        }

        return random.choice(openings.get(self.persona.tag, ["我想了解一下保险"]))

    def respond_to_agent(self, agent_message: str) -> str:
        """
        根据Agent的消息生成回复
        基于人设和当前状态决策
        """
        # 更新信任度（基于Agent的专业性和态度）
        self._update_trust(agent_message)

        # 根据对话阶段生成回复
        turn = len(self.conversation_history)

        if turn == 0:
            return self.get_opening_message()

        # 分析Agent消息质量
        msg_quality = self._analyze_message_quality(agent_message)

        # 生成回复
        if self.status == CustomerStatus.SERVING:
            return self._generate_serving_response(agent_message, msg_quality)

        return "好的，我再考虑一下。"

    def _update_trust(self, agent_message: str):
        """更新对Agent的信任度"""
        # 检查专业性关键词
        professional_keywords = ["条款", "保障范围", "免责", "保费", "保额", "理赔"]
        professionalism = sum(1 for k in professional_keywords if k in agent_message) / len(professional_keywords)

        # 检查合规性（是否夸大收益）
        violation_keywords = ["稳赚", "保本", "肯定", "绝对", "一定赚"]
        violations = sum(1 for k in violation_keywords if k in agent_message)

        # 更新信任度
        trust_delta = professionalism * 0.1 - violations * 0.2
        self.trust_score = max(0, min(1, self.trust_score + trust_delta))

        # 如果严重违规，直接标记为拦截
        if violations >= 2:
            self.status = CustomerStatus.BLOCKED
            self.rejection_reason = "合规拦截-夸大收益"

    def _analyze_message_quality(self, message: str) -> Dict[str, float]:
        """分析Agent消息质量"""
        return {
            "professionalism": 0.5,  # 专业性
            "empathy": 0.5,          # 同理心
            "clarity": 0.5,          # 清晰度
            "relevance": 0.5         # 相关性
        }

    def _generate_serving_response(self, agent_message: str, quality: Dict[str, float]) -> str:
        """生成服务中的回复"""
        # 根据人设和信任度生成不同反应

        # 价格敏感型客户关注价格
        if self.persona.price_sensitivity > 0.6 and "价格" in agent_message or "保费" in agent_message:
            return random.choice([
                "这个价格有点贵，能不能便宜点？",
                "我对比了一下其他公司，你们的价格没什么优势啊",
                "有没有性价比更高的方案？"
            ])

        # 高净值客户关注服务
        if self.persona.tag == CustomerTag.HIGH_NET_WORTH:
            return random.choice([
                "你们有什么针对高端客户的服务？",
                "这个方案能不能再优化一下？",
                "我需要和家里商量一下"
            ])

        # 默认回复
        default_responses = [
            "明白了，请继续",
            "这个我不太懂，你能解释一下吗？",
            "好的，还有其他要注意的吗？",
            "那我应该怎么买？"
        ]

        return random.choice(default_responses)

    def make_purchase_decision(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        做出购买决策
        基于信任度、需求匹配度、价格敏感度等
        """
        # 计算成交概率
        purchase_probability = self._calculate_purchase_probability(proposal)

        if random.random() < purchase_probability:
            self.status = CustomerStatus.CLOSED
            self.final_decision = "purchase"
            self.purchase_amount = proposal.get("premium", 0)

            return {
                "decision": "purchase",
                "amount": self.purchase_amount,
                "reason": "产品匹配需求，信任Agent"
            }
        else:
            self.status = CustomerStatus.LOST
            self.final_decision = "reject"
            self.rejection_reason = self._generate_rejection_reason()

            return {
                "decision": "reject",
                "reason": self.rejection_reason
            }

    def _calculate_purchase_probability(self, proposal: Dict[str, Any]) -> float:
        """计算成交概率"""
        # 基础概率
        base_prob = 0.3

        # 信任度影响
        trust_factor = self.trust_score * 0.4

        # 需求匹配度影响
        need_match = 0.2  # 简化计算

        # 价格敏感度影响
        price_factor = (1 - self.persona.price_sensitivity) * 0.1

        probability = base_prob + trust_factor + need_match + price_factor
        return min(0.9, max(0.1, probability))

    def _generate_rejection_reason(self) -> str:
        """生成拒绝原因"""
        reasons = {
            CustomerTag.HIGH_NET_WORTH: ["方案不够高端", "需要再比较", "资金安排问题"],
            CustomerTag.YOUNG_PARENTS: ["保费太贵", "需要和家人商量", "想再比较一下"],
            CustomerTag.ELDERLY: ["太复杂搞不懂", "担心理赔", "觉得不划算"],
            CustomerTag.HEALTH_ANXIOUS: ["保障不够全面", "保费太高", "健康告知担心"],
            CustomerTag.INVESTMENT: ["收益率不满意", "流动性不好", "想再比较"]
        }

        return random.choice(reasons.get(self.persona.tag, ["再考虑一下"]))

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.persona.id,
            "label": self.persona.label,
            "tag": self.persona.tag.value,
            "age": self.persona.age,
            "gender": self.persona.gender,
            "occupation": self.persona.occupation,
            "income": self.persona.income,
            "status": self.status.value,
            "agent_id": self.assigned_agent,
            "trust_score": round(self.trust_score, 2),
            "conversation_turns": len(self.conversation_history)
        }


def generate_random_customer(session_id: str) -> VirtualCustomer:
    """生成随机虚拟客户"""
    persona = random.choice(CUSTOMER_PERSONAS)
    return VirtualCustomer(persona, session_id)


def get_customer_by_tag(tag: CustomerTag, session_id: str) -> VirtualCustomer:
    """按标签获取客户"""
    personas = [p for p in CUSTOMER_PERSONAS if p.tag == tag]
    if not personas:
        personas = CUSTOMER_PERSONAS

    persona = random.choice(personas)
    return VirtualCustomer(persona, session_id)
