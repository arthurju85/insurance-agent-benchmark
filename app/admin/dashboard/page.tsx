"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useI18n } from "@/lib/i18n"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  getDashboardStats,
  getSubmissions,
  isAuthenticated,
  logout,
  type DashboardStats,
  type Submission,
} from "@/lib/admin/api"
import {
  Shield,
  LogOut,
  FileText,
  CheckCircle2,
  Clock,
  Users,
  Trophy,
  TrendingUp,
  Database,
  Server,
  AlertCircle,
  Menu,
  X,
} from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/admin/dashboard", label: "仪表盘", icon: Shield },
  { href: "/admin/questions", label: "题目管理", icon: FileText },
  { href: "/admin/submissions", label: "提交审核", icon: CheckCircle2 },
]

export default function AdminDashboardPage() {
  const { t } = useI18n()
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [loading, setLoading] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // 检查登录状态
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/admin/login")
    }
  }, [router])

  // 获取数据
  useEffect(() => {
    const fetchData = async () => {
      if (!isAuthenticated()) return

      try {
        const [statsData, submissionsData] = await Promise.all([
          getDashboardStats().catch(() => null),
          getSubmissions().catch(() => []),
        ])

        // 模拟数据（如果 API 不可用）
        setStats(
          statsData || {
            total_questions: 450,
            questions_by_dimension: {
              knowledge: 120,
              understanding: 95,
              reasoning: 88,
              compliance: 77,
              tools: 70,
            },
            questions_by_difficulty: {
              easy: 150,
              medium: 200,
              hard: 100,
            },
            variant_questions: 1250,
            total_evaluations: 328,
            evaluations_this_week: 45,
            evaluations_today: 8,
            avg_score: 72.5,
            registered_agents: 12,
            active_agents: 8,
            system_health: "healthy",
            storage_usage: { used: 2.4, total: 10 },
          }
        )

        setSubmissions(
          submissionsData || [
            {
              id: "sub-001",
              company_name: "平安保险",
              contact_person: "张三",
              email: "zhangsan@pingan.com",
              agent_type: "insurer",
              company_type: "insurer",
              status: "pending",
              submitted_at: "2026-02-25T10:00:00Z",
            },
            {
              id: "sub-002",
              company_name: "腾讯云 AI",
              contact_person: "李四",
              email: "lisi@tencent.com",
              agent_type: "tech",
              company_type: "tech",
              status: "pending",
              submitted_at: "2026-02-24T15:30:00Z",
            },
          ]
        )
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleLogout = () => {
    logout()
    router.push("/admin/login")
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return <Badge variant="secondary">待审核</Badge>
      case "approved":
        return <Badge className="bg-green-500">已通过</Badge>
      case "rejected":
        return <Badge variant="destructive">已拒绝</Badge>
      default:
        return <Badge>{status}</Badge>
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Clock className="h-8 w-8 animate-spin mx-auto text-primary mb-2" />
          <p className="text-muted-foreground">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 lg:px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <Shield className="h-4 w-4 text-primary" />
            </div>
            <span className="font-semibold">管理后台</span>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              退出
            </Button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8 lg:px-6">
        <div className="flex gap-6">
          {/* Desktop Sidebar */}
          <aside className="hidden lg:block w-48 shrink-0">
            <nav className="sticky top-20 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-muted transition-colors"
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Link>
              ))}
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1 min-w-0">
            <div className="mb-6">
              <h1 className="text-2xl font-bold tracking-tight">仪表盘</h1>
              <p className="text-sm text-muted-foreground">
                系统概览和统计数据
              </p>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    题目总数
                  </CardDescription>
                  <CardTitle className="text-3xl font-bold">
                    {stats?.total_questions || 0}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-muted-foreground" />
                    变体题目数
                  </CardDescription>
                  <CardTitle className="text-3xl font-bold">
                    {stats?.variant_questions || 0}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription className="flex items-center gap-2">
                    <Trophy className="h-4 w-4 text-muted-foreground" />
                    评测总数
                  </CardDescription>
                  <CardTitle className="text-3xl font-bold">
                    {stats?.total_evaluations || 0}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    平均分数
                  </CardDescription>
                  <CardTitle className="text-3xl font-bold">
                    {stats?.avg_score?.toFixed(1) || 0}
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>

            {/* More Stats */}
            <div className="grid gap-4 md:grid-cols-3 mb-8">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>本周评测</CardDescription>
                  <CardTitle className="text-2xl font-bold">
                    {stats?.evaluations_this_week || 0}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>今日评测</CardDescription>
                  <CardTitle className="text-2xl font-bold">
                    {stats?.evaluations_today || 0}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>系统状态</CardDescription>
                  <div className="flex items-center gap-2">
                    <div
                      className={cn(
                        "h-3 w-3 rounded-full",
                        stats?.system_health === "healthy"
                          ? "bg-green-500"
                          : "bg-red-500"
                      )}
                    />
                    <CardTitle className="text-2xl font-bold capitalize">
                      {stats?.system_health === "healthy" ? "健康" : "异常"}
                    </CardTitle>
                  </div>
                </CardHeader>
              </Card>
            </div>

            {/* Questions by Dimension */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>题目维度分布</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-5">
                  {Object.entries(stats?.questions_by_dimension || {}).map(
                    ([dimension, count]) => (
                      <div
                        key={dimension}
                        className="p-4 rounded-lg bg-muted/50 text-center"
                      >
                        <div className="text-sm text-muted-foreground capitalize">
                          {dimension}
                        </div>
                        <div className="text-2xl font-bold">{count}</div>
                      </div>
                    )
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Questions by Difficulty */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>题目难度分布</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  {Object.entries(stats?.questions_by_difficulty || {}).map(
                    ([difficulty, count]) => (
                      <div
                        key={difficulty}
                        className="p-4 rounded-lg bg-muted/50 text-center"
                      >
                        <div className="text-sm text-muted-foreground capitalize">
                          {difficulty === "easy" ? "简单" : difficulty === "medium" ? "中等" : "困难"}
                        </div>
                        <div className="text-2xl font-bold">{count}</div>
                      </div>
                    )
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Agent Stats */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Agent 统计</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="p-4 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        注册 Agent
                      </span>
                    </div>
                    <div className="text-3xl font-bold">
                      {stats?.registered_agents || 0}
                    </div>
                  </div>
                  <div className="p-4 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-2 mb-2">
                      <Server className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        活跃 Agent
                      </span>
                    </div>
                    <div className="text-3xl font-bold">
                      {stats?.active_agents || 0}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Pending Submissions */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>待审核提交</CardTitle>
                  <Link href="/admin/submissions">
                    <Button variant="outline" size="sm">
                      查看全部
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                {submissions.filter((s) => s.status === "pending").length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>公司</TableHead>
                        <TableHead>联系人</TableHead>
                        <TableHead>类型</TableHead>
                        <TableHead>提交时间</TableHead>
                        <TableHead>状态</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {submissions
                        .filter((s) => s.status === "pending")
                        .slice(0, 5)
                        .map((submission) => (
                          <TableRow key={submission.id}>
                            <TableCell className="font-medium">
                              {submission.company_name}
                            </TableCell>
                            <TableCell>{submission.contact_person}</TableCell>
                            <TableCell>
                              <Badge variant="outline">
                                {submission.company_type === "insurer"
                                  ? "保险公司"
                                  : submission.company_type === "tech"
                                  ? "技术厂商"
                                  : "开源"}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-muted-foreground">
                              {new Date(submission.submitted_at).toLocaleDateString("zh-CN")}
                            </TableCell>
                            <TableCell>{getStatusBadge(submission.status)}</TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <CheckCircle2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>暂无待审核的提交</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </main>
        </div>
      </div>
    </div>
  )
}
