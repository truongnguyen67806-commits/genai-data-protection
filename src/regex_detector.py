
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
        "cccd", "cmnd", "can cuoc", "chung minh nhan dan"
    ],
    "BANK_ACCOUNT": [
        "so tai khoan",
        "số tài khoản",
        "stk",
        "tai khoan ngan hang",
        "tài khoản ngân hàng"
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
        r"\s*[:=]\s*(\S{4,})"
    ),
    "ACADEMIC_RECORD": re.compile(
        r"(?i)(?:GPA|diem\s*trung\s*binh|"
        r"diem\s*thi|xep\s*loai|hoc\s*bong|"
        r"ky\s*luat|canh\s*cao\s*hoc\s*vu)"
        r"\s*[:=]?\s*"
        r"(3[.,]?\d?|[0-2][.,]\d+|[0-9]+|"
        r"gioi|kha|trung\s*binh|yeu|"
        r"duoc\s*cap|bi\s*canh\s*cao)"
    ),
}


def has_context(text, start, label, window=60):
    """
    Kiem tra tu khoa ngu canh o phia truoc du lieu.
    """
    keywords = CONTEXT_KEYWORDS.get(label, [])
    context = text[max(0, start - window):start].lower()

    return any(keyword in context for keyword in keywords)


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
            if label in [
                "STUDENT_ID",
                "CREDENTIAL",
                "ACADEMIC_RECORD"
            ]:
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
