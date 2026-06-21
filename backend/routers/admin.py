"""Route admin — expose les indicateurs calculés par l'insights_agent."""
from typing import Literal

from fastapi import APIRouter, Query

from agents.insights_agent import compute_insights
from models.schemas import InsightsOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/insights", response_model=InsightsOut)
def get_insights(period: Literal["day", "month", "all"] = Query("all")):
    return compute_insights(period=period)
