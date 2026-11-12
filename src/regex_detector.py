
import re
import unicodedata


def normalize_text(text):
    """Chuan hoa Unicode truoc khi xac dinh vi tri du lieu."""
    return unicodedata.normalize("NFC", text)


# Cac tu khoa dung de xac dinh ngu canh du lieu nhay cam
CONTEXT_KEYWORDS = {
    "STUDENT_ID": [
        "mssv",
        "mã sinh viên",
        "ma sinh vien",
        "student id"
    ],
    "NATIONAL_ID": [
        "cccd",
        "cmnd",
        "căn cước",
        "can cuoc",
        "chứng minh nhân dân",
        "chung minh nhan dan"
    ],
    "BANK_ACCOUNT": [
        "số tài khoản",
        "so tai khoan",
        "stk",
        "tài khoản ngân hàng",
        "tai khoan ngan hang"
    ],
}

# Cac mau Regex
PATTERNS = {
    "PHONE": re.compile(
        r"(?<!\d)(?:\+84|0084|0)(?:[\s.-]?\d){8,10}(?!\d)"
    ),

    "EMAIL": re.compile(
        r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
    ),

    "STUDENT_ID": re.compile(
        r"(?:mssv|mã\s*sinh\s*viên|ma\s*sinh\s*vien|student\s*id)"
        r"\s*[:#-]?\s*([A-Za-z0-9_-]{5,20})",
        re.IGNORECASE
    ),

    "NATIONAL_ID": re.compile(
        r"(?<!\d)(?:\d{9}|\d{12})(?!\d)"
    ),

    "BANK_ACCOUNT": re.compile(
        r"(?<!\d)\d{9,14}(?!\d)"
    ),

    "SECRET_KEY": re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{16,}|"
        r"AIza[A-Za-z0-9_-]{20,})\b"
    ),

    "CREDENTIAL": re.compile(
        r"(?i)(?:mật\s*khẩu|mat\s*khau|password|passwd|"
        r"pin|otp|mã\s*xác\s*thực|ma\s*xac\s*thuc)"
        r"\s*[:=]\s*([^\s;,.]+[!?]?)"
    ),
    "ACADEMIC_RECORD": re.compile(
    r"(?i)((?:GPA|điểm\s*trung\s*bình|diem\s*trung\s*binh|"
    r"điểm\s*thi|diem\s*thi|xếp\s*loại|xep\s*loai|"
    r"học\s*bổng|hoc\s*bong|kỷ\s*luật|ky\s*luat|"
    r"cảnh\s*cáo\s*học\s*vụ|canh\s*cao\s*hoc\s*vu)"
    r"\s*[:=]?\s*"
    r"(?:[0-9]+[.,][0-9]+|[0-9]+|"
    r"giỏi|gioi|khá|kha|trung\s*bình|trung\s*binh|"
    r"yếu|yeu|được\s*cấp|duoc\s*cap|"
    r"bị\s*cảnh\s*cáo|bi\s*canh\s*cao))"
),
}


def has_context(text, start, label, window=60):
    """
    Xac dinh loai du lieu theo tu khoa ngu canh gan nhat.
    """
    context = text[max(0, start - window):start].lower()

    nearest_label = None
    nearest_position = -1

    for candidate_label in [
        "STUDENT_ID",
        "NATIONAL_ID",
        "BANK_ACCOUNT"
    ]:
        for keyword in CONTEXT_KEYWORDS.get(candidate_label, []):
            position = context.rfind(keyword)

            if position > nearest_position:
                nearest_position = position
                nearest_label = candidate_label

    return nearest_label == label


def detect_sensitive_entities(input_text):
    """
    Phat hien du lieu nhay cam bang Regex.

    start: vi tri bat dau.
    end: vi tri ket thuc, khong bao gom ky tu tai end.
    """

    text = normalize_text(input_text)
    results = []

    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(text):

            # Lay vi tri rieng cua gia tri du lieu
            # Lay vi tri cua du lieu nhay cam
            if label in ["STUDENT_ID", "CREDENTIAL", "ACADEMIC_RECORD"]:
                start, end = match.span(1)
            else:
                start, end = match.span()

            value = text[start:end]

            # Kiem tra ngu canh voi cac loai can tu khoa
            if label in [
                "STUDENT_ID",
                "NATIONAL_ID",
                "BANK_ACCOUNT"
            ]:
                if not has_context(text, start, label):
                    continue

            results.append({
                "label": label,
                "text": value,
                "start": start,
                "end": end,
                "confidence": 0.95,
                "method": "REGEX"
            })

    # Sap xep ket qua theo vi tri xuat hien
    results.sort(
        key=lambda item: (item["start"], item["end"])
    )

    return results


if __name__ == "__main__":

    sample_text = """
    Mat khau: DemoPass123
    GPA: 3.5
    Hôm nay tôi đi học ở thư viện.
    """

    print("VAN BAN KIEM THU:")
    print(sample_text)

    entities = detect_sensitive_entities(sample_text)

    print("\nKET QUA PHAT HIEN:")

    if not entities:
        print("Khong phat hien du lieu nhay cam.")
    else:
        for entity in entities:
            print(entity)
