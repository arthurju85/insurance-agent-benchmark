/**
 * Hook for managing Arena real-time data
 */

import { useState, useEffect, useCallback, useRef } from "react"
import { apiClient, ArenaStatus, ArenaLeaderboardEntry, ArenaEvent, TimeSeriesDataPoint, Customer } from "@/lib/api/client"

interface UseArenaReturn {
  status: string
  isRunning: boolean
  agentStats: ArenaLeaderboardEntry[]
  timeSeriesData: TimeSeriesDataPoint[]
  activeCustomers: Customer[]
  recentEvents: ArenaEvent[]
  startArena: (agents: any[], durationMinutes: number) => Promise<void>
  stopArena: () => Promise<void>
  isLoading: boolean
  error: string | null
}

export function useArena(): UseArenaReturn {
  const [status, setStatus] = useState<string>("idle")
  const [agentStats, setAgentStats] = useState<ArenaLeaderboardEntry[]>([])
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesDataPoint[]>([])
  const [activeCustomers, setActiveCustomers] = useState<Customer[]>([])
  const [recentEvents, setRecentEvents] = useState<ArenaEvent[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const pollingRef = useRef<NodeJS.Timeout | null>(null)

  // Fetch initial status
  const fetchStatus = useCallback(async () => {
    try {
      const data = await apiClient.getArenaStatus()
      setStatus(data.status)
      setAgentStats(data.agent_stats as unknown as ArenaLeaderboardEntry[])
      setTimeSeriesData(data.time_series)
    } catch (err) {
      console.error("Failed to fetch arena status:", err)
    }
  }, [])

  // Fetch active customers
  const fetchCustomers = useCallback(async () => {
    try {
      const data = await apiClient.getActiveCustomers()
      setActiveCustomers(data.customers)
    } catch (err) {
      console.error("Failed to fetch customers:", err)
    }
  }, [])

  // Fetch recent events
  const fetchEvents = useCallback(async () => {
    try {
      const data = await apiClient.getArenaEvents(20)
      setRecentEvents(data.events)
    } catch (err) {
      console.error("Failed to fetch events:", err)
    }
  }, [])

  // Start polling when arena is running
  useEffect(() => {
    if (status === "running") {
      // Start polling
      pollingRef.current = setInterval(() => {
        fetchStatus()
        fetchCustomers()
        fetchEvents()
      }, 5000)

      // Try WebSocket connection
      try {
        const ws = apiClient.createWebSocketConnection()

        ws.onopen = () => {
          console.log("WebSocket connected")
        }

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data)

          if (data.type === "stats_update") {
            setAgentStats(data.data.agent_stats)
            setTimeSeriesData(data.data.time_series)
          } else if (data.type === "customer_generated") {
            fetchCustomers()
            setRecentEvents((prev) => [data, ...prev].slice(0, 50))
          } else if (["deal_closed", "compliance_violation", "customer_lost"].includes(data.type)) {
            fetchStatus()
            setRecentEvents((prev) => [data, ...prev].slice(0, 50))
          }
        }

        ws.onerror = (error) => {
          console.error("WebSocket error:", error)
        }

        ws.onclose = () => {
          console.log("WebSocket disconnected")
        }

        wsRef.current = ws
      } catch (err) {
        console.error("Failed to create WebSocket:", err)
      }
    } else {
      // Stop polling
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }

      // Close WebSocket
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [status, fetchStatus, fetchCustomers, fetchEvents])

  // Initial fetch
  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  const startArena = async (agents: any[], durationMinutes: number) => {
    setIsLoading(true)
    setError(null)

    try {
      await apiClient.startArena({
        agents,
        duration_minutes: durationMinutes,
      })

      // Refresh status
      await fetchStatus()
    } catch (err: any) {
      setError(err.message || "Failed to start arena")
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const stopArena = async () => {
    setIsLoading(true)

    try {
      await apiClient.stopArena()
      await fetchStatus()
    } catch (err: any) {
      setError(err.message || "Failed to stop arena")
    } finally {
      setIsLoading(false)
    }
  }

  return {
    status,
    isRunning: status === "running",
    agentStats,
    timeSeriesData,
    activeCustomers,
    recentEvents,
    startArena,
    stopArena,
    isLoading,
    error,
  }
}
