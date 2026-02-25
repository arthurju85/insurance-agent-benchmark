// Mock data for InsAgent Arena

export interface AgentData {
  id: string
  name: string
  vendor: string
  version: string
  type: "insurer" | "tech" | "opensource"
  color: string
  overallScore: number
  change: number
  scores: {
    knowledge: number
    claims: number
    actuarial: number
    compliance: number
    tools: number
  }
  history: number[] // 6 months of scores
}

export const agents: AgentData[] = [
  {
    id: "pingan-a",
    name: "PingAn Agent-A",
    vendor: "Ping An Insurance",
    version: "v3.2",
    type: "insurer",
    color: "var(--chart-1)",
    overallScore: 92.4,
    change: 2.1,
    scores: { knowledge: 95.2, claims: 91.8, actuarial: 88.5, compliance: 94.1, tools: 92.3 },
    history: [85.1, 87.3, 88.9, 90.2, 90.3, 92.4],
  },
  {
    id: "taibao-b",
    name: "CPIC Agent-B",
    vendor: "CPIC",
    version: "v2.8",
    type: "insurer",
    color: "var(--chart-2)",
    overallScore: 89.7,
    change: -0.5,
    scores: { knowledge: 91.3, claims: 90.2, actuarial: 85.1, compliance: 92.8, tools: 89.1 },
    history: [82.5, 84.1, 86.7, 88.9, 90.2, 89.7],
  },
  {
    id: "zhongan-c",
    name: "ZhongAn Agent-C",
    vendor: "ZhongAn Online",
    version: "v4.1",
    type: "tech",
    color: "var(--chart-3)",
    overallScore: 87.3,
    change: 3.8,
    scores: { knowledge: 84.5, claims: 85.9, actuarial: 82.3, compliance: 90.1, tools: 93.7 },
    history: [75.2, 78.4, 80.1, 82.5, 83.5, 87.3],
  },
  {
    id: "renmin-d",
    name: "PICC Agent-D",
    vendor: "PICC",
    version: "v2.1",
    type: "insurer",
    color: "var(--chart-4)",
    overallScore: 85.9,
    change: 1.2,
    scores: { knowledge: 89.7, claims: 87.3, actuarial: 80.5, compliance: 88.2, tools: 83.8 },
    history: [78.3, 80.1, 82.4, 83.9, 84.7, 85.9],
  },
  {
    id: "taikang-e",
    name: "TaiKang Agent-E",
    vendor: "Taikang Insurance",
    version: "v1.9",
    type: "insurer",
    color: "var(--chart-5)",
    overallScore: 84.1,
    change: -1.3,
    scores: { knowledge: 86.8, claims: 83.5, actuarial: 79.2, compliance: 87.5, tools: 83.5 },
    history: [79.5, 81.2, 83.1, 84.5, 85.4, 84.1],
  },
  {
    id: "insurtech-f",
    name: "InsurBot-F",
    vendor: "InsurTech Co.",
    version: "v5.0",
    type: "tech",
    color: "#8884d8",
    overallScore: 83.5,
    change: 4.2,
    scores: { knowledge: 80.1, claims: 78.9, actuarial: 77.5, compliance: 85.3, tools: 95.7 },
    history: [70.1, 73.5, 76.2, 78.1, 79.3, 83.5],
  },
  {
    id: "opensource-g",
    name: "OpenInsure-G",
    vendor: "Open Source Community",
    version: "v1.2",
    type: "opensource",
    color: "#82ca9d",
    overallScore: 78.2,
    change: 5.1,
    scores: { knowledge: 75.3, claims: 74.8, actuarial: 72.1, compliance: 80.5, tools: 88.3 },
    history: [62.1, 65.4, 68.7, 72.3, 73.1, 78.2],
  },
  {
    id: "huatai-h",
    name: "HuaTai Agent-H",
    vendor: "Huatai Insurance",
    version: "v2.3",
    type: "insurer",
    color: "#ffc658",
    overallScore: 81.8,
    change: 0.3,
    scores: { knowledge: 84.2, claims: 82.1, actuarial: 78.9, compliance: 83.5, tools: 80.3 },
    history: [76.2, 78.1, 79.5, 80.8, 81.5, 81.8],
  },
]

// Arena data
export interface VirtualCustomer {
  id: string
  label: string
  age: number
  gender: string
  occupation: string
  income: string
  tag: "highnet" | "parents" | "elderly" | "health" | "invest"
  status: "pending" | "serving" | "closed" | "lost" | "blocked"
  agentId?: string
}

export const virtualCustomers: VirtualCustomer[] = [
  { id: "C001", label: "高净值客户", age: 45, gender: "男", occupation: "企业高管", income: "100万+", tag: "highnet", status: "closed", agentId: "pingan-a" },
  { id: "C002", label: "年轻父母", age: 32, gender: "女", occupation: "互联网产品经理", income: "30-50万", tag: "parents", status: "serving", agentId: "taibao-b" },
  { id: "C003", label: "退休人群", age: 62, gender: "男", occupation: "退休教师", income: "10-20万", tag: "elderly", status: "closed", agentId: "pingan-a" },
  { id: "C004", label: "健康焦虑", age: 28, gender: "女", occupation: "自由职业", income: "15-25万", tag: "health", status: "serving", agentId: "zhongan-c" },
  { id: "C005", label: "理财导向", age: 38, gender: "男", occupation: "金融分析师", income: "50-80万", tag: "invest", status: "pending" },
  { id: "C006", label: "年轻父母", age: 30, gender: "男", occupation: "工程师", income: "25-40万", tag: "parents", status: "serving", agentId: "renmin-d" },
  { id: "C007", label: "高净值客户", age: 52, gender: "女", occupation: "企业主", income: "200万+", tag: "highnet", status: "lost" },
  { id: "C008", label: "退休人群", age: 58, gender: "女", occupation: "医生(即将退休)", income: "20-35万", tag: "elderly", status: "blocked" },
  { id: "C009", label: "健康焦虑", age: 35, gender: "男", occupation: "教师", income: "15-25万", tag: "health", status: "pending" },
  { id: "C010", label: "理财导向", age: 42, gender: "女", occupation: "律师", income: "60-100万", tag: "invest", status: "serving", agentId: "taikang-e" },
]

export interface TransactionRecord {
  id: string
  time: string
  agentId: string
  agentName: string
  action: "deal" | "reject" | "lost"
  product: string
  amount: number
  customerTag: string
  reason?: string
}

export const transactionFeed: TransactionRecord[] = [
  { id: "T001", time: "10:23:45", agentId: "pingan-a", agentName: "PingAn Agent-A", action: "deal", product: "重疾险", amount: 12800, customerTag: "高净值客户" },
  { id: "T002", time: "10:23:12", agentId: "taibao-b", agentName: "CPIC Agent-B", action: "deal", product: "年金险", amount: 50000, customerTag: "退休人群" },
  { id: "T003", time: "10:22:58", agentId: "zhongan-c", agentName: "ZhongAn Agent-C", action: "reject", product: "万能险", amount: 0, customerTag: "老年群体", reason: "合规拦截-夸大收益" },
  { id: "T004", time: "10:22:31", agentId: "pingan-a", agentName: "PingAn Agent-A", action: "deal", product: "终身寿险", amount: 88000, customerTag: "高净值客户" },
  { id: "T005", time: "10:21:55", agentId: "renmin-d", agentName: "PICC Agent-D", action: "deal", product: "意外险", amount: 3600, customerTag: "年轻父母" },
  { id: "T006", time: "10:21:18", agentId: "taikang-e", agentName: "TaiKang Agent-E", action: "lost", product: "健康险", amount: 0, customerTag: "健康焦虑" },
  { id: "T007", time: "10:20:42", agentId: "taibao-b", agentName: "CPIC Agent-B", action: "deal", product: "教育金", amount: 25000, customerTag: "年轻父母" },
  { id: "T008", time: "10:19:58", agentId: "zhongan-c", agentName: "ZhongAn Agent-C", action: "deal", product: "百万医疗", amount: 1580, customerTag: "健康焦虑" },
  { id: "T009", time: "10:19:15", agentId: "pingan-a", agentName: "PingAn Agent-A", action: "deal", product: "年金险", amount: 120000, customerTag: "理财导向" },
  { id: "T010", time: "10:18:30", agentId: "renmin-d", agentName: "PICC Agent-D", action: "reject", product: "投连险", amount: 0, customerTag: "老年群体", reason: "合规拦截-不适当推荐" },
]

// Generate arena chart data (time series for multiple agents)
export function generateArenaChartData() {
  const points = 48 // 24 hours at 30-min intervals
  const data = []
  const agentGMVs: Record<string, number> = {
    "PingAn Agent-A": 0,
    "CPIC Agent-B": 0,
    "ZhongAn Agent-C": 0,
    "PICC Agent-D": 0,
    "TaiKang Agent-E": 0,
  }

  for (let i = 0; i < points; i++) {
    const hour = Math.floor(i / 2) + 9
    const min = (i % 2) * 30
    const time = `${hour.toString().padStart(2, "0")}:${min.toString().padStart(2, "0")}`

    // Simulate cumulative GMV growth with some randomness
    agentGMVs["PingAn Agent-A"] += Math.random() * 8000 + 3000
    agentGMVs["CPIC Agent-B"] += Math.random() * 7000 + 2500
    agentGMVs["ZhongAn Agent-C"] += Math.random() * 6000 + 2000
    agentGMVs["PICC Agent-D"] += Math.random() * 5500 + 1800
    agentGMVs["TaiKang Agent-E"] += Math.random() * 5000 + 1500

    data.push({
      time,
      "PingAn Agent-A": Math.round(agentGMVs["PingAn Agent-A"]),
      "CPIC Agent-B": Math.round(agentGMVs["CPIC Agent-B"]),
      "ZhongAn Agent-C": Math.round(agentGMVs["ZhongAn Agent-C"]),
      "PICC Agent-D": Math.round(agentGMVs["PICC Agent-D"]),
      "TaiKang Agent-E": Math.round(agentGMVs["TaiKang Agent-E"]),
    })
  }
  return data
}

export const arenaAgentColors: Record<string, string> = {
  "PingAn Agent-A": "var(--chart-1)",
  "CPIC Agent-B": "var(--chart-2)",
  "ZhongAn Agent-C": "var(--chart-3)",
  "PICC Agent-D": "var(--chart-4)",
  "TaiKang Agent-E": "var(--chart-5)",
}

export const arenaAgentStatus = [
  { id: "pingan-a", name: "PingAn Agent-A", serving: 3, waiting: 2, gmv: 156000 },
  { id: "taibao-b", name: "CPIC Agent-B", serving: 2, waiting: 4, gmv: 128000 },
  { id: "zhongan-c", name: "ZhongAn Agent-C", serving: 4, waiting: 1, gmv: 89000 },
  { id: "renmin-d", name: "PICC Agent-D", serving: 2, waiting: 3, gmv: 72000 },
  { id: "taikang-e", name: "TaiKang Agent-E", serving: 1, waiting: 5, gmv: 58000 },
]
