"""
Summarization Agent — transforme la transcription brute d'une consultation
en note structurée (façon SOAP, adaptée en français), avec une liste de
prescriptions mentionnées.

Le résultat est TOUJOURS présenté en édition au médecin avant d'être
sauvegardé comme définitif (voir routers/consultations.py,
ConsultationValidateRequest) — l'IA assiste, elle ne remplace jamais le
jugement médical.
"""
from agents.base_agent import get_llm_provider, safe_json_parse
from models.schemas import ConsultationSummary

SUMMARY_SYSTEM_PROMPT = """Tu es un assistant médical qui aide à structurer le
compte-rendu d'une consultation à partir de sa transcription brute.

Réponds STRICTEMENT en JSON avec ce format, rien d'autre, en français :
{
  "resume": "résumé en 2-3 phrases de la consultation",
  "symptomes": ["symptôme 1", "symptôme 2"],
  "diagnostic_suggere": "diagnostic évoqué (reste une SUGGESTION à valider par le médecin)",
  "prescriptions": [{"medicament": "...", "dosage": "...", "duree": "..."}],
  "recommandation_suivi": "ce qui est recommandé comme suivi",
  "needs_human_review": true
}

Si la transcription est trop courte, ambiguë, ou ne mentionne pas clairement
un diagnostic ou des prescriptions, indique-le honnêtement plutôt que
d'inventer des informations médicales. Ne fais JAMAIS de diagnostic définitif :
formule toujours comme une suggestion à valider."""


def summarize_consultation(transcript: str) -> ConsultationSummary:
    llm = get_llm_provider()
    raw = llm.complete(SUMMARY_SYSTEM_PROMPT, transcript, json_mode=True)
    data = safe_json_parse(raw)
    data.setdefault("needs_human_review", True)  # toujours True par sécurité par défaut
    return ConsultationSummary(**data)
