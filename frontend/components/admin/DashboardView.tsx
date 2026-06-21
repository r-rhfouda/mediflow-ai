"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardTitle } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { InsightsOut } from "@/lib/types";

export type DashboardPeriod = "day" | "month" | "all";

const MOCK_INSIGHTS: InsightsOut = {
  avg_wait_time_minutes: { Urgence: 4, Grossesse: 12, "Âgé/chronique": 18, Normal: 35 },
  consultations_per_day: { "2026-06-15": 12, "2026-06-16": 9, "2026-06-17": 14 },
  top_diagnoses: { "Déséquilibre glycémique": 4, "Grippe saisonnière": 3, "Hypertension": 2 },
  top_medications: { Metformine: 4, Paracétamol: 3, Amoxicilline: 2 },
  priority_distribution: { Urgence: 1, Grossesse: 2, "Âgé/chronique": 1, Normal: 6 },
  no_show_rate: 0.08,
  avg_consultation_duration_minutes: 17.5,
  ai_summary_edit_rate: 0.22,
  hourly_distribution: { "08h": 2, "09h": 5, "10h": 7, "11h": 6, "14h": 4, "15h": 8, "16h": 5, "17h": 3 },
};

const PRIORITY_COLORS = ["#C0152F", "#8B5CF6", "#C2780A", "#D6608C"];

interface DashboardViewProps {
  title: string;
  subtitle: string;
  period: DashboardPeriod;
}

export function DashboardView({ title, subtitle, period }: DashboardViewProps) {
  const [insights, setInsights] = useState<InsightsOut>(MOCK_INSIGHTS);
  const [usingMock, setUsingMock] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .getInsights(period)
      .then((data) => {
        setInsights(data as InsightsOut);
        setUsingMock(false);
      })
      .catch(() => {
        setUsingMock(true);
      })
      .finally(() => setLoading(false));
  }, [period]);

  const waitData = Object.entries(insights.avg_wait_time_minutes).map(([name, value]) => ({ name, value }));
  const priorityData = Object.entries(insights.priority_distribution).map(([name, value]) => ({ name, value }));
  const diagnosisData = Object.entries(insights.top_diagnoses).map(([name, value]) => ({ name, value }));
  const hourlyData = Object.entries(insights.hourly_distribution).map(([name, value]) => ({ name, value }));

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">{title}</h1>
          <p className="text-sm text-ink/60">{subtitle}</p>
        </div>
        {usingMock && (
          <span className="rounded bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
            {loading ? "Chargement..." : "Données de démonstration (backend non connecté)"}
          </span>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardTitle>Temps d&apos;attente moyen par priorité (min)</CardTitle>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={waitData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F3D9E4" />
                <XAxis dataKey="name" fontSize={12} stroke="#3B2832" />
                <YAxis fontSize={12} stroke="#3B2832" />
                <Tooltip />
                <Bar dataKey="value" fill="#D6608C" radius={[4, 4, 0, 0]} />
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
                <CartesianGrid strokeDasharray="3 3" stroke="#F3D9E4" />
                <XAxis type="number" fontSize={12} />
                <YAxis dataKey="name" type="category" width={160} fontSize={11} />
                <Tooltip />
                <Bar dataKey="value" fill="#A8456B" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardTitle>Affluence par heure de la journée</CardTitle>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F3D9E4" />
                <XAxis dataKey="name" fontSize={11} stroke="#3B2832" />
                <YAxis fontSize={12} stroke="#3B2832" />
                <Tooltip />
                <Bar dataKey="value" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
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

        <Card className="flex flex-col items-center justify-center">
          <CardTitle>Durée moyenne de consultation</CardTitle>
          <p className="mt-4 font-display text-5xl font-semibold text-brand">
            {insights.avg_consultation_duration_minutes != null
              ? `${insights.avg_consultation_duration_minutes.toFixed(0)} min`
              : "—"}
          </p>
          <p className="mt-1 text-xs text-ink/50">par patient</p>
        </Card>

        <Card className="flex flex-col items-center justify-center lg:col-span-2">
          <CardTitle>Taux de correction des résumés IA par le médecin</CardTitle>
          <p className="mt-4 font-display text-5xl font-semibold text-brand">
            {(insights.ai_summary_edit_rate * 100).toFixed(0)}%
          </p>
          <p className="mt-1 text-xs text-ink/50">
            des résumés générés par l&apos;IA ont nécessité une relecture attentive — indicateur de fiabilité de l&apos;agent
          </p>
        </Card>
      </div>
    </div>
  );
}
