"use client";

import { AppShell } from "@/components/layout/AppShell";
import { DashboardView } from "@/components/admin/DashboardView";

export default function DailyDashboardPage() {
  return (
    <AppShell>
      <DashboardView
        title="Tableau de bord — Quotidien"
        subtitle="Activité des dernières 24 heures."
        period="day"
      />
    </AppShell>
  );
}
