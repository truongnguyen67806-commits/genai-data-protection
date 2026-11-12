
import json
import csv
from pathlib import Path

from src.hybrid_detector import detect_hybrid


DATASET_PATH = Path("data/dataset_nhay_cam_vi.jsonl")
OUTPUT_PATH = Path("results/hybrid_error_analysis.csv")


def entity_key(entity):
    return (
        entity["label"],
        entity["start"],
        entity["end"]
    )


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    false_positives = []
    false_negatives = []
    true_positives = []

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    test_records = [
        record for record in records
        if record["split"] == "test"
    ]

    for record in test_records:
        text = record["text"]
        expected = record["entities"]
        predicted = detect_hybrid(text)

        expected_map = {
            entity_key(entity): entity
            for entity in expected
        }

        predicted_map = {
            entity_key(entity): entity
            for entity in predicted
        }

        for key in expected_map.keys() & predicted_map.keys():
            true_positives.append({
                "id": record["id"],
                "type": "TP",
                "text": text,
                "label": key[0],
                "expected_text": expected_map[key]["text"],
                "predicted_text": predicted_map[key]["text"],
                "start": key[1],
                "end": key[2]
            })

        for key in predicted_map.keys() - expected_map.keys():
            false_positives.append({
                "id": record["id"],
                "type": "FP",
                "text": text,
                "label": key[0],
                "expected_text": "",
                "predicted_text": predicted_map[key]["text"],
                "start": key[1],
                "end": key[2]
            })

        for key in expected_map.keys() - predicted_map.keys():
            false_negatives.append({
                "id": record["id"],
                "type": "FN",
                "text": text,
                "label": key[0],
                "expected_text": expected_map[key]["text"],
                "predicted_text": "",
                "start": key[1],
                "end": key[2]
            })

    all_errors = false_positives + false_negatives

    fieldnames = [
        "id", "type", "text", "label",
        "expected_text", "predicted_text",
        "start", "end"
    ]

    with OUTPUT_PATH.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(all_errors)

    print("SO MAU TEST:", len(test_records))
    print("TRUE POSITIVE:", len(true_positives))
    print("FALSE POSITIVE:", len(false_positives))
    print("FALSE NEGATIVE:", len(false_negatives))
    print("TONG SO LOI:", len(all_errors))

    print("\nPHAN LOAI LOI:")
    for label in sorted({
        item["label"] for item in all_errors
    }):
        fp = sum(
            1 for item in false_positives
            if item["label"] == label
        )
        fn = sum(
            1 for item in false_negatives
            if item["label"] == label
        )
        print(f"{label}: FP={fp}, FN={fn}")

    print("\nDA LUU:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
