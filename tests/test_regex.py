
import pytest

from src.regex_detector import detect_sensitive_entities


@pytest.mark.parametrize(
    "sample_text, expected_label, expected_value",
    [
        (
            "Điện thoại: 0912345678",
            "PHONE",
            "0912345678"
        ),
        (
            "Email: an.test@example.com",
            "EMAIL",
            "an.test@example.com"
        ),
        (
            "MSSV: SV20260001",
            "STUDENT_ID",
            "SV20260001"
        ),
        (
            "CCCD: 012345678901",
            "NATIONAL_ID",
            "012345678901"
        ),
        (
            "Số tài khoản: 123456789012",
            "BANK_ACCOUNT",
            "123456789012"
        ),
        (
            "API key: sk-abcdefghijklmnop",
            "SECRET_KEY",
            "sk-abcdefghijklmnop"
        ),
                (
            "Mật khẩu: DemoPass123",
            "CREDENTIAL",
            "DemoPass123"
        ),
        (
            "GPA: 3.5",
            "ACADEMIC_RECORD",
            "GPA: 3.5"
        ),
    ]
)
def test_detect_sensitive_data(
    sample_text,
    expected_label,
    expected_value
):
    """Kiểm tra hệ thống phát hiện đúng dữ liệu."""

    results = detect_sensitive_entities(sample_text)

    matching_results = [
        item for item in results
        if item["label"] == expected_label
    ]

    assert len(matching_results) == 1

    entity = matching_results[0]

    assert entity["text"] == expected_value
    assert sample_text[entity["start"]:entity["end"]] == expected_value


def test_no_sensitive_data():
    """Kiểm tra văn bản bình thường không bị phát hiện nhầm."""

    sample_text = """
    Hôm nay trời đẹp.
    Tôi đang học môn nghiên cứu khoa học.
    Trường đại học tổ chức hội thảo.
    """

    results = detect_sensitive_entities(sample_text)

    assert results == []


def test_detection_positions():
    """Kiểm tra vị trí start và end."""

    sample_text = "Email: an.test@example.com"

    results = detect_sensitive_entities(sample_text)

    assert len(results) == 1

    entity = results[0]

    assert entity["start"] == 7
    assert entity["end"] == 26
    assert sample_text[entity["start"]:entity["end"]] == "an.test@example.com"
