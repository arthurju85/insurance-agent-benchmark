"use client"

import { Fragment, useState } from "react"
import { useI18n } from "@/lib/i18n"
import type { LeaderboardEntry } from "@/lib/api/client"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Sparkline } from "./sparkline"
import { AgentRadarChart } from "./radar-chart"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ChevronDown, ChevronUp, TrendingUp, TrendingDown, Minus, Eye } from "lucide-react"

interface RankingTableProps {
  agents: LeaderboardEntry[]
  sortKey: string
  compareMode: boolean
}

function RankIcon({ rank }: { rank: number }) {
  if (rank === 1) return <div className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-500/15 text-amber-500 font-bold text-sm">1</div>
  if (rank === 2) return <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-400/15 text-slate-400 font-bold text-sm">2</div>
  if (rank === 3) return <div className="flex h-7 w-7 items-center justify-center rounded-full bg-orange-600/15 text-orange-600 font-bold text-sm">3</div>
  return <div className="flex h-7 w-7 items-center justify-center text-muted-foreground font-medium text-sm">{rank}</div>
}

export function RankingTable({ agents, sortKey, compareMode }: RankingTableProps) {
  const { t } = useI18n()
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  const sorted = [...agents].sort((a, b) => {
    if (sortKey === "overall") return b.overall_percentage - a.overall_percentage
    if (sortKey === "knowledge") return b.knowledge_score - a.knowledge_score
    if (sortKey === "claims") return b.reasoning_score - a.reasoning_score
    if (sortKey === "actuarial") return b.tools_score - a.tools_score
    if (sortKey === "compliance") return b.compliance_score - a.compliance_score
    if (sortKey === "tools") return b.tools_score - a.tools_score
    return b.overall_percentage - a.overall_percentage
  })

  const getScore = (agent: LeaderboardEntry) => {
    if (sortKey === "overall") return agent.overall_percentage
    if (sortKey === "knowledge") return agent.knowledge_score
    if (sortKey === "claims") return agent.reasoning_score
    if (sortKey === "actuarial") return agent.tools_score
    if (sortKey === "compliance") return agent.compliance_score
    if (sortKey === "tools") return agent.tools_score
    return agent.overall_percentage
  }

  const toggleSelect = (agentId: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(agentId)) {
        next.delete(agentId)
      } else if (next.size < 3) {
        next.add(agentId)
      }
      return next
    })
  }

  const selectedAgents = sorted.filter((a) => selectedIds.has(a.agent_id))

  return (
    <div className="space-y-4">
      {/* Compare radar chart */}
      {compareMode && selectedAgents.length >= 2 && (
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-sm font-medium text-foreground mb-2">
            {selectedAgents.map((a) => a.agent_name).join(" vs ")}
          </p>
          <AgentRadarChart agents={selectedAgents} />
        </div>
      )}

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent border-border">
              {compareMode && <TableHead className="w-10" />}
              <TableHead className="w-16 text-center">{t("leaderboard.rank")}</TableHead>
              <TableHead>{t("leaderboard.agent")}</TableHead>
              <TableHead className="text-right w-24">{t("leaderboard.score")}</TableHead>
              <TableHead className="text-right w-20">{t("leaderboard.change")}</TableHead>
              <TableHead className="text-center w-24">{t("leaderboard.trend")}</TableHead>
              <TableHead className="w-24" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.map((agent, i) => {
              const rank = i + 1
              const isExpanded = expandedId === agent.agent_id
              const score = getScore(agent)
              return (
                <Fragment key={agent.agent_id}>
                  <TableRow
                    className={cn(
                      "group cursor-pointer transition-colors border-border",
                      isExpanded && "bg-muted/50",
                      compareMode && selectedIds.has(agent.agent_id) && "bg-primary/5"
                    )}
                    onClick={() => {
                      if (compareMode) {
                        toggleSelect(agent.agent_id)
                      } else {
                        setExpandedId(isExpanded ? null : agent.agent_id)
                      }
                    }}
                  >
                    {compareMode && (
                      <TableCell className="text-center">
                        <div
                          className={cn(
                            "h-4 w-4 rounded border-2 transition-colors",
                            selectedIds.has(agent.agent_id)
                              ? "bg-primary border-primary"
                              : "border-muted-foreground/30"
                          )}
                        />
                      </TableCell>
                    )}
                    <TableCell className="text-center">
                      <div className="flex justify-center">
                        <RankIcon rank={rank} />
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <img
                          src={`/icon-${i % 2 === 0 ? "light" : "dark"}-32x32.png`}
                          alt={agent.agent_name}
                          className="h-6 w-6 rounded"
                          width={24}
                          height={24}
                        />
                        <div className="flex flex-col">
                          <span className="font-semibold text-foreground text-sm">{agent.agent_name}</span>
                          <span className="text-xs text-muted-foreground">
                            {agent.vendor} &middot; {agent.version}
                          </span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <span className="font-mono font-bold text-foreground text-base tabular-nums">
                        {score.toFixed(1)}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <span
                        className={cn(
                          "inline-flex items-center gap-0.5 text-sm font-medium",
                          agent.change > 0 && "text-success",
                          agent.change < 0 && "text-destructive",
                          agent.change === 0 && "text-muted-foreground"
                        )}
                      >
                        {agent.change > 0 ? (
                          <TrendingUp className="h-3.5 w-3.5" />
                        ) : agent.change < 0 ? (
                          <TrendingDown className="h-3.5 w-3.5" />
                        ) : (
                          <Minus className="h-3.5 w-3.5" />
                        )}
                        {agent.change > 0 ? "+" : ""}
                        {agent.change.toFixed(1)}
                      </span>
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex justify-center">
                        <Sparkline data={[]} isUp={agent.change >= 0} />
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Button variant="ghost" size="sm" className="h-7 px-2 text-xs text-muted-foreground hover:text-foreground">
                          <Eye className="h-3.5 w-3.5 mr-1" />
                          {t("leaderboard.details")}
                        </Button>
                        {!compareMode && (
                          isExpanded ? (
                            <ChevronUp className="h-4 w-4 text-muted-foreground" />
                          ) : (
                            <ChevronDown className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                          )
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                  {isExpanded && !compareMode && (
                    <TableRow className="border-border">
                      <TableCell colSpan={7} className="bg-muted/30 p-4">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          <div>
                            <AgentRadarChart agents={[agent]} />
                          </div>
                          <div className="space-y-3">
                            <h4 className="text-sm font-semibold text-foreground">
                              {sortKey === "overall" ? t("leaderboard.overall") : ""} Score Breakdown
                            </h4>
                            {[
                              { key: "knowledge", score: agent.knowledge_score, label: t("leaderboard.knowledge") },
                              { key: "claims", score: agent.reasoning_score, label: t("leaderboard.claims") },
                              { key: "actuarial", score: agent.tools_score, label: t("leaderboard.actuarial") },
                              { key: "compliance", score: agent.compliance_score, label: t("leaderboard.compliance") },
                              { key: "tools", score: agent.tools_score, label: t("leaderboard.tools") },
                            ].map((dim) => (
                                <div key={dim.key} className="flex items-center gap-3">
                                  <span className="text-xs text-muted-foreground w-20 shrink-0">
                                    {dim.label}
                                  </span>
                                  <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                                    <div
                                      className="h-full rounded-full bg-primary transition-all"
                                      style={{ width: `${dim.score}%` }}
                                    />
                                  </div>
                                  <span className="font-mono text-xs font-medium text-foreground w-10 text-right tabular-nums">
                                    {dim.score.toFixed(1)}
                                  </span>
                                </div>
                            ))}
                            <div className="pt-3 flex gap-2">
                              <Badge variant="outline" className="text-xs">{agent.agent_type === "insurer" ? "Insurer" : agent.agent_type === "tech" ? "Tech" : "Open Source"}</Badge>
                              <Badge variant="secondary" className="text-xs">{agent.version}</Badge>
                            </div>
                          </div>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </Fragment>
              )
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
