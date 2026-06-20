"""
Connexion d'un médecin à son agenda Google (OAuth2, gratuit).

Flux :
  1. Le médecin clique "Connecter mon agenda Google" dans /profile (frontend)
     → redirige vers GET /calendar/oauth/start?doctor_id=...
  2. L'utilisateur valide l'accès sur l'écran Google standard.
  3. Google redirige vers GOOGLE_REDIRECT_URI (= /calendar/oauth/callback),
     qui échange le code contre un refresh_token et le stocke en base.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

from core.config import settings
from db.google_oauth import SCOPES, save_credentials

router = APIRouter(prefix="/calendar", tags=["calendar"])


def _build_flow() -> Flow:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=503,
            detail="Google Calendar non configuré (GOOGLE_CLIENT_ID/SECRET manquants).",
        )
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }
    return Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=settings.google_redirect_uri)


@router.get("/oauth/start")
def oauth_start(doctor_id: str = Query(...)):
    flow = _build_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",   # force l'émission d'un refresh_token à chaque fois
        state=doctor_id,    # on retrouve le médecin au retour via ce paramètre
    )
    return RedirectResponse(auth_url)


@router.get("/oauth/callback")
def oauth_callback(code: str, state: str):
    doctor_id = state
    flow = _build_flow()
    flow.fetch_token(code=code)
    save_credentials(doctor_id, flow.credentials)
    # Redirige vers la page profil du frontend avec une confirmation visuelle.
    return RedirectResponse(f"{settings.frontend_origin}/profile?calendar_connected=true")
