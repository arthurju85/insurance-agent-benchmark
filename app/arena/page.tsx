"use client"

import { useState, useEffect } from "react"
import { useI18n } from "@/lib/i18n"
import { SiteHeader } from "@/components/site-header"
import { LiveChart } from "@/components/arena/live-chart"
import { TransactionFeed } from "@/components/arena/transaction-feed"
import { CustomerPool } from "@/components/arena/customer-pool"
import { AgentStatusPanel } from "@/components/arena/agent-status"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Swords, Radio, Users } from "lucide-react"

function CountdownTimer() {
  const [time, setTime] = useState(9258) // seconds remaining

  useEffect(() => {
    const interval = setInterval(() => {
      setTime((prev) => (prev > 0 ? prev - 1 : 0))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const h = Math.floor(time / 3600)
  const m = Math.floor((time % 3600) / 60)
  const s = time % 60

  return (
    <span className="font-mono font-bold tabular-nums text-foreground">
      {h.toString().padStart(2, "0")}:{m.toString().padStart(2, "0")}:{s.toString().padStart(2, "0")}
    </span>
  )
}

export default function ArenaPage() {
  const { t } = useI18n()
  const [metric, setMetric] = useState("gmv")
  const [scenarioFilter, setScenarioFilter] = useState("all")

  const metricOptions = [
    { value: "gmv", label: t("arena.chart.gmv") },
    { value: "volume", label: t("arena.chart.volume") },
    { value: "conversion", label: t("arena.chart.conversion") },
    { value: "compliance", label: t("arena.chart.compliance") },
  ]

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <main className="mx-auto max-w-7xl px-4 py-6 lg:px-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
              <Swords className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground text-balance">
                {t("arena.title")}
              </h1>
              <p className="text-sm text-muted-foreground">
                {t("arena.subtitle")}
              </p>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="flex flex-wrap items-center gap-3 mb-6 p-4 rounded-xl border border-border bg-card">
          <div className="flex items-center gap-2">
            <div className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-success" />
            </div>
            <Badge variant="outline" className="text-success border-success/30 font-semibold text-xs">
              <Radio className="h-3 w-3 mr-1" />
              {t("arena.status.live")}
            </Badge>
          </div>

          <div className="h-4 w-px bg-border" />

          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">{t("arena.remaining")}:</span>
            <CountdownTimer />
          </div>

          <div className="h-4 w-px bg-border" />

          <div className="flex items-center gap-1.5 text-sm">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">{t("arena.agents")}:</span>
            <span className="font-semibold text-foreground">5</span>
          </div>

          <div className="flex-1" />

          {/* Scenario Filter */}
          <div className="flex items-center gap-1">
            {[
              { key: "all", label: t("arena.filter.all") },
              { key: "highnet", label: t("arena.filter.highnet") },
              { key: "parents", label: t("arena.filter.parents") },
              { key: "elderly", label: t("arena.filter.elderly") },
            ].map((f) => (
              <button
                key={f.key}
                onClick={() => setScenarioFilter(f.key)}
                className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors ${
                  scenarioFilter === f.key
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6">
          {/* Left - Charts */}
          <div className="space-y-6">
            {/* Live Chart */}
            <div className="rounded-xl border border-border bg-card p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-foreground">
                  {metricOptions.find((m) => m.value === metric)?.label}
                </h2>
                <Select value={metric} onValueChange={setMetric}>
                  <SelectTrigger className="w-[180px] h-8 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {metricOptions.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value} className="text-xs">
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <LiveChart metric={metric} />
            </div>

            {/* Transaction Feed */}
            <TransactionFeed />
          </div>

          {/* Right - Sidebar */}
          <div className="space-y-6">
            <AgentStatusPanel />
            <CustomerPool />
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
          <a href="/docs#arena-rules" className="hover:text-foreground transition-colors underline underline-offset-4">
            {t("arena.rules")}
          </a>
          <span className="text-border">|</span>
          <a href="/arena/history" className="hover:text-foreground transition-colors underline underline-offset-4">
            {t("arena.replay")}
          </a>
        </div>
      </main>
    </div>
  )
}
