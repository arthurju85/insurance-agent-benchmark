"use client"

import { useState } from "react"
import { useI18n } from "@/lib/i18n"
import { SiteHeader } from "@/components/site-header"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Swords, Trophy, Calendar, TrendingUp, Eye } from "lucide-react"

// Mock historical data
const historicalRounds = [
  {
    id: "2025-12",
    month: "2025-12",
    status: "completed",
    winner: { id: "pingan-a", name: "PingAn Agent-A", gmv: 2850000, policies: 156 },
    participants: 5,
    totalGMV: 12500000,
    totalPolicies: 680,
    avgConversion: 42.5,
    dates: "2025-12-01 ~ 2025-12-31",
  },
  {
    id: "2025-11",
    month: "2025-11",
    status: "completed",
    winner: { id: "taibao-b", name: "CPIC Agent-B", gmv: 2650000, policies: 148 },
    participants: 5,
    totalGMV: 11800000,
    totalPolicies: 645,
    avgConversion: 40.2,
    dates: "2025-11-01 ~ 2025-11-30",
  },
  {
    id: "2025-10",
    month: "2025-10",
    status: "completed",
    winner: { id: "pingan-a", name: "PingAn Agent-A", gmv: 2420000, policies: 138 },
    participants: 5,
    totalGMV: 10900000,
    totalPolicies: 598,
    avgConversion: 38.8,
    dates: "2025-10-01 ~ 2025-10-31",
  },
  {
    id: "2025-09",
    month: "2025-09",
    status: "completed",
    winner: { id: "zhongan-c", name: "ZhongAn Agent-C", gmv: 2180000, policies: 142 },
    participants: 5,
    totalGMV: 9800000,
    totalPolicies: 562,
    avgConversion: 37.5,
    dates: "2025-09-01 ~ 2025-09-30",
  },
  {
    id: "2025-08",
    month: "2025-08",
    status: "completed",
    winner: { id: "pingan-a", name: "PingAn Agent-A", gmv: 1950000, policies: 125 },
    participants: 5,
    totalGMV: 8600000,
    totalPolicies: 498,
    avgConversion: 35.2,
    dates: "2025-08-01 ~ 2025-08-31",
  },
]

export default function ArenaHistoryPage() {
  const { t } = useI18n()
  const [selectedRound, setSelectedRound] = useState<string | null>(null)

  const selectedData = historicalRounds.find((r) => r.id === selectedRound)

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
                {t("arena.history.title")}
              </h1>
              <p className="text-sm text-muted-foreground">
                {t("arena.history.subtitle")}
              </p>
            </div>
          </div>
        </div>

        {/* Statistics Summary */}
        <div className="grid gap-4 md:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>{t("arena.history.totalRounds")}</CardDescription>
              <CardTitle className="text-3xl font-bold">5</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>{t("arena.history.totalGMV")}</CardDescription>
              <CardTitle className="text-3xl font-bold">¥5,360{t("unit.wan")}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>{t("arena.history.totalPolicies")}</CardDescription>
              <CardTitle className="text-3xl font-bold">2,983 {t("arena.history.winnerPolicies").replace("保单数", "").trim()}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>{t("arena.history.avgConversion")}</CardDescription>
              <CardTitle className="text-3xl font-bold">38.8%</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Historical Rounds */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Swords className="h-5 w-5" />
            {t("arena.history.pastRounds")}
          </h2>
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent border-border">
                  <TableHead>{t("arena.history.round")}</TableHead>
                  <TableHead>{t("arena.history.dates")}</TableHead>
                  <TableHead>{t("arena.history.winner")}</TableHead>
                  <TableHead className="text-right">{t("arena.history.winnerGMV")}</TableHead>
                  <TableHead className="text-right">{t("arena.history.winnerPolicies")}</TableHead>
                  <TableHead className="text-right">{t("arena.history.totalGMVLabel")}</TableHead>
                  <TableHead className="text-center">{t("arena.history.participants")}</TableHead>
                  <TableHead className="text-center">{t("arena.history.details")}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {historicalRounds.map((round) => (
                  <TableRow key={round.id} className="border-border">
                    <TableCell>
                      <Badge variant="outline" className="font-mono">
                        {round.month}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {round.dates}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Trophy className="h-4 w-4 text-amber-500" />
                        <span className="font-semibold">{round.winner.name}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      ¥{(round.winner.gmv / 10000).toFixed(0)}{t("unit.wan")}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {round.winner.policies}
                    </TableCell>
                    <TableCell className="text-right font-mono text-muted-foreground">
                      ¥{(round.totalGMV / 10000).toFixed(0)}{t("unit.wan")}
                    </TableCell>
                    <TableCell className="text-center">{round.participants}</TableCell>
                    <TableCell className="text-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 px-2 text-xs"
                        onClick={() => setSelectedRound(round.id)}
                      >
                        <Eye className="h-3.5 w-3.5 mr-1" />
                        {t("arena.history.details")}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Selected Round Details */}
        {selectedData && (
          <div className="mt-8 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">
                {selectedData.month} {t("arena.history.roundDetails")}
              </h2>
              <Button variant="outline" size="sm" onClick={() => setSelectedRound(null)}>
                {t("leaderboard.details")}
              </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>{t("arena.history.round")}</CardDescription>
                  <CardTitle className="text-2xl font-bold">{selectedData.month}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>{t("arena.history.totalGMV")}</CardDescription>
                  <CardTitle className="text-2xl font-bold">¥{(selectedData.totalGMV / 10000).toFixed(0)}{t("unit.wan")}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>{t("arena.history.totalPolicies")}</CardDescription>
                  <CardTitle className="text-2xl font-bold">{selectedData.totalPolicies}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>{t("arena.history.avgConversion")}</CardDescription>
                  <CardTitle className="text-2xl font-bold">{selectedData.avgConversion}%</CardTitle>
                </CardHeader>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="h-5 w-5 text-amber-500" />
                  {t("arena.history.winner")}：{selectedData.winner.name}
                </CardTitle>
                <CardDescription>
                  GMV: ¥{(selectedData.winner.gmv / 10000).toFixed(0)}{t("unit.wan")} | {t("arena.history.winnerPolicies")}：{selectedData.winner.policies}
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        )}

        {/* Back to Arena */}
        <div className="mt-8 flex justify-center">
          <Button asChild variant="outline">
            <a href="/arena">
              <Swords className="h-4 w-4 mr-2" />
              {t("arena.history.backToArena")}
            </a>
          </Button>
        </div>
      </main>
    </div>
  )
}
