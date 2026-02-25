"use client"

import { Line, LineChart, ResponsiveContainer } from "recharts"

interface SparklineProps {
  data?: number[]
  color?: string
  isUp: boolean
}

export function Sparkline({ data, isUp }: SparklineProps) {
  // Provide default empty data if not available
  const chartData = (data || []).map((value, i) => ({ value, index: i }))
  const strokeColor = isUp ? "oklch(0.65 0.2 160)" : "oklch(0.6 0.22 25)"

  // If no data, show placeholder
  if (chartData.length === 0) {
    return (
      <div className="w-20 h-8 flex items-center justify-center text-muted-foreground text-xs">
        -
      </div>
    )
  }

  return (
    <div className="w-20 h-8">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <Line
            type="monotone"
            dataKey="value"
            stroke={strokeColor}
            strokeWidth={1.5}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
