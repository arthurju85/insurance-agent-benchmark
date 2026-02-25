"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useTheme } from "next-themes"
import { useI18n, type Locale } from "@/lib/i18n"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Sun, Moon, Monitor, Globe, Menu } from "lucide-react"
import { useState, useEffect } from "react"

const localeLabels = (t: (key: string) => string) => ({
  "zh-CN": t("locale.zh-CN"),
  "zh-TW": t("locale.zh-TW"),
  en: t("locale.en"),
})

export function SiteHeader() {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const { locale, setLocale, t } = useI18n()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])

  const labels = localeLabels(t)

  const navItems = [
    { href: "/", label: t("nav.leaderboard") },
    { href: "/arena", label: t("nav.arena") },
    { href: "/docs", label: t("nav.docs") },
    { href: "/submit", label: t("nav.submit") },
  ]

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/60 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-7xl items-center px-4 lg:px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 mr-8">
          <img
            src={mounted && theme === "dark" ? "/icon-dark-32x32.png" : "/icon-light-32x32.png"}
            alt="InsAgent Arena Logo"
            className="h-8 w-8"
            width={32}
            height={32}
          />
          <span className="text-lg font-bold tracking-tight text-foreground">
            InsAgent Arena
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href) && item.href !== "#"
            return (
              <Link
                key={item.href + item.label}
                href={item.href}
                className={cn(
                  "px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="flex-1" />

        {/* Language Switcher */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="gap-1.5 text-muted-foreground">
              <Globe className="h-4 w-4" />
              <span className="hidden sm:inline text-xs" suppressHydrationWarning>{mounted ? labels[locale] : ""}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {(Object.keys(labels) as Locale[]).map((loc) => (
              <DropdownMenuItem
                key={loc}
                onClick={() => setLocale(loc)}
                className={cn(locale === loc && "bg-accent")}
              >
                {labels[loc]}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Theme Switcher */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="text-muted-foreground">
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setTheme("light")}>
              <Sun className="mr-2 h-4 w-4" />
              {t("theme.light")}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("dark")}>
              <Moon className="mr-2 h-4 w-4" />
              {t("theme.dark")}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("system")}>
              <Monitor className="mr-2 h-4 w-4" />
              {t("theme.system")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Mobile Menu */}
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="sm" className="md:hidden text-muted-foreground">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-64">
            <nav className="flex flex-col gap-2 mt-8">
              {navItems.map((item) => {
                const isActive =
                  item.href === "/"
                    ? pathname === "/"
                    : pathname.startsWith(item.href) && item.href !== "#"
                return (
                  <Link
                    key={item.href + item.label}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "px-4 py-2.5 text-sm font-medium rounded-md transition-colors",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    )}
                  >
                    {item.label}
                  </Link>
                )
              })}
            </nav>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  )
}
