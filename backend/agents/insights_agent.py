"""
Insights Agent — la brique BI&A du projet : transforme les données brutes
en indicateurs pour le tableau de bord admin.

Tout est calculé avec pandas à partir des données déjà en base (aucun appel
LLM ici — c'est de l'agrégation classique, gratuite et rapide).
"""
from collections import Counter

import pandas as pd

from db.database import get_supabase
from models.schemas import InsightsOut

PRIORITY_LABELS = {1: "Urgence", 2: "Grossesse", 3: "Âgé/chronique", 4: "Normal"}


def compute_insights() -> InsightsOut:
    sb = get_supabase()

    queue_rows = sb.table("queue_entries").select("*").execute().data
    appt_rows = sb.table("appointments").select("*").execute().data
    consult_rows = sb.table("consultations").select("*").execute().data
    prescr_rows = sb.table("prescriptions").select("*").execute().data

    queue_df = pd.DataFrame(queue_rows)
    appt_df = pd.DataFrame(appt_rows)
    consult_df = pd.DataFrame(consult_rows)
    prescr_df = pd.DataFrame(prescr_rows)

    avg_wait = _avg_wait_by_priority(queue_df)
    consultations_per_day = _consultations_per_day(consult_df)
    top_diagnoses = _top_diagnoses(consult_df)
    top_meds = _top_medications(prescr_df)
    priority_distribution = _priority_distribution(queue_df)
    no_show_rate = _no_show_rate(appt_df)

    return InsightsOut(
        avg_wait_time_minutes=avg_wait,
        consultations_per_day=consultations_per_day,
        top_diagnoses=top_diagnoses,
        top_medications=top_meds,
        priority_distribution=priority_distribution,
        no_show_rate=no_show_rate,
    )


def _avg_wait_by_priority(queue_df: pd.DataFrame) -> dict[str, float]:
    if queue_df.empty or "status" not in queue_df:
        return {}
    done = queue_df[queue_df["status"] == "done"].copy()
    if done.empty:
        return {}
    done["arrival_time"] = pd.to_datetime(done["arrival_time"])
    done["called_at"] = pd.to_datetime(done.get("called_at", done["arrival_time"]))
    done["wait_minutes"] = (done["called_at"] - done["arrival_time"]).dt.total_seconds() / 60
    grouped = done.groupby("priority")["wait_minutes"].mean()
    return {PRIORITY_LABELS.get(p, str(p)): round(v, 1) for p, v in grouped.items()}


def _consultations_per_day(consult_df: pd.DataFrame) -> dict[str, int]:
    if consult_df.empty:
        return {}
    consult_df["created_at"] = pd.to_datetime(consult_df["created_at"])
    counts = consult_df.groupby(consult_df["created_at"].dt.date).size()
    return {str(day): int(count) for day, count in counts.items()}


def _top_diagnoses(consult_df: pd.DataFrame) -> dict[str, int]:
    if consult_df.empty or "summary" not in consult_df:
        return {}
    diagnoses = [
        row.get("diagnostic_suggere")
        for row in consult_df["summary"].dropna()
        if isinstance(row, dict) and row.get("diagnostic_suggere")
    ]
    return dict(Counter(diagnoses).most_common(5))


def _top_medications(prescr_df: pd.DataFrame) -> dict[str, int]:
    if prescr_df.empty:
        return {}
    return dict(Counter(prescr_df["medication"]).most_common(5))


def _priority_distribution(queue_df: pd.DataFrame) -> dict[str, int]:
    if queue_df.empty:
        return {}
    counts = queue_df["priority"].value_counts().to_dict()
    return {PRIORITY_LABELS.get(p, str(p)): int(c) for p, c in counts.items()}


def _no_show_rate(appt_df: pd.DataFrame) -> float:
    if appt_df.empty:
        return 0.0
    total = len(appt_df)
    no_shows = (appt_df["status"] == "no_show").sum()
    return round(no_shows / total, 3) if total else 0.0
