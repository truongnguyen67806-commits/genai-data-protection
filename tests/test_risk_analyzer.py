
import pytest

from src.risk_analyzer import analyze_risk


def make_entity(label):
    return {
        "label": label,
        "text": "test",
        "start": 0,
        "end": 4,
        "confidence": 0.95,
        "method": "TEST"
    }


def test_risk_none():
    result = analyze_risk([])

    assert result["level"] == "NONE"
    assert result["score"] == 0


def test_risk_low():
    entities = [
        make_entity("PERSON_NAME")
    ]

    result = analyze_risk(entities)

    assert result["level"] == "LOW"
    assert result["score"] == 1


def test_risk_medium():
    entities = [
        make_entity("EMAIL"),
        make_entity("PHONE")
    ]

    result = analyze_risk(entities)

    assert result["level"] == "MEDIUM"
    assert result["score"] == 2


def test_risk_high_sensitive_data():
    entities = [
        make_entity("NATIONAL_ID")
    ]

    result = analyze_risk(entities)

    assert result["level"] == "HIGH"
    assert result["score"] == 3


def test_risk_high_academic_record():
    entities = [
        make_entity("PERSON_NAME"),
        make_entity("ACADEMIC_RECORD")
    ]

    result = analyze_risk(entities)

    assert result["level"] == "HIGH"
    assert result["score"] == 3


def test_risk_high_many_entity_types():
    entities = [
        make_entity("PERSON_NAME"),
        make_entity("EMAIL"),
        make_entity("PHONE")
    ]

    result = analyze_risk(entities)

    assert result["level"] == "HIGH"


def test_risk_high_many_entities():
    entities = [
        make_entity("EMAIL"),
        make_entity("EMAIL"),
        make_entity("EMAIL"),
        make_entity("EMAIL"),
        make_entity("EMAIL")
    ]

    result = analyze_risk(entities)

    assert result["level"] == "HIGH"


def test_high_has_priority_over_medium():
    entities = [
        make_entity("EMAIL"),
        make_entity("BANK_ACCOUNT")
    ]

    result = analyze_risk(entities)

    assert result["level"] == "HIGH"
