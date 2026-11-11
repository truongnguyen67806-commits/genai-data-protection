
from src.masker import mask_sensitive_data


def make_entity(label, text, start, end):
    return {
        "label": label,
        "text": text,
        "start": start,
        "end": end,
        "confidence": 0.95,
        "method": "TEST"
    }


def test_mask_email():
    text = "Email của tôi là an@gmail.com"
    start = text.index("an@gmail.com")
    end = start + len("an@gmail.com")

    entities = [
        make_entity("EMAIL", "an@gmail.com", start, end)
    ]

    result = mask_sensitive_data(text, entities)

    assert result == "Email của tôi là [EMAIL]"


def test_mask_person_name():
    text = "Tôi là Nguyễn Văn An"
    start = text.index("Nguyễn Văn An")
    end = start + len("Nguyễn Văn An")

    entities = [
        make_entity("PERSON_NAME", "Nguyễn Văn An", start, end)
    ]

    result = mask_sensitive_data(text, entities)

    assert result == "Tôi là [PERSON_NAME]"


def test_mask_multiple_entities():
    text = "Nguyễn Văn An có email an@gmail.com"

    name = "Nguyễn Văn An"
    email = "an@gmail.com"

    entities = [
        make_entity(
            "PERSON_NAME",
            name,
            text.index(name),
            text.index(name) + len(name)
        ),
        make_entity(
            "EMAIL",
            email,
            text.index(email),
            text.index(email) + len(email)
        )
    ]

    result = mask_sensitive_data(text, entities)

    assert result == "[PERSON_NAME] có email [EMAIL]"


def test_mask_empty_entities():
    text = "Hôm nay tôi đi học"

    result = mask_sensitive_data(text, [])

    assert result == text
