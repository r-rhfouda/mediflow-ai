"""
Anomaly Agent — détecte des incohérences qui méritent une alerte humaine.

Volontairement basé sur des règles simples et explicables plutôt que sur
un LLM : dans ce contexte (sécurité du patient), la prévisibilité prime
sur la sophistication. Chaque alerte est remontée à l'admin/médecin,
jamais auto-appliquée (aucune prescription n'est modifiée automatiquement).
"""
from models.schemas import AnomalyAlert, ConsultationSummary, PatientContext


def check_consultation(patient: PatientContext, summary: ConsultationSummary) -> list[AnomalyAlert]:
    alerts: list[AnomalyAlert] = []

    # 1. Allergie connue vs médicament prescrit.
    for prescription in summary.prescriptions:
        for allergy in patient.allergies:
            if allergy.lower() in prescription.medicament.lower():
                alerts.append(
                    AnomalyAlert(
                        alert_type="allergy_conflict",
                        severity="high",
                        message=(
                            f"Le patient a une allergie déclarée à '{allergy}' mais "
                            f"'{prescription.medicament}' est prescrit."
                        ),
                        suggested_action="Vérifier la prescription avec le médecin avant délivrance.",
                    )
                )

    # 2. Résumé qui signale lui-même une incertitude forte.
    if summary.needs_human_review:
        alerts.append(
            AnomalyAlert(
                alert_type="low_confidence_summary",
                severity="medium",
                message="Le résumé généré par l'IA signale un niveau de confiance faible.",
                suggested_action="Le médecin doit relire et corriger le résumé avant validation.",
            )
        )

    return alerts
