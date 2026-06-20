"use client";

import { useRef, useState } from "react";
import { Mic, Square, Loader2, ShieldCheck } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ConsultationSummary } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Step = "consent" | "recording" | "processing" | "review" | "done";

export default function ConsultationPage({ params }: { params: { id: string } }) {
  const appointmentId = params.id;

  const [step, setStep] = useState<Step>("consent");
  const [consentGiven, setConsentGiven] = useState(false);
  const [summary, setSummary] = useState<ConsultationSummary | null>(null);
  const [consultationId, setConsultationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];
    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.onstop = handleRecordingStop;
    recorder.start();
    mediaRecorderRef.current = recorder;
    setStep("recording");
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    mediaRecorderRef.current?.stream.getTracks().forEach((t) => t.stop());
  }

  async function handleRecordingStop() {
    setStep("processing");
    setError(null);
    const blob = new Blob(chunksRef.current, { type: "audio/webm" });

    const formData = new FormData();
    formData.append("audio", blob, "consultation.webm");

    try {
      const res = await fetch(
        `${API_URL}/consultations/${appointmentId}/audio?consent_given=${consentGiven}`,
        { method: "POST", body: formData }
      );
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setSummary(data.draft_summary);
      setConsultationId(data.consultation.id);
      setStep("review");
    } catch (err) {
      setError(
        "Échec de la transcription/résumé — vérifiez que le backend tourne et que GROQ_API_KEY est configuré (voir backend/README.md)."
      );
      setStep("consent");
    }
  }

  async function handleValidate() {
    if (!summary || !consultationId) return;
    await fetch(`${API_URL}/consultations/${consultationId}/validate`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ summary }),
    });
    setStep("done");
  }

  return (
    <AppShell>
      <h1 className="mb-1 font-display text-2xl font-semibold text-ink">Consultation</h1>
      <p className="mb-6 text-sm text-ink/60">Rendez-vous {appointmentId}</p>

      {error && <p className="mb-4 text-sm text-priority-urgence">{error}</p>}

      {step === "consent" && (
        <Card className="max-w-lg">
          <CardTitle>Avant d&apos;enregistrer</CardTitle>
          <label className="mt-3 flex items-start gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={consentGiven}
              onChange={(e) => setConsentGiven(e.target.checked)}
              className="mt-0.5"
            />
            Le patient a été informé et consent à l&apos;enregistrement audio de cette
            consultation, utilisé uniquement pour générer un résumé qui sera validé par le médecin.
          </label>
          <Button className="mt-4" disabled={!consentGiven} onClick={startRecording}>
            <Mic className="h-4 w-4" /> Démarrer l&apos;enregistrement
          </Button>
        </Card>
      )}

      {step === "recording" && (
        <Card className="max-w-lg">
          <div className="flex items-center gap-3">
            <span className="h-3 w-3 animate-pulse rounded-full bg-priority-urgence" />
            <p className="text-sm font-medium text-ink">Enregistrement en cours...</p>
          </div>
          <Button variant="danger" className="mt-4" onClick={stopRecording}>
            <Square className="h-4 w-4" /> Arrêter
          </Button>
        </Card>
      )}

      {step === "processing" && (
        <Card className="max-w-lg">
          <div className="flex items-center gap-3 text-sm text-ink/60">
            <Loader2 className="h-4 w-4 animate-spin" />
            Transcription puis résumé en cours (faster-whisper + agent IA local)...
          </div>
        </Card>
      )}

      {step === "review" && summary && (
        <Card className="max-w-2xl">
          <CardTitle>Résumé généré — à valider</CardTitle>
          <p className="mb-4 mt-1 text-xs text-amber-700">
            Suggestion de l&apos;IA. Corrigez librement avant validation : c&apos;est cette version qui sera archivée.
          </p>

          <div className="flex flex-col gap-3">
            <Field label="Résumé">
              <textarea
                value={summary.resume}
                onChange={(e) => setSummary({ ...summary, resume: e.target.value })}
                className="w-full rounded border border-line px-3 py-2 text-sm"
                rows={2}
              />
            </Field>
            <Field label="Diagnostic suggéré">
              <input
                value={summary.diagnostic_suggere}
                onChange={(e) => setSummary({ ...summary, diagnostic_suggere: e.target.value })}
                className="w-full rounded border border-line px-3 py-2 text-sm"
              />
            </Field>
            <Field label="Recommandation de suivi">
              <input
                value={summary.recommandation_suivi}
                onChange={(e) => setSummary({ ...summary, recommandation_suivi: e.target.value })}
                className="w-full rounded border border-line px-3 py-2 text-sm"
              />
            </Field>
            <Field label="Prescriptions">
              <ul className="flex flex-col gap-1 text-sm text-ink">
                {summary.prescriptions.map((p, i) => (
                  <li key={i} className="rounded bg-canvas px-2 py-1 font-mono text-xs">
                    {p.medicament} — {p.dosage} — {p.duree}
                  </li>
                ))}
                {summary.prescriptions.length === 0 && (
                  <li className="text-xs text-ink/40">Aucune prescription détectée.</li>
                )}
              </ul>
            </Field>
          </div>

          <Button className="mt-5" onClick={handleValidate}>
            <ShieldCheck className="h-4 w-4" /> Valider et archiver
          </Button>
        </Card>
      )}

      {step === "done" && (
        <Card className="max-w-lg">
          <p className="text-sm font-medium text-brand-deep">
            ✓ Consultation validée et archivée dans l&apos;historique du patient.
          </p>
        </Card>
      )}
    </AppShell>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-ink/50">
        {label}
      </label>
      {children}
    </div>
  );
}
