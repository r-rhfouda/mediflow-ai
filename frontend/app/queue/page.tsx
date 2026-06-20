"use client";

import { useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";
import { AlertTriangle, PhoneCall, CheckCircle2 } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { PriorityBadge } from "@/components/queue/PriorityBadge";
import { api } from "@/lib/api";
import { QueueEntry, Priority } from "@/lib/types";

// Données de repli affichées si le backend n'est pas encore lancé — permet
// de travailler sur l'UI sans dépendre de FastAPI. À retirer une fois
// l'intégration réelle terminée (voir docs/PROJECT_PLAN.md, Jour 5).
const MOCK_QUEUE: QueueEntry[] = [
  { id: "1", patient_id: "p1", patient_name: "Laila Cherkaoui", priority: 1, priority_reason: "Urgence déclarée : douleur thoracique", needs_human_review: false, arrival_time: new Date(Date.now() - 10 * 60000).toISOString(), status: "waiting", ticket_number: 14 },
  { id: "2", patient_id: "p2", patient_name: "Salma Tazi", priority: 2, priority_reason: "Patiente enceinte", needs_human_review: false, arrival_time: new Date(Date.now() - 50 * 60000).toISOString(), status: "waiting", ticket_number: 11 },
  { id: "3", patient_id: "p3", patient_name: "Mohamed Senhaji", priority: 3, priority_reason: "Patient âgé (74 ans) avec pathologie chronique", needs_human_review: false, arrival_time: new Date(Date.now() - 40 * 60000).toISOString(), status: "waiting", ticket_number: 12 },
  { id: "4", patient_id: "p4", patient_name: "Youssef Amrani", priority: 2, priority_reason: "Symptômes combinés jugés préoccupants par l'agent IA (confiance modérée)", needs_human_review: true, arrival_time: new Date(Date.now() - 5 * 60000).toISOString(), status: "waiting", ticket_number: 15 },
  { id: "5", patient_id: "p5", patient_name: "Karim Idrissi", priority: 4, priority_reason: "Aucun facteur de priorité détecté", needs_human_review: false, arrival_time: new Date(Date.now() - 60 * 60000).toISOString(), status: "waiting", ticket_number: 10 },
];

const RAIL_COLOR: Record<Priority, string> = {
  1: "bg-priority-urgence",
  2: "bg-priority-grossesse",
  3: "bg-priority-senior",
  4: "bg-priority-normal",
};

export default function QueuePage() {
  const [entries, setEntries] = useState<QueueEntry[]>(MOCK_QUEUE);
  const [usingMock, setUsingMock] = useState(true);

  useEffect(() => {
    api
      .getQueue()
      .then((data) => {
        setEntries(data as QueueEntry[]);
        setUsingMock(false);
      })
      .catch(() => {
        // Backend pas encore lancé / pas encore branché → on garde le mock.
      });
  }, []);

  async function handleCall(id: string) {
    await api.callPatient(id).catch(() => null);
    setEntries((prev) => prev.map((e) => (e.id === id ? { ...e, status: "in_consultation" } : e)));
  }

  async function handleDone(id: string) {
    await api.finishPatient(id).catch(() => null);
    setEntries((prev) => prev.filter((e) => e.id !== id));
  }

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">File d&apos;attente</h1>
          <p className="text-sm text-ink/60">
            Triée par priorité, puis par heure d&apos;arrivée — pas par ordre d&apos;arrivée seul.
          </p>
        </div>
        {usingMock && (
          <span className="rounded bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
            Données de démonstration (backend non connecté)
          </span>
        )}
      </div>

      <div className="flex flex-col gap-2">
        {entries.map((entry) => (
          <Card key={entry.id} className="flex items-center gap-4 p-0 overflow-hidden">
            <div className={`h-16 w-1.5 shrink-0 ${RAIL_COLOR[entry.priority]}`} />

            <div className="flex flex-1 items-center justify-between py-3 pr-5">
              <div className="flex items-center gap-4">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${
                    entry.status === "waiting" ? "bg-brand status-dot-waiting" : "bg-line"
                  }`}
                />
                <span className="font-mono text-sm text-ink/50">#{String(entry.ticket_number).padStart(3, "0")}</span>
                <div>
                  <p className="font-body text-sm font-semibold text-ink">{entry.patient_name}</p>
                  <p className="text-xs text-ink/50">{entry.priority_reason}</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                {entry.needs_human_review && (
                  <span title="L'agent IA recommande une vérification humaine">
                    <AlertTriangle className="h-4 w-4 text-amber-600" />
                  </span>
                )}
                <PriorityBadge priority={entry.priority} />
                <span className="w-28 text-right text-xs text-ink/50">
                  arrivé {formatDistanceToNow(new Date(entry.arrival_time), { locale: fr, addSuffix: true })}
                </span>

                {entry.status === "waiting" ? (
                  <Button variant="secondary" onClick={() => handleCall(entry.id)}>
                    <PhoneCall className="h-3.5 w-3.5" /> Appeler
                  </Button>
                ) : (
                  <Button variant="ghost" onClick={() => handleDone(entry.id)}>
                    <CheckCircle2 className="h-3.5 w-3.5" /> Terminer
                  </Button>
                )}
              </div>
            </div>
          </Card>
        ))}

        {entries.length === 0 && (
          <p className="py-12 text-center text-sm text-ink/40">Aucun patient en attente.</p>
        )}
      </div>
    </AppShell>
  );
}
