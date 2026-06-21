// Types partagés — garder alignés avec backend/models/schemas.py

export type Priority = 1 | 2 | 3 | 4;

export const PRIORITY_LABELS: Record<Priority, string> = {
  1: "Urgence",
  2: "Grossesse",
  3: "Âgé / chronique",
  4: "Normal",
};

export const PRIORITY_COLOR_CLASS: Record<Priority, string> = {
  1: "bg-priority-urgence",
  2: "bg-priority-grossesse",
  3: "bg-priority-senior",
  4: "bg-priority-normal",
};

export interface QueueEntry {
  id: string;
  patient_id: string;
  patient_name: string;
  priority: Priority;
  priority_reason: string;
  needs_human_review: boolean;
  arrival_time: string;
  status: "waiting" | "in_consultation" | "done" | "left";
  ticket_number: number;
}

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  scheduled_at: string;
  reason: string | null;
  status: string;
  google_event_id?: string | null;
}

export interface PrescriptionItem {
  medicament: string;
  dosage?: string;
  duree?: string;
}

export interface ConsultationSummary {
  resume: string;
  symptomes: string[];
  diagnostic_suggere: string;
  prescriptions: PrescriptionItem[];
  recommandation_suivi: string;
  needs_human_review: boolean;
}

export interface InsightsOut {
  avg_wait_time_minutes: Record<string, number>;
  consultations_per_day: Record<string, number>;
  top_diagnoses: Record<string, number>;
  top_medications: Record<string, number>;
  priority_distribution: Record<string, number>;
  no_show_rate: number;
  avg_consultation_duration_minutes: number | null;
  ai_summary_edit_rate: number;
  hourly_distribution: Record<string, number>;
}
