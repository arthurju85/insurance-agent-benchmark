/**
 * Hook for fetching question bank statistics
 */

import useSWR from "swr"
import { apiClient } from "@/lib/api/client"

interface QuestionStats {
  total_questions: number
  by_dimension: Record<string, number>
  by_difficulty: Record<string, number>
  by_type?: Record<string, number>
}

export function useQuestionStats() {
  const { data, error, isLoading } = useSWR<QuestionStats>(
    "/api/v1/questions/stats",
    () => apiClient.getQuestionStats(),
    {
      revalidateOnFocus: false,
    }
  )

  return {
    stats: data,
    totalQuestions: data?.total_questions || 0,
    dimensionDistribution: data?.by_dimension || {},
    isLoading,
    error,
  }
}
