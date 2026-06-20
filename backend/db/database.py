"""
Client Supabase partagé.
Utilise la clé service_role : elle contourne le RLS, donc CE CLIENT NE DOIT
JAMAIS être exposé ou réutilisé côté frontend. Le frontend utilise sa propre
clé "anon" (voir frontend/lib/supabaseClient.ts) qui respecte le RLS.
"""
from functools import lru_cache

from supabase import Client, create_client

from core.config import settings


@lru_cache
def get_supabase() -> Client:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY manquants dans .env — "
            "voir backend/.env.example"
        )
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
