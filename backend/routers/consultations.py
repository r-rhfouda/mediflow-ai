"""
Routes de consultation — pipeline complet :
  upload audio → transcription_agent → summarization_agent → édition par
  le médecin → validation définitive (+ anomaly_agent + prescriptions).

Le résumé généré n'est JAMAIS sauvegardé comme définitif tant que
PATCH /consultations/{id}/validate n'a pas été appelé explicitement par
le médecin depuis l'UI (champ "summary" éditable avant envoi).
"""
import os
import tempfile
from datetime import date, datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile

from agents.anomaly_agent import check_consultation
from agents.summarization_agent import summarize_consultation
from agents.transcription_agent import transcribe
from db.database import get_supabase
from models.schemas import ConsultationValidateRequest, PatientContext

router = APIRouter(prefix="/consultations", tags=["consultations"])


@router.post("/{appointment_id}/audio")
async def upload_consultation_audio(appointment_id: str, consent_given: bool, audio: UploadFile = File(...)):
    if not consent_given:
        raise HTTPException(
            status_code=400,
            detail="Le consentement du patient à l'enregistrement est obligatoire.",
        )

    sb = get_supabase()

    # 1. Sauvegarde temporaire locale pour la transcription.
    suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        # 2. Upload vers Supabase Storage (bucket "consultation-audio", à créer
        #    une fois dans le dashboard Supabase : Storage > New bucket, privé).
        storage_path = f"{appointment_id}/{audio.filename}"
        with open(tmp_path, "rb") as f:
            sb.storage.from_("consultation-audio").upload(storage_path, f)

        # 3. Transcription (gratuite, locale).
        transcription = transcribe(tmp_path)

        # 4. Résumé structuré (gratuit, via Groq par défaut).
        summary = summarize_consultation(transcription["transcript"])
    finally:
        os.remove(tmp_path)

    consultation = (
        sb.table("consultations")
        .insert(
            {
                "appointment_id": appointment_id,
                "audio_url": storage_path,
                "consent_given": consent_given,
                "transcript": transcription["transcript"],
                "summary": summary.model_dump(),
                "validated_by_doctor": False,
            }
        )
        .execute()
        .data[0]
    )

    return {"consultation": consultation, "draft_summary": summary}


@router.patch("/{consultation_id}/validate")
def validate_consultation(consultation_id: str, payload: ConsultationValidateRequest):
    sb = get_supabase()

    consultation = sb.table("consultations").select("*").eq("id", consultation_id).single().execute().data
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation introuvable.")

    appointment = (
        sb.table("appointments").select("patient_id").eq("id", consultation["appointment_id"]).single().execute().data
    )
    patient_row = sb.table("patients").select("*").eq("id", appointment["patient_id"]).single().execute().data
    patient = PatientContext(
        patient_id=appointment["patient_id"],
        date_of_birth=date.fromisoformat(patient_row["date_of_birth"]),
        is_pregnant=patient_row.get("is_pregnant", False),
        chronic_conditions=patient_row.get("chronic_conditions") or [],
        allergies=patient_row.get("allergies") or [],
    )

    # Le médecin a pu corriger le résumé : on garde SA version comme définitive.
    sb.table("consultations").update(
        {
            "summary": payload.summary.model_dump(),
            "validated_by_doctor": True,
            "validated_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", consultation_id).execute()

    # Enregistrement des prescriptions structurées dans leur propre table
    # (facilite l'historique patient et les indicateurs BI).
    for item in payload.summary.prescriptions:
        sb.table("prescriptions").insert(
            {
                "consultation_id": consultation_id,
                "patient_id": appointment["patient_id"],
                "medication": item.medicament,
                "dosage": item.dosage,
                "duration": item.duree,
            }
        ).execute()

    # Détection d'anomalies (allergies, faible confiance...) → alertes, jamais auto-appliquées.
    alerts = check_consultation(patient, payload.summary)
    for alert in alerts:
        sb.table("audit_log").insert(
            {
                "related_table": "consultations",
                "related_id": consultation_id,
                "event_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
            }
        ).execute()

    return {"status": "validated", "alerts": alerts}
