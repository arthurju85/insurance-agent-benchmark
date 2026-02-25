/**
 * API客户端
 * 统一封装后端API调用
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.message || `API错误: ${response.status}`)
    }

    return response.json()
  }

  // ========== 题库相关 ==========

  async getQuestionStats() {
    return this.request<{
      total_questions: number
      by_dimension: Record<string, number>
      by_difficulty: Record<string, number>
    }>("/api/v1/questions/stats")
  }

  async getQuestions(params?: { dimension?: string; difficulty?: string; limit?: number }) {
    const query = new URLSearchParams()
    if (params?.dimension) query.set("dimension", params.dimension)
    if (params?.difficulty) query.set("difficulty", params.difficulty)
    if (params?.limit) query.set("limit", params.limit.toString())

    return this.request<QuestionSummary[]>(`/api/v1/questions/?${query}`)
  }

  async getQuestion(questionId: string) {
    return this.request<QuestionDetail>(`/api/v1/questions/${questionId}`)
  }

  // ========== 排行榜相关 ==========

  async getLeaderboard(params?: { month?: string; agent_type?: string }) {
    const query = new URLSearchParams()
    if (params?.month) query.set("month", params.month)
    if (params?.agent_type) query.set("agent_type", params.agent_type)

    return this.request<LeaderboardResponse>(`/api/v1/leaderboard/current?${query}`)
  }

  async getAgentHistory(agentId: string) {
    return this.request<AgentHistoryResponse>(`/api/v1/leaderboard/history/${agentId}`)
  }

  // ========== Agent管理 ==========

  async listAgents() {
    return this.request<AgentConfig[]>("/api/v1/agents/")
  }

  async createAgent(agentConfig: CreateAgentRequest) {
    return this.request<{ success: boolean; agent_id: string }>("/api/v1/agents/", {
      method: "POST",
      body: JSON.stringify(agentConfig),
    })
  }

  async testAgent(agentId: string) {
    return this.request<AgentTestResponse>(`/api/v1/agents/${agentId}/test`)
  }

  // ========== 评测相关 ==========

  async runEvaluation(request: RunEvaluationRequest) {
    return this.request<EvaluationResponse>("/api/v1/evaluation/run", {
      method: "POST",
      body: JSON.stringify(request),
    })
  }

  // ========== 竞技场相关 ==========

  async getArenaStatus() {
    return this.request<ArenaStatus>("/api/v1/arena/status")
  }

  async getArenaLeaderboard() {
    return this.request<ArenaLeaderboardResponse>("/api/v1/arena/leaderboard")
  }

  async startArena(request: StartArenaRequest) {
    return this.request<{ success: boolean; message: string; session_id?: string }>(
      "/api/v1/arena/start",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    )
  }

  async stopArena() {
    return this.request<{ success: boolean; message: string }>("/api/v1/arena/stop", {
      method: "POST",
    })
  }

  async getArenaEvents(limit?: number) {
    const query = limit ? `?limit=${limit}` : ""
    return this.request<{ events: ArenaEvent[] }>(`/api/v1/arena/events${query}`)
  }

  async getArenaTimeSeries() {
    return this.request<{ data: TimeSeriesDataPoint[] }>("/api/v1/arena/time-series")
  }

  async getActiveCustomers() {
    return this.request<{ customers: Customer[]; total: number }>("/api/v1/arena/customers")
  }

  // WebSocket连接
  createWebSocketConnection(): WebSocket {
    const wsUrl = this.baseUrl.replace("http://", "ws://").replace("https://", "wss://")
    return new WebSocket(`${wsUrl}/api/v1/arena/ws`)
  }
}

// 类型定义
export interface QuestionSummary {
  question_id: string
  dimension: string
  question_type: string
  difficulty: string
  title: string
  score: number
}

export interface QuestionDetail extends QuestionSummary {
  content: string
  context?: string
  expected_schema?: any
  validation_rules: any
  ground_truth?: any
  tags: string[]
}

export interface LeaderboardResponse {
  leaderboard_id: string
  name: string
  evaluation_date: string
  total_agents: number
  entries: LeaderboardEntry[]
}

export interface LeaderboardEntry {
  rank: number
  agent_id: string
  agent_name: string
  vendor: string
  version: string
  agent_type: string
  overall_score: number
  overall_percentage: number
  knowledge_score: number
  understanding_score: number
  reasoning_score: number
  compliance_score: number
  tools_score: number
  change: number
  evaluation_date: string
}

export interface AgentHistoryResponse {
  agent_id: string
  history: { month: string; score: number }[]
}

export interface AgentConfig {
  id: string
  name: string
  vendor: string
  version: string
  agent_type: string
  model: string
}

export interface CreateAgentRequest {
  id: string
  name: string
  version?: string
  vendor: string
  agent_type: string
  base_url?: string
  api_key?: string
  model: string
  temperature?: number
  system_prompt?: string
}

export interface AgentTestResponse {
  success: boolean
  latency_ms: number
  error?: string
}

export interface RunEvaluationRequest {
  agent_config: CreateAgentRequest
  question_set_id?: string
  question_ids?: string[]
  concurrency?: number
}

export interface EvaluationResponse {
  evaluation_id: string
  status: string
  result?: {
    total_score: number
    max_total_score: number
    overall_percentage: number
    dimension_scores: DimensionScore[]
    question_results: QuestionResult[]
  }
}

export interface DimensionScore {
  dimension: string
  score: number
  max_score: number
  percentage: number
  question_count: number
}

export interface QuestionResult {
  question_id: string
  dimension: string
  score: number
  max_score: number
  status: string
  latency_ms: number
}

export interface ArenaStatus {
  status: string
  agents: number
  total_customers: number
  pending_customers: number
  serving_customers: number
  agent_stats: AgentArenaStats[]
  time_series: TimeSeriesDataPoint[]
}

export interface AgentArenaStats {
  agent_id: string
  agent_name: string
  total_gmv: number
  deal_count: number
  reject_count: number
  lost_count: number
  customers_served: number
  customers_converted: number
  conversion_rate: number
  compliance_score: number
}

export interface ArenaLeaderboardResponse {
  status: string
  leaderboard: ArenaLeaderboardEntry[]
}

export interface ArenaLeaderboardEntry {
  rank: number
  agent_id: string
  agent_name: string
  total_gmv: number
  deal_count: number
  conversion_rate: number
  compliance_score: number
  composite_score: number
}

export interface StartArenaRequest {
  agents: CreateAgentRequest[]
  duration_minutes: number
  config?: {
    max_concurrent_customers?: number
    max_agents_per_customer?: number
    gmv_weight?: number
    conversion_weight?: number
    compliance_weight?: number
  }
}

export interface ArenaEvent {
  type: string
  timestamp: string
  data: any
}

export interface TimeSeriesDataPoint {
  time: string
  timestamp: number
  [agentName: string]: number | string
}

export interface Customer {
  id: string
  label: string
  tag: string
  age: number
  gender: string
  occupation: string
  income: string
  status: string
  agent_id?: string
  trust_score: number
}

// 导出单例
export const apiClient = new ApiClient()

// 默认导出
export default apiClient
