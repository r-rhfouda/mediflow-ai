"""
Abstraction du fournisseur LLM utilisé par les agents (triage en cas
ambigu, résumé de consultation, détection d'anomalies).

Par défaut : GroqProvider — gratuit, sans carte bancaire, et très rapide
(inférence sur puces LPU dédiées). Créer une clé sur console.groq.com/keys
(30 secondes, juste un email). Limites du tier gratuit largement
suffisantes pour un prototype/une démo : ~30 requêtes/min, 1000/jour sur
le modèle recommandé ci-dessous — voir backend/README.md pour le détail.

AnthropicProvider et OpenAIProvider sont fournis pour la flexibilité future
mais nécessitent une clé API PAYANTE — non nécessaires pour ce projet.
"""
import json
from typing import Protocol

from core.config import settings


class LLMProvider(Protocol):
    def complete(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        ...


class GroqProvider:
    """Gratuit, sans carte bancaire. Implémentation par défaut recommandée.
    API compatible OpenAI : on réutilise le SDK officiel `groq`."""

    def __init__(self) -> None:
        from groq import Groq  # import différé : évite une dépendance dure si non utilisé

        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY manquant dans .env — créez une clé gratuite sur "
                "https://console.groq.com/keys (voir backend/README.md)"
            )
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_model

    def complete(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"} if json_mode else None,
            temperature=0.2,
        )
        return response.choices[0].message.content


class AnthropicProvider:
    """PAYANT — optionnel. Activer uniquement si LLM_PROVIDER=anthropic."""

    def __init__(self) -> None:
        import anthropic  # nécessite `pip install anthropic` (non installé par défaut)

        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY manquant dans .env")
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def complete(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        message = self._client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text


class OpenAIProvider:
    """PAYANT — optionnel. Activer uniquement si LLM_PROVIDER=openai."""

    def __init__(self) -> None:
        import openai  # nécessite `pip install openai` (non installé par défaut)

        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY manquant dans .env")
        self._client = openai.OpenAI(api_key=settings.openai_api_key)

    def complete(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        completion = self._client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"} if json_mode else None,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content


def get_llm_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "groq":
        return GroqProvider()
    if provider == "anthropic":
        return AnthropicProvider()
    if provider == "openai":
        return OpenAIProvider()
    raise ValueError(f"LLM_PROVIDER inconnu : {provider}")


def safe_json_parse(raw: str) -> dict:
    """Les LLM ajoutent parfois du texte autour du JSON — on extrait la
    première accolade ouvrante/fermante pour rester robuste."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start : end + 1])
        raise
