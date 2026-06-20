"""
Point d'entrée du backend MediFlow AI.

Lancement local : uvicorn main:app --reload --port 8000
Documentation auto-générée disponible sur http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import admin, appointments, calendar, consultations, patients, queue

app = FastAPI(
    title="MediFlow AI",
    description="API du système de gestion de cabinet médical augmenté par des agents IA.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(appointments.router)
app.include_router(calendar.router)
app.include_router(queue.router)
app.include_router(consultations.router)
app.include_router(patients.router)
app.include_router(admin.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "env": settings.env, "llm_provider": settings.llm_provider}
