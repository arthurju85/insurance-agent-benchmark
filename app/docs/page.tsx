"use client"

import { useI18n } from "@/lib/i18n"
import { SiteHeader } from "@/components/site-header"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
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
  Layers
} from "lucide-react"

export default function DocsPage() {
  const { t } = useI18n()

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

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <main className="mx-auto max-w-7xl px-4 py-8 lg:px-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground text-balance">
                {t("docs.title")}
              </h1>
              <p className="text-sm text-muted-foreground">
                {t("docs.subtitle")}
              </p>
            </div>
          </div>
        </div>

        {/* 评测维度 */}
        <section className="mb-10">
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
        <section className="mb-10">
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
        <section className="mb-10">
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
        <section className="mb-10">
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
        <section className="mb-10">
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

        {/* Footer */}
        <div className="mt-8 pt-8 border-t border-border">
          <p className="text-sm text-muted-foreground text-center">
            {t("docs.footer")} <a href="/docs" className="text-primary hover:underline">{t("docs.footer.link")}</a>
          </p>
        </div>
      </main>
    </div>
  )
}
