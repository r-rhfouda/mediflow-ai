"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { Activity, BarChart3, BellRing, CalendarDays, ListOrdered, TrendingUp, UserCircle } from "lucide-react";

const NAV_ITEMS = [
  { href: "/queue", label: "File d'attente", icon: ListOrdered },
  { href: "/notifications", label: "Notifications", icon: BellRing },
  { href: "/appointments", label: "Rendez-vous", icon: CalendarDays },
  { href: "/profile", label: "Profil", icon: UserCircle },
  { href: "/admin/daily", label: "Dashboard — Jour", icon: BarChart3 },
  { href: "/admin/monthly", label: "Dashboard — Mois", icon: TrendingUp },
  { href: "/admin/overview", label: "Dashboard — Global", icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-60 flex-col bg-brand-deep text-white">
      <div className="flex items-center gap-2 px-5 py-6">
        <Activity className="h-6 w-6" strokeWidth={2.5} />
        <span className="font-display text-lg font-semibold tracking-tight">MediFlow AI</span>
      </div>

      <nav className="flex-1 px-3">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname?.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "mb-1 flex items-center gap-3 rounded px-3 py-2.5 text-sm font-medium font-body transition-colors",
                active ? "bg-white/10 text-white" : "text-white/70 hover:bg-white/5 hover:text-white"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 px-5 py-4 text-xs text-white/50 font-body">
        Cabinet médical · Démo
      </div>
    </aside>
  );
}
