"""
Schémas Pydantic — un seul endroit pour toutes les formes de données
échangées entre le frontend et l'API. Garder ces modèles alignés avec
database/schema.sql.
"""
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Priority = Literal[1, 2, 3, 4]


# ---------------- Patients ----------------
class PatientContext(BaseModel):
    """Tout ce dont le triage_agent a besoin pour évaluer une priorité."""
    patient_id: str
    date_of_birth: date
    is_pregnant: bool = False
    chronic_conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)


# ---------------- File d'attente / Triage ----------------
class CheckInRequest(BaseModel):
    appointment_id: str
    patient_id: str
    motif_libre: str
    urgence_declaree: bool = False


class TriageResult(BaseModel):
    priority: Priority
    reason: str
    confidence: float = 1.0
    needs_human_review: bool = False


class QueueEntryOut(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    priority: Priority
    priority_reason: str
    needs_human_review: bool
    arrival_time: datetime
    status: Literal["waiting", "in_consultation", "done", "left"]
    ticket_number: int


# ---------------- Rendez-vous ----------------
class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    scheduled_at: datetime
    reason: Optional[str] = None


class AppointmentOut(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    scheduled_at: datetime
    reason: Optional[str]
    status: str
    google_event_id: Optional[str] = None


# ---------------- Consultations ----------------
class PrescriptionItem(BaseModel):
    medicament: str
    dosage: Optional[str] = None
    duree: Optional[str] = None


class ConsultationSummary(BaseModel):
    resume: str
    symptomes: list[str] = Field(default_factory=list)
    diagnostic_suggere: str
    prescriptions: list[PrescriptionItem] = Field(default_factory=list)
    recommandation_suivi: str
    needs_human_review: bool = False


class ConsultationValidateRequest(BaseModel):
    """Le médecin peut corriger le résumé généré avant qu'il devienne définitif."""
    summary: ConsultationSummary


# ---------------- Anomalies ----------------
class AnomalyAlert(BaseModel):
    alert_type: str
    severity: Literal["low", "medium", "high"]
    message: str
    suggested_action: str


# ---------------- Admin / BI ----------------
class InsightsOut(BaseModel):
    avg_wait_time_minutes: dict[str, float]   # par niveau de priorité
    consultations_per_day: dict[str, int]
    top_diagnoses: dict[str, int]
    top_medications: dict[str, int]
    priority_distribution: dict[str, int]
    no_show_rate: float
