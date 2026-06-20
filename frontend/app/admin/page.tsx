"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardTitle } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { InsightsOut } from "@/lib/types";

const MOCK_INSIGHTS: InsightsOut = {
  avg_wait_time_minutes: { Urgence: 4, Grossesse: 12, "Âgé/chronique": 18, Normal: 35 },
  consultations_per_day: { "2026-06-15": 12, "2026-06-16": 9, "2026-06-17": 14 },
  top_diagnoses: { "Déséquilibre glycémique": 4, "Grippe saisonnière": 3, "Hypertension": 2 },
  top_medications: { Metformine: 4, Paracétamol: 3, Amoxicilline: 2 },
  priority_distribution: { Urgence: 1, Grossesse: 2, "Âgé/chronique": 1, Normal: 6 },
  no_show_rate: 0.08,
};

const PRIORITY_COLORS = ["#C0152F", "#6D28D9", "#B45309", "#0E6B5C"];

export default function AdminPage() {
  const [insights, setInsights] = useState<InsightsOut>(MOCK_INSIGHTS);
  const [usingMock, setUsingMock] = useState(true);

  useEffect(() => {
    api
      .getInsights()
      .then((data) => {
        setInsights(data as InsightsOut);
        setUsingMock(false);
      })
      .catch(() => {});
  }, []);

  const waitData = Object.entries(insights.avg_wait_time_minutes).map(([name, value]) => ({ name, value }));
  const priorityData = Object.entries(insights.priority_distribution).map(([name, value]) => ({ name, value }));
  const diagnosisData = Object.entries(insights.top_diagnoses).map(([name, value]) => ({ name, value }));

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl font-semibold text-ink">Tableau de bord</h1>
        {usingMock && (
          <span className="rounded bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
            Données de démonstration (backend non connecté)
          </span>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardTitle>Temps d&apos;attente moyen par priorité (min)</CardTitle>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={waitData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E4E1" />
                <XAxis dataKey="name" fontSize={12} stroke="#161B22" />
                <YAxis fontSize={12} stroke="#161B22" />
                <Tooltip />
                <Bar dataKey="value" fill="#0E6B5C" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardTitle>Répartition des patients par priorité</CardTitle>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={priorityData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
                  {priorityData.map((_, i) => (
                    <Cell key={i} fill={PRIORITY_COLORS[i % PRIORITY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardTitle>Diagnostics les plus fréquents</CardTitle>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={diagnosisData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E4E1" />
                <XAxis type="number" fontSize={12} />
                <YAxis dataKey="name" type="category" width={160} fontSize={11} />
                <Tooltip />
                <Bar dataKey="value" fill="#0A4A40" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="flex flex-col items-center justify-center">
          <CardTitle>Taux de no-show</CardTitle>
          <p className="mt-4 font-display text-5xl font-semibold text-brand">
            {(insights.no_show_rate * 100).toFixed(0)}%
          </p>
          <p className="mt-1 text-xs text-ink/50">des rendez-vous planifiés</p>
        </Card>
      </div>
    </AppShell>
  );
}
