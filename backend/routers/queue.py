"""
Routes de la file d'attente — le cœur fonctionnel du sujet : un patient
arrivé en premier n'est pas forcément servi en premier.
"""
from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException

from agents.triage_agent import evaluate_priority
from db.database import get_supabase
from models.schemas import CheckInRequest, PatientContext, QueueAlertOut, QueueEntryOut, TriageResult

router = APIRouter(prefix="/queue", tags=["queue"])

# Seuil au-delà duquel un patient en attente déclenche une alerte côté réception.
LONG_WAIT_THRESHOLD_MINUTES = 30


@router.get("", response_model=list[QueueEntryOut])
def list_queue():
    sb = get_supabase()
    rows = (
        sb.table("queue_entries")
        .select("*, patients(profiles(full_name))")
        .eq("status", "waiting")
        .order("priority", desc=False)
        .order("arrival_time", desc=False)
        .execute()
        .data
    )
    return [
        QueueEntryOut(
            id=row["id"],
            patient_id=row["patient_id"],
            patient_name=row.get("patients", {}).get("profiles", {}).get("full_name", "Inconnu"),
            priority=row["priority"],
            priority_reason=row["priority_reason"] or "",
            needs_human_review=row["needs_human_review"],
            arrival_time=row["arrival_time"],
            status=row["status"],
            ticket_number=row["ticket_number"],
        )
        for row in rows
    ]


@router.get("/alerts", response_model=list[QueueAlertOut])
def list_long_wait_alerts():
    """Renvoie les patients toujours en attente depuis plus de
    LONG_WAIT_THRESHOLD_MINUTES — pensé pour être interrogé périodiquement
    par le frontend afin d'alerter la réception qu'un patient a été oublié,
    indépendamment de sa priorité initiale."""
    sb = get_supabase()
    rows = (
        sb.table("queue_entries")
        .select("*, patients(profiles(full_name))")
        .eq("status", "waiting")
        .execute()
        .data
    )

    now = datetime.now(timezone.utc)
    alerts: list[QueueAlertOut] = []
    for row in rows:
        arrival = datetime.fromisoformat(row["arrival_time"].replace("Z", "+00:00"))
        wait_minutes = int((now - arrival).total_seconds() / 60)
        if wait_minutes >= LONG_WAIT_THRESHOLD_MINUTES:
            alerts.append(
                QueueAlertOut(
                    entry_id=row["id"],
                    patient_id=row["patient_id"],
                    patient_name=row.get("patients", {}).get("profiles", {}).get("full_name", "Inconnu"),
                    priority=row["priority"],
                    wait_minutes=wait_minutes,
                    arrival_time=row["arrival_time"],
                )
            )
    return sorted(alerts, key=lambda a: a.wait_minutes, reverse=True)


@router.post("/checkin", response_model=TriageResult)
def checkin(payload: CheckInRequest):
    sb = get_supabase()

    patient_row = sb.table("patients").select("*").eq("id", payload.patient_id).single().execute().data
    if not patient_row:
        raise HTTPException(status_code=404, detail="Patient introuvable.")

    patient = PatientContext(
        patient_id=payload.patient_id,
        date_of_birth=date.fromisoformat(patient_row["date_of_birth"]),
        is_pregnant=patient_row.get("is_pregnant", False),
        chronic_conditions=patient_row.get("chronic_conditions") or [],
        allergies=patient_row.get("allergies") or [],
    )

    result = evaluate_priority(patient, payload.motif_libre, payload.urgence_declaree)

    sb.table("queue_entries").insert(
        {
            "appointment_id": payload.appointment_id,
            "patient_id": payload.patient_id,
            "priority": result.priority,
            "priority_reason": result.reason,
            "needs_human_review": result.needs_human_review,
            "status": "waiting",
        }
    ).execute()
    sb.table("appointments").update({"status": "checked_in"}).eq("id", payload.appointment_id).execute()

    return result


@router.patch("/{entry_id}/call")
def call_patient(entry_id: str):
    sb = get_supabase()
    sb.table("queue_entries").update(
        {"status": "in_consultation", "called_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", entry_id).execute()
    return {"status": "ok"}


@router.patch("/{entry_id}/done")
def finish_patient(entry_id: str):
    sb = get_supabase()
    sb.table("queue_entries").update({"status": "done"}).eq("id", entry_id).execute()
    return {"status": "ok"}


@router.patch("/{entry_id}/override")
def override_priority(entry_id: str, new_priority: int, reason: str):
    """Supervision humaine : la réception peut toujours corriger une
    priorité calculée par l'agent IA."""
    if new_priority not in (1, 2, 3, 4):
        raise HTTPException(status_code=400, detail="Priorité invalide (1-4 attendu).")
    sb = get_supabase()
    sb.table("queue_entries").update(
        {"priority": new_priority, "priority_reason": f"[Override manuel] {reason}", "needs_human_review": False}
    ).eq("id", entry_id).execute()
    sb.table("audit_log").insert(
        {
            "related_table": "queue_entries",
            "related_id": entry_id,
            "event_type": "priority_overridden",
            "severity": "low",
            "message": f"Priorité changée manuellement en {new_priority} : {reason}",
        }
    ).execute()
    return {"status": "ok"}
