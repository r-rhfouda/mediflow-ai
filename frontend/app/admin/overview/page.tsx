"use client";

import { AppShell } from "@/components/layout/AppShell";
import { DashboardView } from "@/components/admin/DashboardView";

export default function OverviewDashboardPage() {
  return (
    <AppShell>
      <DashboardView
        title="Tableau de bord — Depuis l'ouverture"
        subtitle="Vue d'ensemble de l'usage du système depuis sa mise en service."
        period="all"
      />
    </AppShell>
  );
}
