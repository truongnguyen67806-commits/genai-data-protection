
import json
import csv
import time
from pathlib import Path

from src.regex_detector import detect_sensitive_entities
from src.ner_detector import detect_ner
from src.hybrid_detector import detect_hybrid


DATASET_PATH = Path("data/dataset_nhay_cam_vi.jsonl")
RESULTS_DIR = Path("results")

DETECTORS = {
    "REGEX": detect_sensitive_entities,
    "NER": detect_ner,
    "HYBRID": detect_hybrid,
}


def load_test_data():
    records = []

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)

            if record["split"] == "test":
                records.append(record)

    return records


def entity_key(entity):
    return (
        entity["label"],
        entity["start"],
        entity["end"]
    )


def evaluate_detector(name, detector, records):
    true_positive = 0
    false_positive = 0
    false_negative = 0

    label_stats = {}

    total_time = 0
    total_predictions = 0

    for record in records:
        text = record["text"]
        expected = record["entities"]

        start_time = time.perf_counter()
        predicted = detector(text)
        elapsed = time.perf_counter() - start_time

        total_time += elapsed
        total_predictions += len(predicted)

        expected_set = {
            entity_key(entity)
            for entity in expected
        }

        predicted_set = {
            entity_key(entity)
            for entity in predicted
        }

        matched = expected_set & predicted_set

        true_positive += len(matched)
        false_positive += len(predicted_set - expected_set)
        false_negative += len(expected_set - predicted_set)

        for label, _, _ in expected_set | predicted_set:
            if label not in label_stats:
                label_stats[label] = {
                    "TP": 0,
                    "FP": 0,
                    "FN": 0
                }

        for label, _, _ in matched:
            label_stats[label]["TP"] += 1

        for label, _, _ in predicted_set - expected_set:
            label_stats[label]["FP"] += 1

        for label, _, _ in expected_set - predicted_set:
            label_stats[label]["FN"] += 1

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive else 0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    miss_rate = (
        false_negative / (true_positive + false_negative)
        if true_positive + false_negative else 0
    )

    return {
        "method": name,
        "TP": true_positive,
        "FP": false_positive,
        "FN": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "miss_rate": miss_rate,
        "time_seconds": total_time,
        "avg_time_ms": total_time / len(records) * 1000,
        "predictions": total_predictions,
        "label_stats": label_stats
    }


def save_results(results):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    summary_path = RESULTS_DIR / "evaluation_summary.csv"

    with summary_path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "Method", "TP", "FP", "FN",
            "Precision", "Recall", "F1",
            "Miss rate", "Time (seconds)",
            "Average time (ms/sample)"
        ])

        for result in results:
            writer.writerow([
                result["method"],
                result["TP"],
                result["FP"],
                result["FN"],
                result["precision"],
                result["recall"],
                result["f1"],
                result["miss_rate"],
                result["time_seconds"],
                result["avg_time_ms"]
            ])

    detail_path = RESULTS_DIR / "evaluation_by_label.csv"

    with detail_path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "Method", "Label", "TP", "FP", "FN",
            "Precision", "Recall", "F1"
        ])

        for result in results:
            for label, stats in sorted(
                result["label_stats"].items()
            ):
                tp = stats["TP"]
                fp = stats["FP"]
                fn = stats["FN"]

                precision = tp / (tp + fp) if tp + fp else 0
                recall = tp / (tp + fn) if tp + fn else 0
                f1 = (
                    2 * precision * recall / (precision + recall)
                    if precision + recall else 0
                )

                writer.writerow([
                    result["method"], label,
                    tp, fp, fn,
                    precision, recall, f1
                ])

    json_path = RESULTS_DIR / "evaluation_results.json"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)


def main():
    records = load_test_data()

    if not records:
        print("Khong tim thay du lieu test.")
        return

    print("SO MAU TEST:", len(records))
    print("BAT DAU DANH GIA...\n")

    results = []

    for name, detector in DETECTORS.items():
        print("Dang danh gia:", name)

        result = evaluate_detector(
            name, detector, records
        )

        results.append(result)

    print("\nKET QUA TONG HOP")
    print("-" * 90)

    print(
        f"{'Method':<12}"
        f"{'Precision':>12}"
        f"{'Recall':>12}"
        f"{'F1':>12}"
        f"{'Miss rate':>12}"
        f"{'Time(ms)':>12}"
    )

    for result in results:
        print(
            f"{result['method']:<12}"
            f"{result['precision']:>12.4f}"
            f"{result['recall']:>12.4f}"
            f"{result['f1']:>12.4f}"
            f"{result['miss_rate']:>12.4f}"
            f"{result['avg_time_ms']:>12.3f}"
        )

    save_results(results)

    print("\nDA LUU KET QUA VAO THU MUC results/")
    print("- evaluation_summary.csv")
    print("- evaluation_by_label.csv")
    print("- evaluation_results.json")


if __name__ == "__main__":
    main()
