
import pytest

from src.hybrid_detector import detect_hybrid


def test_detect_email():
    results = detect_hybrid("Email của tôi là an@gmail.com")

    assert any(
        item["label"] == "EMAIL"
        and item["text"] == "an@gmail.com"
        for item in results
    )


def test_detect_person_name():
    results = detect_hybrid("Tôi là Nguyễn Văn An")

    assert any(
        item["label"] == "PERSON_NAME"
        and item["text"] == "Nguyễn Văn An"
        for item in results
    )


def test_detect_person_and_email():
    results = detect_hybrid(
        "Tôi là Nguyễn Văn An, email an@gmail.com"
    )

    labels = [item["label"] for item in results]

    assert "PERSON_NAME" in labels
    assert "EMAIL" in labels


def test_clean_text():
    results = detect_hybrid("Hôm nay thời tiết rất đẹp")

    assert results == []
