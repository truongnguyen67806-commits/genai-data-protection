
from src.regex_detector import detect_sensitive_entities
from src.ner_detector import detect_ner


def detect_hybrid(input_text):
    regex_results = detect_sensitive_entities(input_text)
    ner_results = detect_ner(input_text)

    results = []

    # Gop ket qua tu Regex va NER
    for entity in regex_results + ner_results:
        is_duplicate = False

        for existing in results:
            if (
                entity["label"] == existing["label"]
                and entity["start"] == existing["start"]
                and entity["end"] == existing["end"]
            ):
                is_duplicate = True

                if entity["confidence"] > existing["confidence"]:
                    existing.update(entity)

                break

        if not is_duplicate:
            results.append(entity)

    # Loai bo PERSON_NAME nam trong mot vung nhan dien
    # du lieu nhay cam khac, vi du DemoPass123 nam trong password
    filtered_results = []

    for entity in results:
        if entity["label"] == "PERSON_NAME":
            is_inside_sensitive_entity = any(
                other["label"] != "PERSON_NAME"
                and other["start"] <= entity["start"]
                and other["end"] >= entity["end"]
                for other in results
            )

            if is_inside_sensitive_entity:
                continue

            # Loai bo API khi nam trong cum tu ky thuat "API key"
            if entity["text"].strip().lower() == "api":
                following_text = input_text[entity["end"]:entity["end"] + 10].lower()

                if following_text.lstrip().startswith("key"):
                    continue

        filtered_results.append(entity)

    # Sap xep ket qua theo vi tri trong van ban
    filtered_results.sort(
        key=lambda item: (item["start"], item["end"])
    )

    return filtered_results
