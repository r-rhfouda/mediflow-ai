"""Routes pour la prise et la gestion des rendez-vous (utilise le scheduling_agent)."""
from fastapi import APIRouter, HTTPException, Query

from agents.scheduling_agent import create_appointment
from db.database import get_supabase
from models.schemas import AppointmentCreate, AppointmentOut

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentOut)
def book_appointment(payload: AppointmentCreate):
    try:
        appointment = create_appointment(
            payload.patient_id, payload.doctor_id, payload.scheduled_at, payload.reason
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return appointment


@router.get("", response_model=list[AppointmentOut])
def list_appointments(doctor_id: str | None = Query(None), patient_id: str | None = Query(None)):
    sb = get_supabase()
    query = sb.table("appointments").select("*")
    if doctor_id:
        query = query.eq("doctor_id", doctor_id)
    if patient_id:
        query = query.eq("patient_id", patient_id)
    return query.order("scheduled_at", desc=False).execute().data


@router.patch("/{appointment_id}/cancel")
def cancel_appointment(appointment_id: str):
    sb = get_supabase()
    sb.table("appointments").update({"status": "cancelled"}).eq("id", appointment_id).execute()
    return {"status": "ok"}
