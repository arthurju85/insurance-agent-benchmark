"use client"

import { useI18n } from "@/lib/i18n"
import { transactionFeed, type TransactionRecord } from "@/lib/data"
import { cn } from "@/lib/utils"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, XCircle, AlertTriangle } from "lucide-react"

function TransactionRow({ tx }: { tx: TransactionRecord }) {
  const { t } = useI18n()

  const actionConfig = {
    deal: {
      icon: CheckCircle2,
      label: t("arena.feed.deal"),
      className: "text-success",
      bg: "",
    },
    reject: {
      icon: XCircle,
      label: t("arena.feed.reject"),
      className: "text-destructive-foreground",
      bg: "bg-destructive/10",
    },
    lost: {
      icon: AlertTriangle,
      label: t("arena.feed.lost"),
      className: "text-warning",
      bg: "",
    },
  }

  const config = actionConfig[tx.action]
  const Icon = config.icon

  return (
    <div className={cn("flex items-start gap-3 px-3 py-2.5 rounded-lg transition-colors hover:bg-muted/50", config.bg)}>
      <Icon className={cn("h-4 w-4 mt-0.5 shrink-0", config.className)} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-muted-foreground font-mono tabular-nums">{tx.time}</span>
          <span className="text-sm font-medium text-foreground truncate">{tx.agentName}</span>
          <Badge
            variant={tx.action === "deal" ? "default" : tx.action === "reject" ? "destructive" : "secondary"}
            className="text-[10px] px-1.5 py-0"
          >
            {config.label}
          </Badge>
        </div>
        <div className="flex items-center gap-2 mt-0.5">
          {tx.action === "deal" && (
            <>
              <span className="text-xs text-muted-foreground">{tx.product}</span>
              <span className="text-xs font-medium text-foreground font-mono tabular-nums">
                ¥{tx.amount.toLocaleString()}
              </span>
            </>
          )}
          {tx.action === "reject" && tx.reason && (
            <span className="text-xs text-destructive-foreground">{tx.reason}</span>
          )}
          <span className="text-[10px] text-muted-foreground ml-auto">[{tx.customerTag}]</span>
        </div>
      </div>
    </div>
  )
}

export function TransactionFeed() {
  const { t } = useI18n()

  return (
    <div className="rounded-xl border border-border bg-card">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <h3 className="text-sm font-semibold text-foreground">{t("arena.feed.title")}</h3>
        <div className="flex h-2 w-2 rounded-full bg-success animate-pulse" />
      </div>
      <ScrollArea className="h-[280px]">
        <div className="p-2 space-y-0.5">
          {transactionFeed.map((tx) => (
            <TransactionRow key={tx.id} tx={tx} />
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}
