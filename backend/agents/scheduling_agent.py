"""
Scheduling Agent — création/mise à jour des rendez-vous et synchronisation
avec Google Calendar.

Google Calendar API est gratuit pour ce volume d'usage (quota largement
suffisant pour un cabinet médical de démonstration). Nécessite un projet
Google Cloud (gratuit) + identifiants OAuth2 — voir backend/README.md.

Si les identifiants Google ne sont pas configurés, la synchronisation est
simplement ignorée (le RDV est créé en base normalement) : ça ne doit
jamais bloquer la prise de RDV pendant le développement.
"""
from datetime import datetime, timedelta

from core.config import settings
from db.database import get_supabase


def create_appointment(patient_id: str, doctor_id: str, scheduled_at: datetime, reason: str | None) -> dict:
    sb = get_supabase()

    conflict = (
        sb.table("appointments")
        .select("id")
        .eq("doctor_id", doctor_id)
        .eq("scheduled_at", scheduled_at.isoformat())
        .neq("status", "cancelled")
        .execute()
    )
    if conflict.data:
        raise ValueError("Ce créneau est déjà réservé pour ce médecin.")

    result = (
        sb.table("appointments")
        .insert(
            {
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "scheduled_at": scheduled_at.isoformat(),
                "reason": reason,
                "status": "scheduled",
            }
        )
        .execute()
    )
    appointment = result.data[0]

    event_id = _sync_to_google_calendar(appointment, scheduled_at, reason)
    if event_id:
        sb.table("appointments").update({"google_event_id": event_id}).eq(
            "id", appointment["id"]
        ).execute()
        appointment["google_event_id"] = event_id

    return appointment


def _sync_to_google_calendar(appointment: dict, scheduled_at: datetime, reason: str | None) -> str | None:
    if not settings.google_client_id or not settings.google_client_secret:
        # Pas configuré → on ne bloque pas le RDV, on log simplement.
        print("[scheduling_agent] Google Calendar non configuré — RDV créé sans sync.")
        return None

    try:
        from googleapiclient.discovery import build

        from db.google_oauth import get_credentials_for_doctor  # voir routers/calendar.py

        creds = get_credentials_for_doctor(appointment["doctor_id"])
        service = build("calendar", "v3", credentials=creds)
        event = {
            "summary": f"Consultation — {reason or 'RDV patient'}",
            "start": {"dateTime": scheduled_at.isoformat()},
            "end": {"dateTime": (scheduled_at + timedelta(minutes=30)).isoformat()},
        }
        created = service.events().insert(calendarId="primary", body=event).execute()
        return created.get("id")
    except Exception as exc:  # pragma: no cover — dépend d'une intégration externe
        print(f"[scheduling_agent] Échec de la synchronisation Google Calendar : {exc}")
        return None
