
import json
from pathlib import Path

from src.hybrid_detector import detect_hybrid
from src.risk_analyzer import analyze_risk
from src.masker import mask_sensitive_data


def main():
    data_path = Path("data/test_cases.json")

    with data_path.open("r", encoding="utf-8") as file:
        test_cases = json.load(file)

    passed = 0
    failed = 0

    print("=" * 65)
    print("KET QUA KIEM THU CAC TINH HUONG MO PHONG")
    print("=" * 65)

    for case in test_cases:
        input_text = case["input"]
        expected = set(case["expected_labels"])

        entities = detect_hybrid(input_text)
        detected = {entity["label"] for entity in entities}
        if case["id"] == "TC04":
            print("\nCHI TIET NHAN DIEN TC04:")
            for entity in entities:
                print(entity)

        risk = analyze_risk(entities)
        masked_text = mask_sensitive_data(input_text, entities)

        missing = expected - detected
        unexpected = detected - expected

        success = not missing and not unexpected

        if success:
            passed += 1
            status = "DAT"
        else:
            failed += 1
            status = "CHUA DAT"

        print(f"\n[{case['id']}] {case['scenario']}")
        print("Trang thai:", status)
        print("Nhan mong doi:", sorted(expected))
        print("Nhan phat hien:", sorted(detected))

        if missing:
            print("Nhan bi bo sot:", sorted(missing))

        if unexpected:
            print("Nhan phat hien thua:", sorted(unexpected))

        print("Muc do rui ro:", risk["level"])
        print("Van ban sau khi che:", masked_text)

    print("\n" + "=" * 65)
    print(f"TONG KET: {passed}/{len(test_cases)} tinh huong dat")
    print("Chua dat:", failed)
    print("=" * 65)


if __name__ == "__main__":
    main()
