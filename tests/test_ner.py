import pytest
from src.ner_detector import detect_ner


@pytest.mark.parametrize(
    "text, expected_name",
    [
        (
            "Tôi là Nguyễn Văn An, học tại Đại học Bách Khoa.",
            "Nguyễn Văn An"
        ),
        (
            "Trần Thị Bình đang học tại Đại học Quốc gia Hà Nội.",
            "Trần Thị Bình"
        ),
        (
            "Lê Minh Hoàng là sinh viên năm thứ ba.",
            "Lê Minh Hoàng"
        ),
    ]
)
def test_detect_person_name(text, expected_name):
    results = detect_ner(text)

    detected_names = [
        item["text"] for item in results
        if item["label"] == "PERSON_NAME"
    ]

    assert expected_name in detected_names


def test_no_person_name():
    text = "Hôm nay trời đẹp và tôi đi học."

    results = detect_ner(text)

    assert not any(
        item["label"] == "PERSON_NAME"
        for item in results
    )