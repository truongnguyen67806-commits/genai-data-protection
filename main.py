
from src.hybrid_detector import detect_hybrid
from src.risk_analyzer import analyze_risk
from src.masker import mask_sensitive_data


def process_text(input_text):
    """
    Xử lý văn bản qua toàn bộ hệ thống bảo vệ dữ liệu.
    """

    # 1. Phát hiện dữ liệu nhạy cảm
    entities = detect_hybrid(input_text)

    # 2. Phân tích mức độ rủi ro
    risk = analyze_risk(entities)

    # 3. Che dữ liệu nhạy cảm
    masked_text = mask_sensitive_data(input_text, entities)

    # 4. Tổng hợp kết quả
    return {
        "original_text": input_text,
        "entities": entities,
        "risk": risk,
        "masked_text": masked_text
    }


def main():
    print("=" * 60)
    print("HE THONG PHAT HIEN VA BAO VE DU LIEU NHAY CAM")
    print("=" * 60)

    input_text = input("\nNhap van ban can kiem tra: ")

    result = process_text(input_text)

    print("\n========== KET QUA PHAN TICH ==========")

    print("\n1. Du lieu nhay cam phat hien:")
    if result["entities"]:
        for entity in result["entities"]:
            print(
                f"- {entity['label']}: {entity['text']} "
                f"(Phuong phap: {entity['method']})"
            )
    else:
        print("Khong phat hien du lieu nhay cam.")

    print("\n2. Muc do rui ro:")
    print("Muc do:", result["risk"]["level"])
    print("Diem:", result["risk"]["score"])

    print("\nLy do:")
    for reason in result["risk"]["reasons"]:
        print("-", reason)

    print("\n3. Van ban sau khi che:")
    print(result["masked_text"])

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
