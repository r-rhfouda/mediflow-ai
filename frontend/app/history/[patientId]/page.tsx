"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { FileText, Pill, Stethoscope } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardTitle } from "@/components/ui/Card";
import { api } from "@/lib/api";

interface HistoryData {
  appointments: any[];
  consultations: any[];
  prescriptions: any[];
  documents: any[];
}

export default function PatientHistoryPage({ params }: { params: { patientId: string } }) {
  const [history, setHistory] = useState<HistoryData | null>(null);

  useEffect(() => {
    api
      .getPatientHistory(params.patientId)
      .then((data) => setHistory(data as HistoryData))
      .catch(() => setHistory({ appointments: [], consultations: [], prescriptions: [], documents: [] }));
  }, [params.patientId]);

  if (!history) {
    return (
      <AppShell>
        <p className="text-sm text-ink/50">Chargement...</p>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <h1 className="mb-6 font-display text-2xl font-semibold text-ink">Historique patient</h1>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardTitle>
            <span className="flex items-center gap-2">
              <Stethoscope className="h-4 w-4" /> Consultations
            </span>
          </CardTitle>
          <div className="mt-3 flex flex-col divide-y divide-line">
            {history.consultations.map((c) => (
              <div key={c.id} className="py-3 text-sm">
                <p className="text-ink">{c.summary?.resume ?? c.transcript?.slice(0, 80)}</p>
                <p className="mt-1 text-xs text-ink/40">
                  {format(new Date(c.created_at), "d MMMM yyyy", { locale: fr })}
                  {c.validated_by_doctor ? " · validé par le médecin" : " · en attente de validation"}
                </p>
              </div>
            ))}
            {history.consultations.length === 0 && (
              <p className="py-6 text-sm text-ink/40">Aucune consultation enregistrée.</p>
            )}
          </div>
        </Card>

        <Card>
          <CardTitle>
            <span className="flex items-center gap-2">
              <Pill className="h-4 w-4" /> Médicaments prescrits
            </span>
          </CardTitle>
          <div className="mt-3 flex flex-col divide-y divide-line">
            {history.prescriptions.map((p) => (
              <div key={p.id} className="flex items-center justify-between py-2.5 text-sm">
                <span className="text-ink">{p.medication}</span>
                <span className="font-mono text-xs text-ink/50">
                  {p.dosage} · {p.duration}
                </span>
              </div>
            ))}
            {history.prescriptions.length === 0 && (
              <p className="py-6 text-sm text-ink/40">Aucune prescription.</p>
            )}
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardTitle>
            <span className="flex items-center gap-2">
              <FileText className="h-4 w-4" /> Documents
            </span>
          </CardTitle>
          <div className="mt-3 grid grid-cols-3 gap-3">
            {history.documents.map((d) => (
              <a
                key={d.id}
                href={d.file_url}
                target="_blank"
                rel="noreferrer"
                className="rounded border border-line p-3 text-xs text-ink hover:border-brand"
              >
                {d.document_type} <br />
                <span className="text-ink/40">
                  {format(new Date(d.uploaded_at), "d MMM yyyy", { locale: fr })}
                </span>
              </a>
            ))}
            {history.documents.length === 0 && (
              <p className="text-sm text-ink/40">Aucun document.</p>
            )}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
