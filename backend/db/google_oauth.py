"""
Stockage et récupération des credentials OAuth2 Google Calendar, par médecin.
Chaque médecin connecte son propre agenda Google une seule fois (flow OAuth2
géré dans routers/calendar.py) ; le refresh_token est ensuite réutilisé pour
créer/modifier des événements sans repasser par l'écran de connexion.
"""
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials

from core.config import settings
from db.database import get_supabase

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def save_credentials(doctor_id: str, credentials: Credentials) -> None:
    sb = get_supabase()
    sb.table("google_credentials").upsert(
        {
            "doctor_id": doctor_id,
            "refresh_token": credentials.refresh_token,
            "access_token": credentials.token,
            "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    ).execute()


def get_credentials_for_doctor(doctor_id: str) -> Credentials:
    sb = get_supabase()
    row = sb.table("google_credentials").select("*").eq("doctor_id", doctor_id).single().execute()
    data = row.data
    if not data:
        raise RuntimeError(
            f"Aucun agenda Google connecté pour le médecin {doctor_id}. "
            "Demandez-lui de se connecter via /calendar/oauth/start."
        )

    creds = Credentials(
        token=data["access_token"],
        refresh_token=data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES,
    )
    return creds
