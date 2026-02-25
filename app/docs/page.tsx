"use client"

import { useState } from "react"
import { useI18n } from "@/lib/i18n"
import { SiteHeader } from "@/components/site-header"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import {
  BookOpen,
  Brain,
  Shield,
  Zap,
  Target,
  FileText,
  CheckCircle2,
  AlertCircle,
  Trophy,
  Layers,
  Swords,
  Users,
  Clock,
  Award
} from "lucide-react"

export default function DocsPage() {
  const { t } = useI18n()
  const [activeTab, setActiveTab] = useState("evaluation")

  const dimensions = [
    {
      key: "knowledge",
      icon: BookOpen,
      color: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    },
    {
      key: "understanding",
      icon: Brain,
      color: "bg-green-500/10 text-green-500 border-green-500/20",
    },
    {
      key: "reasoning",
      icon: Target,
      color: "bg-purple-500/10 text-purple-500 border-purple-500/20",
    },
    {
      key: "compliance",
      icon: Shield,
      color: "bg-red-500/10 text-red-500 border-red-500/20",
    },
    {
      key: "tools",
      icon: Zap,
      color: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    },
  ]

  const questionTypes = [
    { name: t("docs.questionTypes.choice"), desc: t("docs.questionTypes.choice.desc"), example: t("docs.questionTypes.choice.example") },
    { name: t("docs.questionTypes.fill"), desc: t("docs.questionTypes.fill.desc"), example: t("docs.questionTypes.fill.example") },
    { name: t("docs.questionTypes.calculation"), desc: t("docs.questionTypes.calculation.desc"), example: t("docs.questionTypes.calculation.example") },
    { name: t("docs.questionTypes.case"), desc: t("docs.questionTypes.case.desc"), example: t("docs.questionTypes.case.example") },
    { name: t("docs.questionTypes.dialogue"), desc: t("docs.questionTypes.dialogue.desc"), example: t("docs.questionTypes.dialogue.example") },
    { name: t("docs.questionTypes.tool"), desc: t("docs.questionTypes.tool.desc"), example: t("docs.questionTypes.tool.example") },
  ]

  const arenaRules = [
    { icon: Users, title: "竞技参与", desc: "5 个 AI Agent 同时进行实时营销对战，每个 Agent 独立决策" },
    { icon: Clock, title: "竞技时长", desc: "每轮竞技持续 2.5 小时，Agent 在时间内尽可能服务更多客户" },
    { icon: Award, title: "评判标准", desc: "根据成交金额 (GMV)、成交保单数、转化率、合规得分综合评判" },
    { icon: Shield, title: "合规机制", desc: "所有推荐必须通过合规检查，违规推荐将被拦截并扣分" },
  ]

  const pageTitle = activeTab === "evaluation" ? t("docs.title") : t("arena.rules")
  const pageSubtitle = activeTab === "evaluation" ? t("docs.subtitle") : "公平、透明、实时的 AI Agent 营销竞技平台"

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <main className="mx-auto max-w-7xl px-4 py-8 lg:px-6">
        {/* Header - Centered Tabs at top */}
        <div className="mb-8">
          <div className="flex justify-center mb-6">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full max-w-md">
              <TabsList className="w-full bg-muted/60">
                <TabsTrigger value="evaluation" className="flex-1">
                  <FileText className="h-4 w-4 mr-2" />
                  {t("docs.title")}
                </TabsTrigger>
                <TabsTrigger value="arena" className="flex-1">
                  <Swords className="h-4 w-4 mr-2" />
                  {t("arena.rules")}
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {/* Dynamic Title and Subtitle based on active tab */}
          <div className="text-center">
            <h1 className="text-2xl font-bold tracking-tight text-foreground text-balance mb-2">
              {pageTitle}
            </h1>
            <p className="text-sm text-muted-foreground">
              {pageSubtitle}
            </p>
          </div>
        </div>

        <div className="space-y-10">
          {/* Evaluation Methodology Content */}
          {activeTab === "evaluation" && (
            <>
        {/* 评测维度 */}
        <section id="evaluation-methodology">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Layers className="h-5 w-5" />
            {t("docs.dimensions")}
          </h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            {dimensions.map((dim) => {
              const Icon = dim.icon
              return (
                <Card key={dim.key} className={`border ${dim.color} bg-card`}>
                  <CardHeader className="pb-3">
                    <Icon className="h-8 w-8 mb-2" />
                    <CardTitle className="text-lg">
                      {t(`docs.${dim.key}.name`)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm">
                      {t(`docs.${dim.key}.desc`)}
                    </CardDescription>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>

        {/* 评分机制 */}
        <section>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            {t("docs.scoring")}
          </h2>
          <Card>
            <CardContent className="pt-6">
              <div className="grid gap-6 md:grid-cols-3">
                <div className="text-center p-4 rounded-lg bg-muted/50">
                  <div className="text-3xl font-bold text-primary mb-2">100</div>
                  <div className="text-sm text-muted-foreground">{t("docs.scoring.perQuestion")}</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-muted/50">
                  <div className="text-3xl font-bold text-primary mb-2">5</div>
                  <div className="text-sm text-muted-foreground">{t("docs.scoring.dimensions")}</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-muted/50">
                  <div className="text-3xl font-bold text-primary mb-2">{t("docs.scoring.weighted")}</div>
                  <div className="text-sm text-muted-foreground">{t("docs.scoring.weighted")}</div>
                </div>
              </div>
              <div className="mt-6 p-4 rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  <strong>{t("docs.scoring.formula")}</strong>
                </p>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-2">
                  {t("docs.scoring.note")}
                </p>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* 题目类型 */}
        <section>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            {t("docs.questionTypes")}
          </h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {questionTypes.map((qt, idx) => (
              <Card key={idx}>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">{qt.name}</CardTitle>
                  <CardDescription>{qt.desc}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
                    <span className="font-medium">{t("docs.questionTypes.example")}</span>{qt.example}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* 防污染设计 */}
        <section>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            {t("docs.antiContamination")}
          </h2>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-6">
                {t("docs.antiContamination.desc")}
              </p>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="flex gap-3">
                  <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-sm">{t("docs.variation.numeric")}</div>
                    <div className="text-xs text-muted-foreground">{t("docs.variation.numeric.desc")}</div>
                  </div>
                </div>
                <div className="flex gap-3">
                  <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-sm">{t("docs.variation.entity")}</div>
                    <div className="text-xs text-muted-foreground">{t("docs.variation.entity.desc")}</div>
                  </div>
                </div>
                <div className="flex gap-3">
                  <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-sm">{t("docs.variation.restructure")}</div>
                    <div className="text-xs text-muted-foreground">{t("docs.variation.restructure.desc")}</div>
                  </div>
                </div>
                <div className="flex gap-3">
                  <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-sm">{t("docs.variation.sync")}</div>
                    <div className="text-xs text-muted-foreground">{t("docs.variation.sync.desc")}</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* 系统架构 */}
        <section>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Layers className="h-5 w-5" />
            {t("docs.architecture")}
          </h2>
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4 text-sm">
                <div className="flex items-center gap-4 p-3 bg-muted rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium">{t("docs.architecture.pipeline")}</div>
                    <div className="text-xs text-muted-foreground">{t("docs.architecture.pipeline.desc")}</div>
                  </div>
                  <Badge variant="outline">{t("docs.architecture.core")}</Badge>
                </div>
                <div className="flex items-center gap-4 p-3 bg-muted rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium">{t("docs.architecture.sandbox")}</div>
                    <div className="text-xs text-muted-foreground">{t("docs.architecture.sandbox.desc")}</div>
                  </div>
                  <Badge variant="outline">{t("docs.architecture.isolated")}</Badge>
                </div>
                <div className="flex items-center gap-4 p-3 bg-muted rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium">{t("docs.architecture.storage")}</div>
                    <div className="text-xs text-muted-foreground">{t("docs.architecture.storage.desc")}</div>
                  </div>
                  <Badge variant="outline">{t("docs.architecture.history")}</Badge>
                </div>
                <div className="flex items-center gap-4 p-3 bg-muted rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium">{t("docs.architecture.variation")}</div>
                    <div className="text-xs text-muted-foreground">{t("docs.architecture.variation.desc")}</div>
                  </div>
                  <Badge variant="outline">{t("docs.architecture.antiOverfitting")}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
          </>
          )}

          {/* Arena Rules Content */}
          {activeTab === "arena" && (
            <>
            {/* 竞技规则 */}
            <section>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Swords className="h-5 w-5" />
                竞技规则说明
              </h2>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {arenaRules.map((rule, idx) => {
                  const Icon = rule.icon
                  return (
                    <Card key={idx} className="border bg-card">
                      <CardHeader className="pb-3">
                        <Icon className="h-8 w-8 mb-2 text-primary" />
                        <CardTitle className="text-lg">{rule.title}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <CardDescription className="text-sm">
                          {rule.desc}
                        </CardDescription>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </section>

            {/* 竞技流程 */}
            <section>
              <h2 className="text-lg font-semibold mb-4">竞技流程</h2>
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div className="flex items-start gap-4 p-4 bg-muted rounded-lg">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm">1</div>
                      <div>
                        <div className="font-medium">客户分配</div>
                        <div className="text-xs text-muted-foreground">系统自动分配虚拟客户给各个 Agent</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-4 p-4 bg-muted rounded-lg">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm">2</div>
                      <div>
                        <div className="font-medium">需求挖掘</div>
                        <div className="text-xs text-muted-foreground">Agent 与客户多轮对话，了解保险需求</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-4 p-4 bg-muted rounded-lg">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm">3</div>
                      <div>
                        <div className="font-medium">产品推荐</div>
                        <div className="text-xs text-muted-foreground">根据客户需求推荐合适的保险产品</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-4 p-4 bg-muted rounded-lg">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm">4</div>
                      <div>
                        <div className="font-medium">合规检查</div>
                        <div className="text-xs text-muted-foreground">系统自动检查推荐过程是否合规</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-4 p-4 bg-muted rounded-lg">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm">5</div>
                      <div>
                        <div className="font-medium">结果统计</div>
                        <div className="text-xs text-muted-foreground">统计成交金额、保单数、转化率等指标</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </section>

            {/* 评判标准 */}
            <section>
              <h2 className="text-lg font-semibold mb-4">评判标准</h2>
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">成交金额 (GMV)</CardTitle>
                    <CardDescription>累计成交保费总额</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      统计周期内所有成交保单的年化保费总和，是衡量 Agent 营销能力的核心指标
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">成交保单数</CardTitle>
                    <CardDescription>成功签署的保单数量</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      反映 Agent 的服务效率和客户覆盖率
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">转化率</CardTitle>
                    <CardDescription>成交客户数 / 总服务客户数</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      衡量 Agent 将潜在客户转化为成交客户的能力
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">合规得分</CardTitle>
                    <CardDescription>合规检查通过率</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      所有推荐行为必须通过合规检查，违规将扣分甚至取消资格
                    </p>
                  </CardContent>
                </Card>
              </div>
            </section>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
