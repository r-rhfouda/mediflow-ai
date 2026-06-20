"""
Tests du triage_agent — uniquement la branche "règles déterministes"
(aucun appel réseau/LLM nécessaire, donc rapide et gratuit à exécuter).

Lancer avec : pytest tests/test_triage_agent.py -v
"""
from datetime import date

from agents.triage_agent import evaluate_priority
from models.schemas import PatientContext


def _patient(**overrides) -> PatientContext:
    defaults = dict(
        patient_id="test-patient",
        date_of_birth=date(1995, 1, 1),
        is_pregnant=False,
        chronic_conditions=[],
        allergies=[],
    )
    defaults.update(overrides)
    return PatientContext(**defaults)


def test_emergency_declared_is_priority_1():
    result = evaluate_priority(_patient(), motif_libre="contrôle", urgence_declaree=True)
    assert result.priority == 1


def test_emergency_keyword_is_priority_1():
    result = evaluate_priority(
        _patient(), motif_libre="J'ai une douleur thoracique depuis ce matin", urgence_declaree=False
    )
    assert result.priority == 1


def test_pregnant_patient_is_priority_2():
    result = evaluate_priority(_patient(is_pregnant=True), motif_libre="contrôle de routine", urgence_declaree=False)
    assert result.priority == 2


def test_elderly_patient_is_priority_3():
    result = evaluate_priority(
        _patient(date_of_birth=date(1950, 1, 1)), motif_libre="contrôle", urgence_declaree=False
    )
    assert result.priority == 3


def test_chronic_condition_is_priority_3():
    result = evaluate_priority(
        _patient(chronic_conditions=["diabète"]), motif_libre="contrôle", urgence_declaree=False
    )
    assert result.priority == 3


def test_normal_short_motif_is_priority_4():
    result = evaluate_priority(_patient(), motif_libre="contrôle de routine", urgence_declaree=False)
    assert result.priority == 4
    assert result.needs_human_review is False
