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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  getSubmissions,
  updateSubmission,
  isAuthenticated,
  type Submission,
} from "@/lib/admin/api"
import {
  Shield,
  LogOut,
  CheckCircle2,
  XCircle,
  Clock,
  Eye,
} from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/admin/dashboard", label: "仪表盘", icon: Shield },
  { href: "/admin/questions", label: "题目管理", icon: Eye },
  { href: "/admin/submissions", label: "提交审核", icon: CheckCircle2 },
]

export default function AdminSubmissionsPage() {
  const { t } = useI18n()
  const router = useRouter()
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [loading, setLoading] = useState(true)
  const [filterStatus, setFilterStatus] = useState<string>("all")
  const [selectedSubmission, setSelectedSubmission] = useState<Submission | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false)
  const [reviewStatus, setReviewStatus] = useState<"approved" | "rejected">("approved")
  const [reviewNotes, setReviewNotes] = useState("")

  // Check auth
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/admin/login")
    }
  }, [router])

  // Fetch submissions
  const fetchSubmissions = async () => {
    setLoading(true)
    try {
      const data = await getSubmissions(filterStatus === "all" ? undefined : filterStatus)
      setSubmissions(data || [])
    } catch (err) {
      console.error("Failed to fetch submissions:", err)
      // Mock data for demo
      const mockSubmissions: Submission[] = [
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
        {
          id: "sub-003",
          company_name: "蚂蚁集团",
          contact_person: "王五",
          email: "wangwu@antgroup.com",
          agent_type: "tech",
          company_type: "tech",
          status: "approved",
          submitted_at: "2026-02-23T09:00:00Z",
        },
        {
          id: "sub-004",
          company_name: "众安保险",
          contact_person: "赵六",
          email: "zhaoliu@zhongan.com",
          agent_type: "insurer",
          company_type: "insurer",
          status: "rejected",
          submitted_at: "2026-02-22T14:00:00Z",
        },
      ]
      setSubmissions(mockSubmissions)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSubmissions()
  }, [filterStatus])

  const handleLogout = () => {
    router.push("/admin/login")
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return (
          <Badge variant="secondary" className="gap-1">
            <Clock className="h-3 w-3" />
            待审核
          </Badge>
        )
      case "approved":
        return (
          <Badge className="bg-green-500 gap-1">
            <CheckCircle2 className="h-3 w-3" />
            已通过
          </Badge>
        )
      case "rejected":
        return (
          <Badge variant="destructive" className="gap-1">
            <XCircle className="h-3 w-3" />
            已拒绝
          </Badge>
        )
      default:
        return <Badge>{status}</Badge>
    }
  }

  const handleReview = async () => {
    if (!selectedSubmission) return

    try {
      await updateSubmission(selectedSubmission.id, reviewStatus, reviewNotes || undefined)
      alert(`提交已${reviewStatus === "approved" ? "批准" : "拒绝"}`)
      setReviewDialogOpen(false)
      setDetailOpen(false)
      fetchSubmissions()
    } catch (err) {
      alert(`审核失败：${err instanceof Error ? err.message : "未知错误"}`)
    }
  }

  const openReviewDialog = (status: "approved" | "rejected") => {
    setReviewStatus(status)
    setReviewNotes("")
    setReviewDialogOpen(true)
  }

  const getAgentTypeLabel = (type: string) => {
    switch (type) {
      case "insurer":
        return "保险公司"
      case "tech":
        return "技术厂商"
      case "open_source":
        return "开源项目"
      default:
        return type
    }
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
              <h1 className="text-2xl font-bold tracking-tight">提交审核</h1>
              <p className="text-sm text-muted-foreground">
                审核 Agent 提交申请
              </p>
            </div>

            {/* Filter */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="flex items-center gap-4">
                  <Label>状态筛选：</Label>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="全部" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">全部</SelectItem>
                      <SelectItem value="pending">待审核</SelectItem>
                      <SelectItem value="approved">已通过</SelectItem>
                      <SelectItem value="rejected">已拒绝</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-4 mb-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>总提交数</CardDescription>
                  <CardTitle className="text-3xl font-bold">{submissions.length}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>待审核</CardDescription>
                  <CardTitle className="text-3xl font-bold text-amber-500">
                    {submissions.filter((s) => s.status === "pending").length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>已通过</CardDescription>
                  <CardTitle className="text-3xl font-bold text-green-500">
                    {submissions.filter((s) => s.status === "approved").length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>已拒绝</CardDescription>
                  <CardTitle className="text-3xl font-bold text-red-500">
                    {submissions.filter((s) => s.status === "rejected").length}
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>

            {/* Submissions Table */}
            <Card>
              <CardHeader>
                <CardTitle>提交列表</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-8 text-muted-foreground">
                    加载中...
                  </div>
                ) : submissions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    暂无提交
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>公司</TableHead>
                        <TableHead>联系人</TableHead>
                        <TableHead>邮箱</TableHead>
                        <TableHead>类型</TableHead>
                        <TableHead>提交时间</TableHead>
                        <TableHead>状态</TableHead>
                        <TableHead className="text-right">操作</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {submissions.map((submission) => (
                        <TableRow key={submission.id}>
                          <TableCell className="font-medium">
                            {submission.company_name}
                          </TableCell>
                          <TableCell>{submission.contact_person}</TableCell>
                          <TableCell className="text-muted-foreground">
                            {submission.email}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">
                              {getAgentTypeLabel(submission.agent_type)}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-muted-foreground text-sm">
                            {new Date(submission.submitted_at).toLocaleDateString("zh-CN")}
                          </TableCell>
                          <TableCell>{getStatusBadge(submission.status)}</TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 px-2"
                              onClick={() => {
                                setSelectedSubmission(submission)
                                setDetailOpen(true)
                              }}
                            >
                              <Eye className="h-3.5 w-3.5" />
                              <span className="ml-1">详情</span>
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </main>
        </div>
      </div>

      {/* Detail Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>提交详情</DialogTitle>
            <DialogDescription>
              {selectedSubmission?.company_name} - {selectedSubmission?.contact_person}
            </DialogDescription>
          </DialogHeader>
          {selectedSubmission && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>公司名称</Label>
                  <div className="mt-2 text-sm">{selectedSubmission.company_name}</div>
                </div>
                <div>
                  <Label>联系人</Label>
                  <div className="mt-2 text-sm">{selectedSubmission.contact_person}</div>
                </div>
                <div>
                  <Label>邮箱</Label>
                  <div className="mt-2 text-sm">{selectedSubmission.email}</div>
                </div>
                <div>
                  <Label>Agent 类型</Label>
                  <div className="mt-2 text-sm">
                    {getAgentTypeLabel(selectedSubmission.agent_type)}
                  </div>
                </div>
                <div>
                  <Label>公司类型</Label>
                  <div className="mt-2 text-sm">
                    {getAgentTypeLabel(selectedSubmission.company_type)}
                  </div>
                </div>
                <div>
                  <Label>提交时间</Label>
                  <div className="mt-2 text-sm">
                    {new Date(selectedSubmission.submitted_at).toLocaleString("zh-CN")}
                  </div>
                </div>
              </div>
              <div>
                <Label>状态</Label>
                <div className="mt-2">{getStatusBadge(selectedSubmission.status)}</div>
              </div>
              {selectedSubmission.status === "pending" && (
                <div className="flex gap-2 pt-4 border-t">
                  <Button
                    className="flex-1 bg-green-600 hover:bg-green-700"
                    onClick={() => openReviewDialog("approved")}
                  >
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    批准
                  </Button>
                  <Button
                    variant="destructive"
                    className="flex-1"
                    onClick={() => openReviewDialog("rejected")}
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    拒绝
                  </Button>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Review Dialog */}
      <Dialog open={reviewDialogOpen} onOpenChange={setReviewDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {reviewStatus === "approved" ? "批准提交" : "拒绝提交"}
            </DialogTitle>
            <DialogDescription>
              {reviewStatus === "approved"
                ? "确认批准此提交？"
                : "确认拒绝此提交？"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="notes">备注（可选）</Label>
              <Textarea
                id="notes"
                placeholder="添加备注信息..."
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                className="mt-2"
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setReviewDialogOpen(false)}>
                取消
              </Button>
              <Button
                onClick={handleReview}
                className={reviewStatus === "approved" ? "bg-green-600 hover:bg-green-700" : ""}
              >
                {reviewStatus === "approved" ? (
                  <>
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    确认批准
                  </>
                ) : (
                  <>
                    <XCircle className="h-4 w-4 mr-2" />
                    确认拒绝
                  </>
                )}
              </Button>
            </DialogFooter>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
