"use client"

import { useI18n } from "@/lib/i18n"
import type { LeaderboardEntry } from "@/lib/api/client"
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
} from "recharts"

interface AgentRadarChartProps {
  agents: LeaderboardEntry[]
}

export function AgentRadarChart({ agents }: AgentRadarChartProps) {
  const { t } = useI18n()

  const dimensions = [
    { key: "knowledge", scoreKey: "knowledge_score", label: t("leaderboard.knowledge") },
    { key: "claims", scoreKey: "reasoning_score", label: t("leaderboard.claims") },
    { key: "actuarial", scoreKey: "tools_score", label: t("leaderboard.actuarial") },
    { key: "compliance", scoreKey: "compliance_score", label: t("leaderboard.compliance") },
    { key: "tools", scoreKey: "tools_score", label: t("leaderboard.tools") },
  ]

  // Calculate industry average
  const avg = dimensions.map((dim) => {
    const sum = agents.reduce(
      (acc, a) => acc + (a[dim.scoreKey as keyof LeaderboardEntry] as number || 0),
      0
    )
    return sum / agents.length
  })

  const data = dimensions.map((dim, i) => {
    const point: Record<string, string | number> = {
      dimension: dim.label,
      average: Math.round(avg[i] * 10) / 10,
    }
    agents.forEach((a) => {
      point[a.agent_name] = a[dim.scoreKey as keyof LeaderboardEntry] as number
    })
    return point
  })

  const chartColors = [
    "oklch(0.65 0.2 240)",
    "oklch(0.7 0.2 160)",
    "oklch(0.75 0.18 45)",
  ]

  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
        <PolarGrid stroke="oklch(0.5 0.02 240 / 0.2)" />
        <PolarAngleAxis
          dataKey="dimension"
          tick={{ fill: "oklch(0.6 0.02 240)", fontSize: 12 }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 100]}
          tick={{ fill: "oklch(0.5 0.02 240)", fontSize: 10 }}
          tickCount={5}
        />
        {/* Industry average dashed line */}
        <Radar
          name="AVG"
          dataKey="average"
          stroke="oklch(0.5 0.02 240 / 0.5)"
          fill="transparent"
          strokeDasharray="5 5"
          strokeWidth={1}
        />
        {agents.slice(0, 3).map((agent, i) => (
          <Radar
            key={agent.agent_id}
            name={agent.agent_name}
            dataKey={agent.agent_name}
            stroke={chartColors[i]}
            fill={chartColors[i]}
            fillOpacity={0.08}
            strokeWidth={2}
          />
        ))}
        <Legend
          wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
