"use client"

import { useState, useEffect } from "react"
import { useI18n } from "@/lib/i18n"
import { apiClient, LeaderboardEntry } from "@/lib/api/client"
import { SiteHeader } from "@/components/site-header"
import { RankingTable } from "@/components/leaderboard/ranking-table"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Trophy, Calendar, Filter, Loader2 } from "lucide-react"

const months = [
  { value: "2026-01", label: "2026-01" },
  { value: "2025-12", label: "2025-12" },
  { value: "2025-11", label: "2025-11" },
  { value: "2025-10", label: "2025-10" },
  { value: "2025-09", label: "2025-09" },
  { value: "2025-08", label: "2025-08" },
]

export default function LeaderboardPage() {
  const { t } = useI18n()
  const [month, setMonth] = useState("2026-01")
  const [agentType, setAgentType] = useState("all")
  const [region, setRegion] = useState("all")
  const [compareMode, setCompareMode] = useState(false)
  const [activeTab, setActiveTab] = useState("overall")

  // API data state
  const [agents, setAgents] = useState<LeaderboardEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch leaderboard data
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const data = await apiClient.getLeaderboard({
          month,
          agent_type: agentType === "all" ? undefined : agentType,
        })
        setAgents(data.entries || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data")
        console.error("Failed to fetch leaderboard:", err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [month, agentType])

  const filteredAgents =
    agentType === "all"
      ? agents
      : agents.filter((a) => a.agent_type === agentType)

  const regionFilteredAgents =
    region === "all"
      ? filteredAgents
      : filteredAgents.filter((a) => {
          const vendor = a.vendor || ""
          if (region === "cn") {
            // 中国大陆：平安、太保、众安、人保、泰康等
            return vendor.includes("Ping") || vendor.includes("CPIC") ||
                   vendor.includes("ZhongAn") || vendor.includes("PICC") ||
                   vendor.includes("Taikang") || vendor.includes("Hua") ||
                   vendor.includes("China")
          }
          if (region === "hk") {
            // 中国香港
            return vendor.includes("Hong Kong") || vendor.includes("HK") ||
                   vendor.includes("AIA") || vendor.includes("Prudential") ||
                   vendor.includes("友邦") || vendor.includes("保诚")
          }
          return true
        })

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <main className="mx-auto max-w-7xl px-4 py-8 lg:px-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
              <Trophy className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground text-balance">
                {t("leaderboard.title")}
              </h1>
              <p className="text-sm text-muted-foreground">
                {t("leaderboard.subtitle")}
              </p>
            </div>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="flex flex-wrap items-center gap-3 mb-6 p-4 rounded-xl border border-border bg-card">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <Select value={month} onValueChange={setMonth}>
              <SelectTrigger className="w-[140px] h-8 text-sm">
                <SelectValue placeholder={t("leaderboard.month")} />
              </SelectTrigger>
              <SelectContent>
                {months.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <Select value={agentType} onValueChange={setAgentType}>
              <SelectTrigger className="w-[140px] h-8 text-sm">
                <SelectValue placeholder={t("leaderboard.type")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t("leaderboard.type.all")}</SelectItem>
                <SelectItem value="insurer">{t("leaderboard.type.insurer")}</SelectItem>
                <SelectItem value="tech">{t("leaderboard.type.tech")}</SelectItem>
                <SelectItem value="opensource">{t("leaderboard.type.opensource")}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <Select value={region} onValueChange={setRegion}>
              <SelectTrigger className="w-[140px] h-8 text-sm">
                <SelectValue placeholder={t("leaderboard.region")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t("leaderboard.region.all")}</SelectItem>
                <SelectItem value="cn">{t("leaderboard.region.cn")}</SelectItem>
                <SelectItem value="hk">{t("leaderboard.region.hk")}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex-1" />

          <div className="flex items-center gap-2">
            <Switch
              id="compare"
              checked={compareMode}
              onCheckedChange={setCompareMode}
            />
            <Label htmlFor="compare" className="text-sm text-muted-foreground cursor-pointer">
              {t("leaderboard.compare")}
            </Label>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="bg-muted/60">
            <TabsTrigger value="overall">{t("leaderboard.overall")}</TabsTrigger>
            <TabsTrigger value="knowledge">{t("leaderboard.knowledge")}</TabsTrigger>
            <TabsTrigger value="claims">{t("leaderboard.claims")}</TabsTrigger>
            <TabsTrigger value="actuarial">{t("leaderboard.actuarial")}</TabsTrigger>
            <TabsTrigger value="compliance">{t("leaderboard.compliance")}</TabsTrigger>
            <TabsTrigger value="tools">{t("leaderboard.tools")}</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab}>
            {isLoading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <span className="ml-2 text-muted-foreground">{t("leaderboard.loading")}</span>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
                <p className="text-lg font-medium text-destructive">{t("leaderboard.error")}</p>
                <p className="text-sm mt-1">{error}</p>
                <button
                  onClick={() => window.location.reload()}
                  className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                >
                  {t("leaderboard.retry")}
                </button>
              </div>
            ) : (
              <RankingTable
                agents={regionFilteredAgents}
                sortKey={activeTab}
                compareMode={compareMode}
              />
            )}
          </TabsContent>
        </Tabs>

        {/* Footer info */}
        <div className="mt-8 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
          <span>{t("leaderboard.updated")}: 2026-01-21 00:00 UTC</span>
          <span className="text-border">|</span>
          <a href="/docs#evaluation-methodology" className="hover:text-foreground transition-colors underline underline-offset-4">
            {t("leaderboard.methodology")}
          </a>
        </div>
      </main>
    </div>
  )
}
