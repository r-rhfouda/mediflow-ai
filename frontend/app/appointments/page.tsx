"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { Appointment } from "@/lib/types";

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [form, setForm] = useState({ patient_id: "", doctor_id: "", scheduled_at: "", reason: "" });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .listAppointments()
      .then((data) => setAppointments(data as Appointment[]))
      .catch(() => setAppointments([]));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const created = (await api.bookAppointment({
        ...form,
        scheduled_at: new Date(form.scheduled_at).toISOString(),
      })) as Appointment;
      setAppointments((prev) => [...prev, created]);
      setForm({ patient_id: "", doctor_id: "", scheduled_at: "", reason: "" });
    } catch (err) {
      alert("Erreur lors de la prise de RDV — vérifiez que le backend est lancé.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <h1 className="mb-6 font-display text-2xl font-semibold text-ink">Rendez-vous</h1>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card>
          <CardTitle>À venir</CardTitle>
          <div className="mt-3 flex flex-col divide-y divide-line">
            {appointments.length === 0 && (
              <p className="py-6 text-sm text-ink/40">
                Aucun rendez-vous (ou backend non connecté — voir le formulaire pour en créer un).
              </p>
            )}
            {appointments.map((a) => (
              <div key={a.id} className="flex items-center justify-between py-3">
                <div>
                  <p className="text-sm font-medium text-ink">
                    {format(new Date(a.scheduled_at), "EEEE d MMMM 'à' HH:mm", { locale: fr })}
                  </p>
                  <p className="text-xs text-ink/50">{a.reason}</p>
                </div>
                <Badge tone={a.status === "cancelled" ? "danger" : "neutral"}>{a.status}</Badge>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <CardTitle>Nouveau rendez-vous</CardTitle>
          <form onSubmit={handleSubmit} className="mt-3 flex flex-col gap-3">
            <input
              required
              placeholder="ID patient (UUID)"
              value={form.patient_id}
              onChange={(e) => setForm({ ...form, patient_id: e.target.value })}
              className="rounded border border-line px-3 py-2 text-sm outline-none focus:border-brand"
            />
            <input
              required
              placeholder="ID médecin (UUID)"
              value={form.doctor_id}
              onChange={(e) => setForm({ ...form, doctor_id: e.target.value })}
              className="rounded border border-line px-3 py-2 text-sm outline-none focus:border-brand"
            />
            <input
              required
              type="datetime-local"
              value={form.scheduled_at}
              onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })}
              className="rounded border border-line px-3 py-2 text-sm outline-none focus:border-brand"
            />
            <input
              placeholder="Motif"
              value={form.reason}
              onChange={(e) => setForm({ ...form, reason: e.target.value })}
              className="rounded border border-line px-3 py-2 text-sm outline-none focus:border-brand"
            />
            <Button type="submit" disabled={submitting}>
              Réserver
            </Button>
            <p className="text-xs text-ink/40">
              TODO (équipe) : remplacer les champs UUID par de vrais sélecteurs patient/médecin
              une fois l&apos;auth et les listes branchées.
            </p>
          </form>
        </Card>
      </div>
    </AppShell>
  );
}
