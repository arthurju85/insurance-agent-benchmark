"use client"

import { useState, useMemo } from "react"
import { useI18n } from "@/lib/i18n"
import { generateArenaChartData } from "@/lib/data"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"

const agentKeys = [
  "PingAn Agent-A",
  "CPIC Agent-B",
  "ZhongAn Agent-C",
  "PICC Agent-D",
  "TaiKang Agent-E",
]

const colors = [
  "oklch(0.65 0.2 240)",
  "oklch(0.7 0.2 160)",
  "oklch(0.75 0.18 45)",
  "oklch(0.65 0.2 330)",
  "oklch(0.7 0.15 280)",
]

const timeRanges = [
  { key: "1h", points: 2 },
  { key: "6h", points: 12 },
  { key: "24h", points: 48 },
  { key: "all", points: 48 },
]

interface LiveChartProps {
  metric: string
}

export function LiveChart({ metric }: LiveChartProps) {
  const { t } = useI18n()
  const [timeRange, setTimeRange] = useState("all")
  const [hiddenAgents, setHiddenAgents] = useState<Set<string>>(new Set())

  const fullData = useMemo(() => generateArenaChartData(), [])

  const range = timeRanges.find((r) => r.key === timeRange)!
  const data = fullData.slice(-range.points)

  const toggleAgent = (name: string) => {
    setHiddenAgents((prev) => {
      const next = new Set(prev)
      if (next.has(name)) next.delete(name)
      else next.add(name)
      return next
    })
  }

  const formatY = (val: number) => {
    if (val >= 10000) return `${(val / 10000).toFixed(0)}${t("unit.wan")}`
    return val.toLocaleString()
  }

  return (
    <div className="space-y-3">
      {/* Time range selector */}
      <div className="flex items-center gap-1">
        {timeRanges.map((r) => (
          <button
            key={r.key}
            onClick={() => setTimeRange(r.key)}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
              timeRange === r.key
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            }`}
          >
            {t(`arena.timerange.${r.key}`)}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="h-[340px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.5 0.02 240 / 0.1)" />
            <XAxis
              dataKey="time"
              tick={{ fill: "oklch(0.5 0.02 240)", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "oklch(0.5 0.02 240 / 0.2)" }}
            />
            <YAxis
              tickFormatter={formatY}
              tick={{ fill: "oklch(0.5 0.02 240)", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={55}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "oklch(0.17 0.015 250)",
                borderColor: "oklch(0.25 0.02 250)",
                borderRadius: 8,
                fontSize: 12,
                color: "oklch(0.95 0.005 240)",
              }}
              labelStyle={{ color: "oklch(0.6 0.02 240)" }}
              formatter={(value: number) => [`¥${value.toLocaleString()}`, undefined]}
            />
            {agentKeys.map((name, i) => (
              <Line
                key={name}
                type="monotone"
                dataKey={name}
                stroke={colors[i]}
                strokeWidth={hiddenAgents.has(name) ? 0 : 2.5}
                dot={false}
                activeDot={hiddenAgents.has(name) ? false : { r: 4, strokeWidth: 0 }}
                opacity={hiddenAgents.has(name) ? 0 : 1}
              />
            ))}
            <Legend
              onClick={(e) => {
                if (typeof e.value === "string") toggleAgent(e.value)
              }}
              wrapperStyle={{ cursor: "pointer", fontSize: 12 }}
              formatter={(value: string) => (
                <span style={{ color: hiddenAgents.has(value) ? "oklch(0.4 0.02 240)" : undefined, textDecoration: hiddenAgents.has(value) ? "line-through" : "none" }}>
                  {value}
                </span>
              )}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
