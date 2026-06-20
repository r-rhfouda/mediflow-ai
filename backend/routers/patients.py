"""Routes pour le dossier / historique d'un patient."""
from fastapi import APIRouter, File, UploadFile

from db.database import get_supabase

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}/history")
def get_patient_history(patient_id: str):
    sb = get_supabase()

    appointments = (
        sb.table("appointments").select("*").eq("patient_id", patient_id).order("scheduled_at", desc=True).execute().data
    )
    appointment_ids = [a["id"] for a in appointments]

    consultations = (
        sb.table("consultations").select("*").in_("appointment_id", appointment_ids or [""]).execute().data
    )
    prescriptions = (
        sb.table("prescriptions").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute().data
    )
    documents = (
        sb.table("documents").select("*").eq("patient_id", patient_id).order("uploaded_at", desc=True).execute().data
    )

    return {
        "appointments": appointments,
        "consultations": consultations,
        "prescriptions": prescriptions,
        "documents": documents,
    }


@router.post("/{patient_id}/documents")
async def upload_document(patient_id: str, document_type: str, file: UploadFile = File(...)):
    sb = get_supabase()
    storage_path = f"{patient_id}/{file.filename}"
    content = await file.read()
    # Bucket "patient-documents" à créer une fois dans Supabase Storage (privé).
    sb.storage.from_("patient-documents").upload(storage_path, content)

    document = (
        sb.table("documents")
        .insert({"patient_id": patient_id, "file_url": storage_path, "document_type": document_type})
        .execute()
        .data[0]
    )
    return document
