"use client"

import { useI18n } from "@/lib/i18n"
import { virtualCustomers, agents, type VirtualCustomer } from "@/lib/data"
import { cn } from "@/lib/utils"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { User, Clock, CheckCircle2, XCircle, ShieldAlert } from "lucide-react"

const statusConfig: Record<
  VirtualCustomer["status"],
  { key: string; className: string; icon: typeof User }
> = {
  pending: { key: "arena.customer.pending", className: "text-muted-foreground border-muted-foreground/30", icon: Clock },
  serving: { key: "arena.customer.serving", className: "text-primary border-primary/30", icon: User },
  closed: { key: "arena.customer.closed", className: "text-success border-success/30", icon: CheckCircle2 },
  lost: { key: "arena.customer.lost", className: "text-warning border-warning/30", icon: XCircle },
  blocked: { key: "arena.customer.blocked", className: "text-destructive-foreground border-destructive/30", icon: ShieldAlert },
}

function CustomerCard({ customer }: { customer: VirtualCustomer }) {
  const { t } = useI18n()
  const config = statusConfig[customer.status]
  const Icon = config.icon
  const agent = customer.agentId ? agents.find((a) => a.id === customer.agentId) : null

  return (
    <div className="rounded-lg border border-border bg-card p-3 hover:bg-muted/50 transition-colors cursor-pointer">
      <div className="flex items-start gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-muted-foreground shrink-0">
          <User className="h-4 w-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-foreground">#{customer.id.slice(-3)}</span>
            <Badge variant="outline" className={cn("text-[10px] px-1.5 py-0", config.className)}>
              <Icon className="h-3 w-3 mr-0.5" />
              {t(config.key)}
            </Badge>
          </div>
          <div className="flex items-center gap-1.5 mt-1 text-xs text-muted-foreground">
            <span>{customer.label}</span>
            <span className="text-border">|</span>
            <span>{customer.age}{customer.gender === "男" ? "M" : "F"}</span>
            <span className="text-border">|</span>
            <span>{customer.income}</span>
          </div>
          {agent && (
            <div className="mt-1.5 text-[10px] text-primary font-medium">
              {agent.name}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export function CustomerPool() {
  const { t } = useI18n()

  return (
    <div className="rounded-xl border border-border bg-card">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <h3 className="text-sm font-semibold text-foreground">{t("arena.customers")}</h3>
        <span className="text-xs text-muted-foreground">{virtualCustomers.length}</span>
      </div>
      <ScrollArea className="h-[320px]">
        <div className="p-2 space-y-2">
          {virtualCustomers.map((c) => (
            <CustomerCard key={c.id} customer={c} />
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}
