"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useI18n } from "@/lib/i18n"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
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
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "@/components/ui/tabs"
import {
  getQuestions,
  getQuestionDetail,
  createVariants,
  isAuthenticated,
  type Question,
  type QuestionListResponse,
} from "@/lib/admin/api"
import {
  Shield,
  LogOut,
  Search,
  Filter,
  Eye,
  Copy,
  Trash2,
  Sparkles,
  Menu,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/admin/dashboard", label: "仪表盘", icon: Shield },
  { href: "/admin/questions", label: "题目管理", icon: Eye },
  { href: "/admin/submissions", label: "提交审核", icon: Filter },
]

const dimensionLabels: Record<string, string> = {
  knowledge: "知识",
  understanding: "理解",
  reasoning: "推理",
  compliance: "合规",
  tools: "工具",
}

const difficultyLabels: Record<string, string> = {
  easy: "简单",
  medium: "中等",
  hard: "困难",
}

export default function AdminQuestionsPage() {
  const { t } = useI18n()
  const router = useRouter()
  const [questions, setQuestions] = useState<Question[]>([])
  const [totalQuestions, setTotalQuestions] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [variantDialogOpen, setVariantDialogOpen] = useState(false)
  const [variantCount, setVariantCount] = useState(3)

  // Filters
  const [dimension, setDimension] = useState<string>("all")
  const [difficulty, setDifficulty] = useState<string>("all")
  const [isVariant, setIsVariant] = useState<string>("all")
  const [keyword, setKeyword] = useState("")

  // Check auth
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/admin/login")
    }
  }, [router])

  // Fetch questions
  const fetchQuestions = async () => {
    setLoading(true)
    try {
      const data = await getQuestions(
        dimension === "all" ? undefined : dimension,
        difficulty === "all" ? undefined : difficulty,
        isVariant === "all" ? undefined : isVariant === "true",
        keyword || undefined,
        currentPage,
        20
      )
      setQuestions(data.questions || [])
      setTotalQuestions(data.total || 0)
      setTotalPages(data.total_pages || 0)
    } catch (err) {
      console.error("Failed to fetch questions:", err)
      // Mock data for demo
      const mockQuestions: Question[] = Array.from({ length: 15 }, (_, i) => ({
        id: `q-${i + 1}`,
        title: `题目 ${i + 1}`,
        content: `这是题目 ${i + 1} 的内容...`,
        dimension: ["knowledge", "understanding", "reasoning", "compliance", "tools"][i % 5],
        difficulty: ["easy", "medium", "hard"][i % 3],
        type: "choice",
        score: 100,
        is_variant: i % 3 === 0,
        tags: [],
      }))
      setQuestions(mockQuestions)
      setTotalQuestions(450)
      setTotalPages(23)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchQuestions()
  }, [currentPage, dimension, difficulty, isVariant])

  const handleSearch = () => {
    setCurrentPage(1)
    fetchQuestions()
  }

  const handleViewDetail = async (questionId: string) => {
    try {
      const detail = await getQuestionDetail(questionId)
      setSelectedQuestion(detail)
    } catch (err) {
      setSelectedQuestion({ id: questionId } as Question)
    }
    setDetailOpen(true)
  }

  const handleCreateVariants = async () => {
    if (!selectedQuestion) return

    try {
      const variantIds = await createVariants(selectedQuestion.id, variantCount)
      alert(`成功创建 ${variantCount} 个变体题目`)
      setVariantDialogOpen(false)
      fetchQuestions()
    } catch (err) {
      alert(`创建变体失败：${err instanceof Error ? err.message : "未知错误"}`)
    }
  }

  const handleLogout = () => {
    router.push("/admin/login")
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
              <h1 className="text-2xl font-bold tracking-tight">题目管理</h1>
              <p className="text-sm text-muted-foreground">
                浏览、搜索和管理题库
              </p>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                  <div className="lg:col-span-2">
                    <Label htmlFor="keyword">关键词搜索</Label>
                    <div className="flex gap-2 mt-2">
                      <Input
                        id="keyword"
                        placeholder="搜索题目内容..."
                        value={keyword}
                        onChange={(e) => setKeyword(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                      />
                      <Button onClick={handleSearch}>
                        <Search className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div>
                    <Label>评测维度</Label>
                    <Select value={dimension} onValueChange={setDimension}>
                      <SelectTrigger className="mt-2">
                        <SelectValue placeholder="全部" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部</SelectItem>
                        {Object.entries(dimensionLabels).map(([key, label]) => (
                          <SelectItem key={key} value={key}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>难度等级</Label>
                    <Select value={difficulty} onValueChange={setDifficulty}>
                      <SelectTrigger className="mt-2">
                        <SelectValue placeholder="全部" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部</SelectItem>
                        {Object.entries(difficultyLabels).map(([key, label]) => (
                          <SelectItem key={key} value={key}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>题目类型</Label>
                    <Select value={isVariant} onValueChange={setIsVariant}>
                      <SelectTrigger className="mt-2">
                        <SelectValue placeholder="全部" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部</SelectItem>
                        <SelectItem value="false">母题</SelectItem>
                        <SelectItem value="true">变体</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-3 mb-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>总题目数</CardDescription>
                  <CardTitle className="text-3xl font-bold">{totalQuestions}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>当前页</CardDescription>
                  <CardTitle className="text-3xl font-bold">
                    {currentPage} / {totalPages}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>每页显示</CardDescription>
                  <CardTitle className="text-3xl font-bold">20</CardTitle>
                </CardHeader>
              </Card>
            </div>

            {/* Questions Table */}
            <Card>
              <CardHeader>
                <CardTitle>题目列表</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-8 text-muted-foreground">
                    加载中...
                  </div>
                ) : questions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    暂无题目
                  </div>
                ) : (
                  <>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>题目 ID</TableHead>
                          <TableHead>标题</TableHead>
                          <TableHead>维度</TableHead>
                          <TableHead>难度</TableHead>
                          <TableHead>类型</TableHead>
                          <TableHead>分数</TableHead>
                          <TableHead className="text-right">操作</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {questions.map((question) => (
                          <TableRow key={question.id}>
                            <TableCell className="font-mono text-xs">
                              {question.id}
                            </TableCell>
                            <TableCell className="max-w-xs truncate">
                              <div className="flex items-center gap-2">
                                {question.is_variant && (
                                  <Badge variant="outline" className="text-xs">
                                    变体
                                  </Badge>
                                )}
                                <span className="font-medium">{question.title}</span>
                              </div>
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline">
                                {dimensionLabels[question.dimension] || question.dimension}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge
                                variant={
                                  question.difficulty === "easy"
                                    ? "secondary"
                                    : question.difficulty === "hard"
                                    ? "destructive"
                                    : "outline"
                                }
                              >
                                {difficultyLabels[question.difficulty] || question.difficulty}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-muted-foreground text-sm">
                              {question.type}
                            </TableCell>
                            <TableCell className="font-mono">
                              {question.score}
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex justify-end gap-1">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 px-2"
                                  onClick={() => handleViewDetail(question.id)}
                                >
                                  <Eye className="h-3.5 w-3.5" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 px-2"
                                  onClick={() => {
                                    setSelectedQuestion(question)
                                    setVariantDialogOpen(true)
                                  }}
                                >
                                  <Sparkles className="h-3.5 w-3.5" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>

                    {/* Pagination */}
                    <div className="flex items-center justify-between mt-4">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      >
                        <ChevronLeft className="h-4 w-4 mr-1" />
                        上一页
                      </Button>
                      <span className="text-sm text-muted-foreground">
                        第 {currentPage} 页，共 {totalPages} 页
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={currentPage === totalPages}
                        onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      >
                        下一页
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </main>
        </div>
      </div>

      {/* Question Detail Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedQuestion?.title || "题目详情"}</DialogTitle>
            <DialogDescription className="flex items-center gap-2">
              <Badge variant="outline">
                {dimensionLabels[selectedQuestion?.dimension || ""] || selectedQuestion?.dimension}
              </Badge>
              <Badge>
                {difficultyLabels[selectedQuestion?.difficulty || ""] || selectedQuestion?.difficulty}
              </Badge>
              {selectedQuestion?.is_variant && <Badge variant="secondary">变体题目</Badge>}
            </DialogDescription>
          </DialogHeader>
          {selectedQuestion && (
            <div className="space-y-4">
              <div>
                <Label>题目内容</Label>
                <div className="mt-2 p-4 rounded-lg bg-muted font-mono text-sm whitespace-pre-wrap">
                  {selectedQuestion.content || "暂无内容"}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>题目类型</Label>
                  <div className="mt-2 text-sm">{selectedQuestion.type}</div>
                </div>
                <div>
                  <Label>分数</Label>
                  <div className="mt-2 text-sm font-mono">{selectedQuestion.score}</div>
                </div>
              </div>
              <div>
                <Label>Tags</Label>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(selectedQuestion.tags || []).map((tag, i) => (
                    <Badge key={i} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                  {(selectedQuestion.tags || []).length === 0 && (
                    <span className="text-sm text-muted-foreground">无标签</span>
                  )}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Create Variants Dialog */}
      <Dialog open={variantDialogOpen} onOpenChange={setVariantDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>生成题目变体</DialogTitle>
            <DialogDescription>
              为题目 &quot;{selectedQuestion?.title}&quot; 生成变体
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="variantCount">变体数量</Label>
              <Select
                value={String(variantCount)}
                onValueChange={(v) => setVariantCount(Number(v))}
              >
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 个</SelectItem>
                  <SelectItem value="3">3 个</SelectItem>
                  <SelectItem value="5">5 个</SelectItem>
                  <SelectItem value="10">10 个</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setVariantDialogOpen(false)}>
                取消
              </Button>
              <Button onClick={handleCreateVariants}>
                <Sparkles className="h-4 w-4 mr-2" />
                生成变体
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
