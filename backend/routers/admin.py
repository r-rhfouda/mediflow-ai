"""Route admin — expose les indicateurs calculés par l'insights_agent."""
from fastapi import APIRouter

from agents.insights_agent import compute_insights
from models.schemas import InsightsOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/insights", response_model=InsightsOut)
def get_insights():
    return compute_insights()
