/**
 * Data transformation utilities
 * Converts API data formats to component-compatible formats
 */

import { LeaderboardEntry } from "./client"

/**
 * Transform API leaderboard entry to component format
 */
export function transformLeaderboardEntry(entry: LeaderboardEntry): {
  id: string
  name: string
  vendor: string
  version: string
  type: string
  color: string
  overallScore: number
  change: number
  scores: {
    knowledge: number
    claims: number
    actuarial: number
    compliance: number
    tools: number
  }
  history: number[]
} {
  // Generate deterministic color based on agent_id
  const colorIndex = entry.agent_id.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % 5 + 1

  return {
    id: entry.agent_id,
    name: entry.agent_name,
    vendor: entry.vendor,
    version: entry.version,
    type: entry.agent_type,
    color: `var(--chart-${colorIndex})`,
    overallScore: entry.overall_percentage,
    change: entry.change,
    scores: {
      knowledge: entry.knowledge_score,
      claims: entry.reasoning_score,
      actuarial: entry.tools_score,
      compliance: entry.compliance_score,
      tools: entry.tools_score,
    },
    history: [], // Would need separate API call to get history
  }
}

/**
 * Transform Arena stats to component format
 */
export function transformArenaStats(entry: {
  agent_id: string
  agent_name: string
  customers_served: number
  total_gmv: number
  deal_count: number
  conversion_rate: number
}): {
  id: string
  name: string
  serving: number
  waiting: number
  gmv: number
  deals: number
  conversion_rate: number
} {
  return {
    id: entry.agent_id,
    name: entry.agent_name,
    serving: entry.customers_served,
    waiting: 0, // Would need to calculate from active connections
    gmv: entry.total_gmv,
    deals: entry.deal_count,
    conversion_rate: entry.conversion_rate,
  }
}
