"""
Transcription Agent — convertit l'audio d'une consultation en texte.

Implémentation par défaut : faster-whisper, un modèle open-source qui
tourne en local sur CPU. Aucune clé API, aucun compte, aucun coût.

Premier appel : le modèle (quelques centaines de Mo) est téléchargé une
seule fois puis mis en cache localement — prévoir une connexion internet
la première fois, pas ensuite.

Le modèle "small" est un bon compromis vitesse/précision pour du français
sur un ordinateur portable standard (transcription d'un extrait de 30s en
quelques secondes sur CPU). Passer à "base" si la machine est très limitée,
ou "medium" si vous avez du temps/une bonne machine et voulez plus de précision.
"""
from functools import lru_cache

from core.config import settings


@lru_cache
def _get_model():
    from faster_whisper import WhisperModel

    return WhisperModel(settings.whisper_model_size, device="cpu", compute_type="int8")


def transcribe(audio_path: str) -> dict:
    model = _get_model()
    segments, info = model.transcribe(audio_path, language="fr", beam_size=5)
    transcript = " ".join(segment.text.strip() for segment in segments)
    return {
        "transcript": transcript.strip(),
        "language": info.language,
        "duration_seconds": info.duration,
    }
