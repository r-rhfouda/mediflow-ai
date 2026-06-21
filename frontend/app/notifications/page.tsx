"use client";

import { useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";
import { AlertTriangle, BellRing, CheckCircle2 } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardTitle } from "@/components/ui/Card";
import { PriorityBadge } from "@/components/queue/PriorityBadge";
import { api } from "@/lib/api";
import { Priority } from "@/lib/types";

interface QueueAlert {
  entry_id: string;
  patient_id: string;
  patient_name: string;
  priority: Priority;
  wait_minutes: number;
  arrival_time: string;
}

// Repli affiché si le backend n'est pas encore lancé — supprimé
// automatiquement dès que /queue/alerts répond.
const MOCK_ALERTS: QueueAlert[] = [
  {
    entry_id: "5",
    patient_id: "p5",
    patient_name: "Karim Idrissi",
    priority: 4,
    wait_minutes: 60,
    arrival_time: new Date(Date.now() - 60 * 60000).toISOString(),
  },
  {
    entry_id: "2",
    patient_id: "p2",
    patient_name: "Salma Tazi",
    priority: 2,
    wait_minutes: 50,
    arrival_time: new Date(Date.now() - 50 * 60000).toISOString(),
  },
];

const POLL_INTERVAL_MS = 30_000; // revérifie toutes les 30 secondes

export default function NotificationsPage() {
  const [alerts, setAlerts] = useState<QueueAlert[]>(MOCK_ALERTS);
  const [usingMock, setUsingMock] = useState(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchAlerts() {
      try {
        const data = (await api.getQueueAlerts()) as QueueAlert[];
        if (!cancelled) {
          setAlerts(data);
          setUsingMock(false);
          setLastChecked(new Date());
        }
      } catch {
        // Backend pas encore lancé — on garde les données de démo affichées.
      }
    }

    fetchAlerts();
    const interval = setInterval(fetchAlerts, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Notifications</h1>
          <p className="text-sm text-ink/60">
            Patients en attente depuis plus de 30 minutes, tous niveaux de priorité confondus.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {usingMock && (
            <span className="rounded bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
              Données de démonstration
            </span>
          )}
          {!usingMock && lastChecked && (
            <span className="flex items-center gap-1.5 text-xs text-ink/40">
              <BellRing className="h-3.5 w-3.5" />
              vérifié {formatDistanceToNow(lastChecked, { locale: fr, addSuffix: true })}
            </span>
          )}
        </div>
      </div>

      {alerts.length === 0 ? (
        <Card className="flex flex-col items-center gap-2 py-12 text-center">
          <CheckCircle2 className="h-8 w-8 text-priority-normal" />
          <p className="text-sm font-medium text-ink">Aucune alerte</p>
          <p className="text-xs text-ink/50">Tous les patients en attente le sont depuis moins de 30 minutes.</p>
        </Card>
      ) : (
        <div className="flex flex-col gap-2">
          {alerts.map((alert) => (
            <Card key={alert.entry_id} className="flex items-center justify-between gap-4 border-l-4 border-l-priority-urgence p-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 shrink-0 text-priority-urgence" />
                <div>
                  <p className="text-sm font-semibold text-ink">{alert.patient_name}</p>
                  <p className="text-xs text-ink/50">
                    Arrivé(e) {formatDistanceToNow(new Date(alert.arrival_time), { locale: fr, addSuffix: true })}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <PriorityBadge priority={alert.priority} />
                <span className="rounded bg-priority-urgence/10 px-2.5 py-1 font-mono text-xs font-semibold text-priority-urgence">
                  {alert.wait_minutes} min d&apos;attente
                </span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}
