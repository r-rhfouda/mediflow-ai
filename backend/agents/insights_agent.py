"""
Insights Agent — la brique BI&A du projet : transforme les données brutes
en indicateurs pour le tableau de bord admin.

Tout est calculé avec pandas à partir des données déjà en base (aucun appel
LLM ici — c'est de l'agrégation classique, gratuite et rapide).

Trois granularités sont supportées via le paramètre `period`, pour
alimenter les 3 pages du tableau de bord admin :
  - "day"   → dernières 24h (pilotage quotidien)
  - "month" → 30 derniers jours (tendances mensuelles)
  - "all"   → depuis l'ouverture du cabinet / le déploiement du système
"""
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Literal

import pandas as pd

from db.database import get_supabase
from models.schemas import InsightsOut

PRIORITY_LABELS = {1: "Urgence", 2: "Grossesse", 3: "Âgé/chronique", 4: "Normal"}

Period = Literal["day", "month", "all"]
PERIOD_WINDOWS: dict[str, timedelta | None] = {
    "day": timedelta(days=1),
    "month": timedelta(days=30),
    "all": None,
}


def _filter_by_period(df: pd.DataFrame, date_column: str, period: Period) -> pd.DataFrame:
    window = PERIOD_WINDOWS[period]
    if window is None or df.empty or date_column not in df:
        return df
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], utc=True)
    cutoff = datetime.now(timezone.utc) - window
    return df[df[date_column] >= cutoff]


def compute_insights(period: Period = "all") -> InsightsOut:
    sb = get_supabase()

    queue_rows = sb.table("queue_entries").select("*").execute().data
    appt_rows = sb.table("appointments").select("*").execute().data
    consult_rows = sb.table("consultations").select("*").execute().data
    prescr_rows = sb.table("prescriptions").select("*").execute().data

    queue_df = _filter_by_period(pd.DataFrame(queue_rows), "arrival_time", period)
    appt_df = _filter_by_period(pd.DataFrame(appt_rows), "scheduled_at", period)
    consult_df = _filter_by_period(pd.DataFrame(consult_rows), "created_at", period)
    # Les prescriptions héritent de la période via les consultations déjà filtrées.
    consult_ids = set(consult_df["id"]) if not consult_df.empty and "id" in consult_df else None
    prescr_df = pd.DataFrame(prescr_rows)
    if consult_ids is not None and not prescr_df.empty:
        prescr_df = prescr_df[prescr_df["consultation_id"].isin(consult_ids)]

    avg_wait = _avg_wait_by_priority(queue_df)
    consultations_per_day = _consultations_per_day(consult_df)
    top_diagnoses = _top_diagnoses(consult_df)
    top_meds = _top_medications(prescr_df)
    priority_distribution = _priority_distribution(queue_df)
    no_show_rate = _no_show_rate(appt_df)
    avg_consultation_duration = _avg_consultation_duration(appt_df, consult_df)
    ai_summary_edit_rate = _ai_summary_edit_rate(consult_df)
    hourly_distribution = _hourly_distribution(appt_df)

    return InsightsOut(
        avg_wait_time_minutes=avg_wait,
        consultations_per_day=consultations_per_day,
        top_diagnoses=top_diagnoses,
        top_medications=top_meds,
        priority_distribution=priority_distribution,
        no_show_rate=no_show_rate,
        avg_consultation_duration_minutes=avg_consultation_duration,
        ai_summary_edit_rate=ai_summary_edit_rate,
        hourly_distribution=hourly_distribution,
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


def _avg_consultation_duration(appt_df: pd.DataFrame, consult_df: pd.DataFrame) -> float | None:
    """Durée moyenne d'une consultation (minutes) — du passage en
    'in_consultation' (queue) à l'enregistrement de la note de consultation.
    Utile pour dimensionner les créneaux et anticiper les retards de planning."""
    if consult_df.empty or appt_df.empty:
        return None
    consult_df = consult_df.copy()
    consult_df["created_at"] = pd.to_datetime(consult_df["created_at"])
    appt_df = appt_df.copy()
    appt_df["scheduled_at"] = pd.to_datetime(appt_df["scheduled_at"])

    merged = consult_df.merge(
        appt_df[["id", "scheduled_at"]], left_on="appointment_id", right_on="id", how="left"
    )
    merged = merged.dropna(subset=["scheduled_at"])
    if merged.empty:
        return None
    durations = (merged["created_at"] - merged["scheduled_at"]).dt.total_seconds() / 60
    durations = durations[(durations > 0) & (durations < 180)]  # filtre les valeurs aberrantes
    return round(durations.mean(), 1) if not durations.empty else None


def _ai_summary_edit_rate(consult_df: pd.DataFrame) -> float:
    """Part des résumés générés par l'IA que le médecin a jugés assez
    incertains pour nécessiter une relecture (needs_human_review=true dans
    le résumé). Indicateur de gouvernance/fiabilité de l'IA : un taux élevé
    signale que le summarization_agent doit être affiné ou que les
    consultations sont particulièrement complexes sur la période."""
    if consult_df.empty or "summary" not in consult_df:
        return 0.0
    summaries = [row for row in consult_df["summary"].dropna() if isinstance(row, dict)]
    if not summaries:
        return 0.0
    flagged = sum(1 for s in summaries if s.get("needs_human_review"))
    return round(flagged / len(summaries), 3)


def _hourly_distribution(appt_df: pd.DataFrame) -> dict[str, int]:
    """Répartition des rendez-vous par heure de la journée — identifie les
    heures de pointe pour aider à répartir le personnel d'accueil et
    anticiper les pics d'affluence plutôt que de les subir."""
    if appt_df.empty:
        return {}
    df = appt_df.copy()
    df["scheduled_at"] = pd.to_datetime(df["scheduled_at"])
    counts = df["scheduled_at"].dt.hour.value_counts().sort_index()
    return {f"{hour:02d}h": int(count) for hour, count in counts.items()}
