"use client"

import { useI18n } from "@/lib/i18n"
import { arenaAgentStatus } from "@/lib/data"
import { Badge } from "@/components/ui/badge"
import { Users, Clock, DollarSign } from "lucide-react"

export function AgentStatusPanel() {
  const { t } = useI18n()

  return (
    <div className="rounded-xl border border-border bg-card">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <h3 className="text-sm font-semibold text-foreground">{t("arena.agentStatus")}</h3>
      </div>
      <div className="p-2 space-y-1">
        {arenaAgentStatus.map((agent, i) => (
          <div
            key={agent.id}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
          >
            <span className="text-xs font-bold text-muted-foreground w-5 text-center tabular-nums">
              {i + 1}
            </span>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-foreground truncate">{agent.name}</div>
              <div className="flex items-center gap-3 mt-0.5">
                <span className="flex items-center gap-1 text-xs text-primary">
                  <Users className="h-3 w-3" />
                  {t("arena.serving")}({agent.serving})
                </span>
                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {t("arena.waiting")}({agent.waiting})
                </span>
              </div>
            </div>
            <div className="text-right shrink-0">
              <div className="flex items-center gap-1 text-sm font-mono font-bold text-foreground tabular-nums">
                <DollarSign className="h-3 w-3 text-success" />
                ¥{(agent.gmv / 1000).toFixed(0)}K
              </div>
              <span className="text-[10px] text-muted-foreground">{t("arena.roundDeal")}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
