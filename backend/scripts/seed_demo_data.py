"""
Crée d'un coup les comptes Supabase Auth ET toutes les données de
démonstration (profils, patients, médecins, RDV, file d'attente).

Usage :
    cd backend
    python scripts/seed_demo_data.py

Pré-requis : backend/.env rempli avec SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY.
Gratuit — aucune carte bancaire, aucune clé payante nécessaire pour ce script.

Idempotence : relancer le script créera des doublons si les comptes existent
déjà. Si besoin de recommencer à zéro, supprimez les utilisateurs de test
depuis Supabase Dashboard > Authentication avant de relancer.
"""
import os
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings  # noqa: E402
from supabase import create_client  # noqa: E402

DEMO_PASSWORD = "MediFlowDemo2026!"  # uniquement pour les comptes fictifs de démo

STAFF = [
    {"email": "admin@mediflow.demo", "full_name": "Sara Admin", "role": "admin"},
    {"email": "reception@mediflow.demo", "full_name": "Nadia Réception", "role": "receptionist"},
    {"email": "dr.alaoui@mediflow.demo", "full_name": "Dr. Yassine Alaoui", "role": "doctor", "specialty": "Médecine générale"},
    {"email": "dr.benali@mediflow.demo", "full_name": "Dr. Imane Benali", "role": "doctor", "specialty": "Gynécologie"},
]

PATIENTS = [
    {"email": "karim.idrissi@mediflow.demo", "full_name": "Karim Idrissi", "dob": date(1990, 4, 12), "pregnant": False, "chronic": [], "allergies": []},
    {"email": "salma.tazi@mediflow.demo", "full_name": "Salma Tazi", "dob": date(1996, 9, 3), "pregnant": True, "chronic": [], "allergies": []},
    {"email": "mohamed.senhaji@mediflow.demo", "full_name": "Mohamed Senhaji", "dob": date(1952, 1, 20), "pregnant": False, "chronic": ["diabète"], "allergies": ["pénicilline"]},
    {"email": "laila.cherkaoui@mediflow.demo", "full_name": "Laila Cherkaoui", "dob": date(1988, 7, 15), "pregnant": False, "chronic": [], "allergies": []},
    {"email": "youssef.amrani@mediflow.demo", "full_name": "Youssef Amrani", "dob": date(1979, 11, 30), "pregnant": False, "chronic": ["hypertension"], "allergies": []},
]

# (email_patient, doctor_email, minutes_écoulés_depuis_arrivée, motif, priorité, raison, revue_humaine)
QUEUE_SCENARIOS = [
    ("karim.idrissi@mediflow.demo", "dr.alaoui@mediflow.demo", 60, "Contrôle de routine", 4, "Aucun facteur de priorité détecté", False),
    ("salma.tazi@mediflow.demo", "dr.benali@mediflow.demo", 50, "Suivi de grossesse", 2, "Patiente enceinte", False),
    ("mohamed.senhaji@mediflow.demo", "dr.alaoui@mediflow.demo", 40, "Suivi diabète", 3, "Patient âgé (74 ans) avec pathologie chronique", False),
    ("laila.cherkaoui@mediflow.demo", "dr.alaoui@mediflow.demo", 10, "Douleur thoracique", 1, "Urgence déclarée : douleur thoracique", False),
    ("youssef.amrani@mediflow.demo", "dr.alaoui@mediflow.demo", 5, "Fatigue inhabituelle depuis 3 jours, vertiges", 2, "Symptômes combinés jugés préoccupants par l'agent IA (confiance modérée)", True),
]


def get_client():
    if not settings.supabase_url or not settings.supabase_service_role_key:
        sys.exit("❌ SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY manquants dans backend/.env")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def create_auth_user(sb, email: str, full_name: str) -> str:
    result = sb.auth.admin.create_user(
        {
            "email": email,
            "password": DEMO_PASSWORD,
            "email_confirm": True,
            "user_metadata": {"full_name": full_name},
        }
    )
    return result.user.id


def main():
    sb = get_client()
    id_map: dict[str, str] = {}

    print("→ Création des comptes staff...")
    for person in STAFF:
        uid = create_auth_user(sb, person["email"], person["full_name"])
        id_map[person["email"]] = uid
        sb.table("profiles").insert({"id": uid, "role": person["role"], "full_name": person["full_name"]}).execute()
        if person["role"] == "doctor":
            sb.table("doctors").insert({"id": uid, "specialty": person["specialty"]}).execute()
        print(f"  ✓ {person['full_name']} ({person['role']})")

    print("→ Création des patients de démo...")
    for p in PATIENTS:
        uid = create_auth_user(sb, p["email"], p["full_name"])
        id_map[p["email"]] = uid
        sb.table("profiles").insert({"id": uid, "role": "patient", "full_name": p["full_name"]}).execute()
        sb.table("patients").insert(
            {
                "id": uid,
                "date_of_birth": p["dob"].isoformat(),
                "is_pregnant": p["pregnant"],
                "chronic_conditions": p["chronic"],
                "allergies": p["allergies"],
            }
        ).execute()
        print(f"  ✓ {p['full_name']}")

    print("→ Création des rendez-vous et de la file d'attente...")
    now = datetime.now(timezone.utc)
    for patient_email, doctor_email, minutes_ago, reason, priority, why, needs_review in QUEUE_SCENARIOS:
        patient_id = id_map[patient_email]
        doctor_id = id_map[doctor_email]
        arrival = now - timedelta(minutes=minutes_ago)

        appt = (
            sb.table("appointments")
            .insert(
                {
                    "patient_id": patient_id,
                    "doctor_id": doctor_id,
                    "scheduled_at": arrival.isoformat(),
                    "reason": reason,
                    "status": "checked_in",
                }
            )
            .execute()
            .data[0]
        )
        sb.table("queue_entries").insert(
            {
                "appointment_id": appt["id"],
                "patient_id": patient_id,
                "priority": priority,
                "priority_reason": why,
                "needs_human_review": needs_review,
                "arrival_time": arrival.isoformat(),
                "status": "waiting",
            }
        ).execute()
        print(f"  ✓ {patient_email} → priorité {priority}")

    print("\n✅ Données de démo créées avec succès.")
    print(f"   Mot de passe (tous les comptes de démo) : {DEMO_PASSWORD}")
    print("   Connectez-vous sur le frontend avec, par exemple : reception@mediflow.demo")


if __name__ == "__main__":
    main()
