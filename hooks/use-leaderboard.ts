/**
 * Hook for fetching and managing leaderboard data
 */

import useSWR from "swr"
import { apiClient, LeaderboardResponse, LeaderboardEntry } from "@/lib/api/client"

interface UseLeaderboardOptions {
  month?: string
  agentType?: string
}

export function useLeaderboard(options: UseLeaderboardOptions = {}) {
  const { data, error, isLoading, mutate } = useSWR<LeaderboardResponse>(
    ["/api/v1/leaderboard/current", options.month, options.agentType],
    () => apiClient.getLeaderboard({
      month: options.month,
      agent_type: options.agentType,
    }),
    {
      refreshInterval: 60000, // 每分钟刷新
      revalidateOnFocus: false,
    }
  )

  // Filter and sort entries based on active tab
  const getSortedEntries = (sortKey: string): LeaderboardEntry[] => {
    if (!data?.entries) return []

    const entries = [...data.entries]

    // Sort based on the selected dimension
    switch (sortKey) {
      case "knowledge":
        return entries.sort((a, b) => b.knowledge_score - a.knowledge_score)
      case "claims":
        return entries.sort((a, b) => b.reasoning_score - a.reasoning_score)
      case "actuarial":
        return entries.sort((a, b) => b.tools_score - a.tools_score)
      case "compliance":
        return entries.sort((a, b) => b.compliance_score - a.compliance_score)
      case "tools":
        return entries.sort((a, b) => b.tools_score - a.tools_score)
      case "overall":
      default:
        return entries.sort((a, b) => b.overall_score - a.overall_score)
    }
  }

  return {
    data,
    entries: data?.entries || [],
    getSortedEntries,
    isLoading,
    error,
    refresh: mutate,
  }
}
