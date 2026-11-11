
HIGH_RISK_LABELS = {
    "NATIONAL_ID",
    "BANK_ACCOUNT",
    "CREDENTIAL",
    "SECRET_KEY",
}

MEDIUM_RISK_LABELS = {
    "PHONE",
    "EMAIL",
    "STUDENT_ID",
    "ADDRESS",
    "ACADEMIC_RECORD",
}


def analyze_risk(entities):
    """
    Phân tích mức độ rủi ro dựa trên danh sách thực thể
    được phát hiện bởi Hybrid Detector.

    Trả về:
    - level: NONE, LOW, MEDIUM hoặc HIGH
    - score: điểm rủi ro
    - reasons: danh sách lý do
    """

    if not entities:
        return {
            "level": "NONE",
            "score": 0,
            "reasons": ["Không phát hiện dữ liệu nhạy cảm."]
        }

    labels = [entity["label"] for entity in entities]
    unique_labels = set(labels)

    reasons = []

    # Điều kiện HIGH
    if unique_labels & HIGH_RISK_LABELS:
        reasons.append("Phát hiện dữ liệu nhạy cảm có mức độ rủi ro cao.")

    if (
        "ACADEMIC_RECORD" in unique_labels
        and (
            "PERSON_NAME" in unique_labels
            or "STUDENT_ID" in unique_labels
        )
    ):
        reasons.append(
            "Hồ sơ học tập đi kèm thông tin định danh cá nhân."
        )

    if len(unique_labels) >= 3:
        reasons.append("Phát hiện từ 3 loại dữ liệu nhạy cảm khác nhau.")

    if len(entities) >= 5:
        reasons.append("Phát hiện từ 5 thực thể nhạy cảm trở lên.")

    if reasons:
        return {
            "level": "HIGH",
            "score": 3,
            "reasons": reasons
        }

    # Điều kiện LOW
    if set(labels) == {"PERSON_NAME"}:
        return {
            "level": "LOW",
            "score": 1,
            "reasons": ["Chỉ phát hiện thông tin họ tên cá nhân."]
        }

    # Điều kiện MEDIUM
    if unique_labels & MEDIUM_RISK_LABELS:
        return {
            "level": "MEDIUM",
            "score": 2,
            "reasons": [
                "Phát hiện dữ liệu cá nhân cần được xem xét trước khi gửi."
            ]
        }

    # Trường hợp nhãn chưa được quy định
    return {
        "level": "LOW",
        "score": 1,
        "reasons": ["Phát hiện thực thể cần được xem xét."]
    }
