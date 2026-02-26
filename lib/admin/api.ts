/**
 * Admin API Client
 * 管理后台 API 客户端
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

// 本地存储 key
const ADMIN_TOKEN_KEY = "admin_token"
const ADMIN_USER_KEY = "admin_user"

export interface AdminUser {
  username: string
  role: string
  email?: string
}

export interface DashboardStats {
  // 题库统计
  total_questions: number
  questions_by_dimension: Record<string, number>
  questions_by_difficulty: Record<string, number>
  variant_questions: number

  // 评测统计
  total_evaluations: number
  evaluations_this_week: number
  evaluations_today: number
  avg_score: number

  // Agent 统计
  registered_agents: number
  active_agents: number

  // 系统状态
  system_health: string
  last_crawl_time?: string
  storage_usage: Record<string, any>
}

export interface Question {
  id: string
  title: string
  content: string
  dimension: string
  difficulty: string
  type: string
  score: number
  is_variant: boolean
  parent_id?: string
  tags: string[]
}

export interface QuestionListResponse {
  total: number
  page: number
  page_size: number
  total_pages: number
  questions: Question[]
}

export interface Submission {
  id: string
  company_name: string
  contact_person: string
  email: string
  agent_type: string
  company_type: string
  status: string
  submitted_at: string
}

// 认证相关函数
export function getToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(ADMIN_TOKEN_KEY)
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return
  localStorage.setItem(ADMIN_TOKEN_KEY, token)
}

export function removeToken(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem(ADMIN_TOKEN_KEY)
  localStorage.removeItem(ADMIN_USER_KEY)
}

export function getUser(): AdminUser | null {
  if (typeof window === "undefined") return null
  const userStr = localStorage.getItem(ADMIN_USER_KEY)
  if (!userStr) return null
  try {
    return JSON.parse(userStr)
  } catch {
    return null
  }
}

export function setUser(user: AdminUser): void {
  if (typeof window === "undefined") return
  localStorage.setItem(ADMIN_USER_KEY, JSON.stringify(user))
}

export function isAuthenticated(): boolean {
  return !!getToken()
}

// API 请求函数
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken()
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token && { "Authorization": `Bearer ${token}` }),
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...headers,
      ...(options.headers as HeadersInit),
    },
  })

  if (!response.ok) {
    if (response.status === 401) {
      removeToken()
      throw new Error("未授权，请重新登录")
    }
    const error = await response.text()
    throw new Error(error || `请求失败：${response.status}`)
  }

  const data = await response.json()
  return data.data || data
}

// 登录相关 API
export async function login(username: string, password: string): Promise<{ token: string; user: AdminUser }> {
  const token = getToken()
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  }

  const response = await fetch(`${API_BASE_URL}/admin/login`, {
    method: "POST",
    headers,
    body: JSON.stringify({ username, password }),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || "登录失败，请检查用户名和密码")
  }

  const data = await response.json()

  // 保存 token 和用户信息
  if (data.token) {
    setToken(data.token)
  }
  if (data.user) {
    setUser(data.user)
  }

  return { token: data.token, user: data.user }
}

export async function logout(): Promise<void> {
  removeToken()
}

// 仪表盘 API
export async function getDashboardStats(): Promise<DashboardStats> {
  return request<DashboardStats>("/admin/dashboard")
}

// 题目管理 API
export async function getQuestions(
  dimension?: string,
  difficulty?: string,
  isVariant?: boolean,
  keyword?: string,
  page = 1,
  pageSize = 20
): Promise<QuestionListResponse> {
  const params = new URLSearchParams()
  if (dimension) params.append("dimension", dimension)
  if (difficulty) params.append("difficulty", difficulty)
  if (isVariant !== undefined) params.append("is_variant", String(isVariant))
  if (keyword) params.append("keyword", keyword)
  params.append("page", String(page))
  params.append("page_size", String(pageSize))

  return request<QuestionListResponse>(`/admin/questions?${params.toString()}`)
}

export async function getQuestionDetail(questionId: string): Promise<Question> {
  return request<Question>(`/admin/questions/${questionId}`)
}

export async function updateQuestion(questionId: string, updates: Partial<Question>): Promise<void> {
  return request(`/admin/questions/${questionId}`, {
    method: "PUT",
    body: JSON.stringify(updates),
  })
}

export async function deleteQuestion(questionId: string): Promise<void> {
  return request(`/admin/questions/${questionId}`, {
    method: "DELETE",
  })
}

export async function createVariants(
  questionId: string,
  count = 3,
  seed?: number
): Promise<string[]> {
  const params = new URLSearchParams()
  params.append("count", String(count))
  if (seed) params.append("seed", String(seed))

  return request<string[]>(`/admin/questions/${questionId}/variants?${params.toString()}`, {
    method: "POST",
  })
}

// 提交审核 API
export async function getSubmissions(status?: string): Promise<Submission[]> {
  const params = status ? `?status=${status}` : ""
  return request<Submission[]>(`/admin/submissions${params}`)
}

export async function updateSubmission(
  submissionId: string,
  status: string,
  notes?: string
): Promise<void> {
  return request(`/admin/submissions/${submissionId}`, {
    method: "PUT",
    body: JSON.stringify({ status, notes }),
  })
}

// Agent 管理 API
export async function getAgents(): Promise<any[]> {
  return request<any[]>("/admin/agents")
}

export async function getEvaluations(status?: string): Promise<any[]> {
  const params = status ? `?status=${status}` : ""
  return request<any[]>(`/admin/evaluations${params}`)
}
