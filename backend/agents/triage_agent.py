"""
Triage Agent — détermine la priorité d'un patient à son arrivée.

Logique volontairement hybride :
  1. Règles déterministes (rapides, gratuites, explicables) couvrent les
     cas normaux : urgence déclarée, grossesse, âge/pathologie chronique.
  2. Si aucune règle ne s'applique mais que le motif libre semble
     préoccupant ("cas hors norme"), on demande son avis à un LLM local
     (Groq, gratuit) — avec un score de confiance et, si la confiance
     est faible, needs_human_review=True pour que l'humain tranche.

Important : ceci est une AIDE à la décision, pas une décision automatique
irréversible. La réceptionniste peut toujours surclasser/déclasser un
patient manuellement dans l'UI.
"""
from datetime import date

from agents.base_agent import get_llm_provider, safe_json_parse
from models.schemas import PatientContext, TriageResult

# Mots-clés simples indiquant une urgence vitale potentielle.
# Volontairement basique : c'est un filet de sécurité avant le LLM, pas un
# outil de diagnostic médical.
EMERGENCY_KEYWORDS = [
    "douleur thoracique", "douleur dans la poitrine",
    "difficulté à respirer", "essoufflement sévère",
    "saignement important", "hémorragie",
    "perte de connaissance", "convulsion",
    "paralysie", "ne sent plus", "ne peut plus parler",
]

ELDERLY_AGE_THRESHOLD = 65

TRIAGE_SYSTEM_PROMPT = """Tu es un assistant de triage dans un cabinet médical.
Tu dois classer un motif de consultation décrit librement par un patient
dans une des 4 catégories de priorité suivantes, et UNIQUEMENT répondre en JSON :

1 = urgence vitale possible (douleur thoracique, difficulté respiratoire grave, etc.)
2 = à prioriser modérément (symptômes combinés inhabituels, douleur intense persistante)
3 = standard mais à surveiller
4 = normal, aucun signal d'alerte

Réponds STRICTEMENT avec ce format JSON, rien d'autre :
{"priority": <1-4>, "reason": "<courte explication en français>", "confidence": <0.0-1.0>}

Si tu n'es pas sûr, mets une confidence basse plutôt que d'inventer une certitude."""


def _calculate_age(date_of_birth: date) -> int:
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def _matches_emergency_keywords(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in EMERGENCY_KEYWORDS)


def evaluate_priority(
    patient: PatientContext, motif_libre: str, urgence_declaree: bool
) -> TriageResult:
    # --- Règle 1 : urgence ---
    if urgence_declaree or _matches_emergency_keywords(motif_libre):
        return TriageResult(
            priority=1,
            reason="Urgence déclarée ou mots-clés d'urgence détectés dans le motif.",
            confidence=1.0,
            needs_human_review=False,
        )

    # --- Règle 2 : grossesse ---
    if patient.is_pregnant:
        return TriageResult(
            priority=2,
            reason="Patiente enceinte.",
            confidence=1.0,
            needs_human_review=False,
        )

    # --- Règle 3 : âgé / pathologie chronique déclarée ---
    age = _calculate_age(patient.date_of_birth)
    if age >= ELDERLY_AGE_THRESHOLD or patient.chronic_conditions:
        reason = (
            f"Patient âgé ({age} ans)" if age >= ELDERLY_AGE_THRESHOLD
            else "Pathologie chronique déclarée au dossier"
        )
        return TriageResult(priority=3, reason=reason, confidence=1.0, needs_human_review=False)

    # --- Règle 4 (par défaut) : normal ---
    # Avant de conclure "normal", on vérifie si le motif libre semble
    # mériter un second avis (cas hors norme).
    if _seems_ambiguous(motif_libre):
        return _ask_llm_fallback(motif_libre)

    return TriageResult(
        priority=4,
        reason="Aucun facteur de priorité détecté.",
        confidence=1.0,
        needs_human_review=False,
    )


def _seems_ambiguous(motif_libre: str) -> bool:
    """Heuristique simple : un motif un peu long avec plusieurs symptômes
    combinés vaut la peine d'être passé au LLM plutôt que classé "normal"
    par défaut. Évite d'appeler le LLM pour "contrôle de routine"."""
    word_count = len(motif_libre.split())
    return word_count >= 6


def _ask_llm_fallback(motif_libre: str) -> TriageResult:
    try:
        llm = get_llm_provider()
        raw = llm.complete(TRIAGE_SYSTEM_PROMPT, motif_libre, json_mode=True)
        data = safe_json_parse(raw)
        confidence = float(data.get("confidence", 0.5))
        return TriageResult(
            priority=int(data["priority"]),
            reason=data.get("reason", "Évalué par l'agent IA."),
            confidence=confidence,
            needs_human_review=confidence < 0.7,
        )
    except Exception:
        # Si le LLM n'est pas joignable (clé Groq manquante, quota dépassé, etc.), on
        # ne bloque JAMAIS le check-in : on classe en priorité 3 par
        # prudence et on demande une revue humaine.
        return TriageResult(
            priority=3,
            reason="Agent IA indisponible — classé par prudence, à valider par la réception.",
            confidence=0.0,
            needs_human_review=True,
        )
