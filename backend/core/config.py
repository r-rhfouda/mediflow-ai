"""
Configuration centralisée du backend.
Toutes les variables d'environnement passent par ici — aucun appel direct
à os.environ ailleurs dans le code, pour rester facile à tester.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"
    frontend_origin: str = "http://localhost:3000"

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""

    # Google Calendar
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/calendar/oauth/callback"

    # LLM — "groq" (gratuit, recommandé) | "anthropic" | "openai" (payants, optionnels)
    llm_provider: str = "groq"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Transcription — "local" (faster-whisper, gratuit) | "openai" (payant, optionnel)
    transcription_provider: str = "local"
    whisper_model_size: str = "small"


settings = Settings()
