"use client";

import { AppShell } from "@/components/layout/AppShell";
import { DashboardView } from "@/components/admin/DashboardView";

export default function MonthlyDashboardPage() {
  return (
    <AppShell>
      <DashboardView
        title="Tableau de bord — Mensuel"
        subtitle="Tendances sur les 30 derniers jours."
        period="month"
      />
    </AppShell>
  );
}
