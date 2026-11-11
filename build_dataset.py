
import csv
import json
import random
import re
import unicodedata
from collections import Counter
from pathlib import Path

# =========================================================
# CAU HINH
# =========================================================

SEED = 2026
TOTAL_SAMPLES = 1000

OUTPUT_DIR = Path("data")
JSONL_PATH = OUTPUT_DIR / "dataset_nhay_cam_vi.jsonl"
CSV_PATH = OUTPUT_DIR / "dataset_nhay_cam_vi.csv"
STATS_PATH = OUTPUT_DIR / "dataset_stats.json"

LABELS = [
    "PERSON_NAME",
    "STUDENT_ID",
    "PHONE",
    "EMAIL",
    "NATIONAL_ID",
    "BANK_ACCOUNT",
    "CREDENTIAL",
    "SECRET_KEY",
    "ACADEMIC_RECORD",
    "ADDRESS",
]

SCENARIOS = ["hoc_tap", "hanh_chinh", "cntt"]

rng = random.Random(SEED)


# =========================================================
# SINH GIA TRI GIA LAP
# =========================================================

FIRST_NAMES = [
    "An", "Bình", "Chi", "Dũng", "Hà",
    "Hùng", "Lan", "Linh", "Minh", "Nam",
    "Phương", "Quân", "Trang", "Tuấn", "Vy",
]

MIDDLE_NAMES = [
    "Văn", "Thị", "Hoàng", "Ngọc", "Đức",
    "Thanh", "Quốc", "Gia", "Anh",
]

LAST_NAMES = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng",
    "Phan", "Vũ", "Đặng", "Bùi", "Đỗ",
]

STREETS = [
    "Lê Lợi", "Trần Phú", "Lạch Tray",
    "Nguyễn Trãi", "Quang Trung", "Tô Hiệu",
]

CITIES = ["Hải Phòng", "Hà Nội", "Đà Nẵng", "Huế"]


def random_digits(length):
    return "".join(rng.choice("0123456789") for _ in range(length))


def make_value(label, index):
    """Tạo giá trị giả lập cho từng loại thực thể."""

    if label == "PERSON_NAME":
        return (
            f"{rng.choice(LAST_NAMES)} "
            f"{rng.choice(MIDDLE_NAMES)} "
            f"{rng.choice(FIRST_NAMES)}"
        )

    if label == "STUDENT_ID":
        return f"SV{2024 + index % 4}{random_digits(4)}"

    if label == "PHONE":
        return f"09{random_digits(8)}"

    if label == "EMAIL":
        return f"sv{index:04d}@example.com"

    if label == "NATIONAL_ID":
        return random_digits(12)

    if label == "BANK_ACCOUNT":
        return random_digits(12)

    if label == "CREDENTIAL":
        return f"DemoPass{index:04d}!"

    if label == "SECRET_KEY":
        return "sk-demo-" + random_digits(24)

    if label == "ACADEMIC_RECORD":
        return f"GPA: {rng.randint(20, 40) / 10:.1f}"

    if label == "ADDRESS":
        return (
            f"{rng.randint(1, 250)} Đường "
            f"{rng.choice(STREETS)}, {rng.choice(CITIES)}"
        )

    raise ValueError(f"Nhãn không hợp lệ: {label}")


LABEL_PREFIX = {
    "PERSON_NAME": "Họ tên",
    "STUDENT_ID": "Mã sinh viên",
    "PHONE": "Số điện thoại",
    "EMAIL": "Email",
    "NATIONAL_ID": "CCCD",
    "BANK_ACCOUNT": "Số tài khoản",
    "CREDENTIAL": "password",
    "SECRET_KEY": "API key",
    "ACADEMIC_RECORD": "Thông tin học tập",
    "ADDRESS": "Địa chỉ",
}


# =========================================================
# TAO NOI DUNG VA TINH OFFSET
# =========================================================

def build_sensitive_text(labels, sample_index, scenario):
    """Tạo văn bản và tính start/end trực tiếp từ chuỗi."""

    scenario_openers = {
        "hoc_tap": [
            "Trong hồ sơ học tập, ",
            "Khi làm bài tập nhóm, ",
            "Thông tin sinh viên gồm ",
        ],
        "hanh_chinh": [
            "Thông tin liên hệ: ",
            "Trong biểu mẫu hành chính, ",
            "Hồ sơ cần kiểm tra gồm ",
        ],
        "cntt": [
            "Trong cấu hình thử nghiệm, ",
            "Log mô phỏng ghi nhận ",
            "Thông tin kiểm thử hệ thống: ",
        ],
    }

    text = rng.choice(scenario_openers[scenario])
    entities = []
    text += f" (mẫu kiểm thử {sample_index})"

    for position, label in enumerate(labels):
        value = make_value(label, sample_index * 10 + position)
        prefix = LABEL_PREFIX[label] + ": "

        if position > 0:
            text += "; "

        text += prefix
        start = len(text)
        text += value
        end = len(text)

        entities.append({
            "start": start,
            "end": end,
            "label": label,
            "text": value,
        })

    text += "."
    return unicodedata.normalize("NFC", text), entities


# =========================================================
# TAO MAU KHONG CO DU LIEU NHAY CAM
# =========================================================

CLEAN_TEXTS = [
    "Hôm nay nhóm thảo luận về trí tuệ nhân tạo trong giáo dục.",
    "Hãy giải thích sự khác nhau giữa dữ liệu có cấu trúc và phi cấu trúc.",
    "Viết chương trình Python sắp xếp danh sách số nguyên.",
    "Sinh viên cần đọc tài liệu trước khi tham gia buổi thảo luận.",
    "Hệ thống cần cải thiện tốc độ xử lý truy vấn.",
    "Bài báo trình bày phương pháp học máy trong phân loại văn bản.",
    "Nhóm sẽ hoàn thiện báo cáo vào cuối học kỳ.",
    "Máy chủ thử nghiệm đang chạy phiên bản phần mềm mới.",
    "Hãy hướng dẫn cách tạo bảng trong cơ sở dữ liệu.",
    "Nội dung này chỉ trình bày kiến thức lập trình cơ bản.",
]

HARD_NEGATIVE_TEXTS = [
    "Phiên bản phần mềm hiện tại là 2.4.1.",
    "Máy chủ thử nghiệm sử dụng cổng dịch vụ 8080.",
    "Mã học phần của môn học là CNTT2026.",
    "Địa chỉ IP máy chủ thử nghiệm là 192.168.1.10.",
    "Ví dụ định dạng số điện thoại là 0xxxxxxxxx.",
    "Biểu mẫu yêu cầu người dùng điền [MSSV] vào ô tương ứng.",
    "Mã đơn hàng giả lập là DH202600123.",
    "Giá trị UUID mẫu là 123e4567-e89b-12d3-a456-426614174000.",
    "Email phòng ban minh họa là phongdaotao@example.edu.vn.",
    "Mã lỗi hệ thống được ghi nhận là ERR-404.",
    "Hàm kiểm tra chuỗi hash SHA256 trong bài thực hành.",
    "Hotline công khai của đơn vị được ghi trong tài liệu hướng dẫn.",
]


# =========================================================
# PHAN LOAI RUI RO
# =========================================================

HIGH_LABELS = {
    "NATIONAL_ID",
    "BANK_ACCOUNT",
    "CREDENTIAL",
    "SECRET_KEY",
}

MEDIUM_LABELS = {
    "PHONE",
    "EMAIL",
    "STUDENT_ID",
    "ADDRESS",
    "ACADEMIC_RECORD",
}


def calculate_risk(entities):
    labels = {entity["label"] for entity in entities}

    if not entities:
        return "none"

    if labels & HIGH_LABELS:
        return "high"

    if (
        "ACADEMIC_RECORD" in labels
        and labels & {"PERSON_NAME", "STUDENT_ID"}
    ):
        return "high"

    if len(labels) >= 3 or len(entities) >= 5:
        return "high"

    if labels == {"PERSON_NAME"}:
        return "low"

    if labels & MEDIUM_LABELS:
        return "medium"

    return "low"


# =========================================================
# SINH 1000 MAU
# =========================================================

def generate_dataset():
    records = []

    # Phân bổ theo kế hoạch: 700 train, 100 dev, 200 test.
    split_plan = [
        ("train", 700, 525, 175),
        ("dev", 100, 75, 25),
        ("test", 200, 150, 50),
    ]

    sample_index = 0

    for split, total, positive_count, negative_count in split_plan:

        # Mỗi split có mã template riêng để tránh dùng chung template_id.
        for local_index in range(total):
            sample_index += 1

            if local_index < positive_count:
                # Mỗi mẫu có 2–4 nhãn khác nhau.
                number_of_entities = 2 + (local_index % 3)
                start_label = (local_index * 3) % len(LABELS)

                selected_labels = [
                    LABELS[(start_label + offset) % len(LABELS)]
                    for offset in range(number_of_entities)
                ]

                scenario = SCENARIOS[local_index % len(SCENARIOS)]

                text, entities = build_sensitive_text(
                    selected_labels,
                    sample_index,
                    scenario,
                )

                template_id = (
                    f"{split.upper()}-POS-{scenario.upper()}-"
                    f"{number_of_entities}"
                )

            else:
                negative_index = local_index - positive_count
                is_hard_negative = negative_index < negative_count * 0.4

                if is_hard_negative:
                    text = HARD_NEGATIVE_TEXTS[
                        negative_index % len(HARD_NEGATIVE_TEXTS)
                    ]
                    template_type = "HARD"
                else:
                    text = CLEAN_TEXTS[
                        negative_index % len(CLEAN_TEXTS)
                    ]
                    template_type = "CLEAN"

                scenario = SCENARIOS[negative_index % len(SCENARIOS)]
                entities = []

                template_id = (
                    f"{split.upper()}-NEG-{template_type}-{scenario.upper()}"
                )

            text = unicodedata.normalize("NFC", text)
            text += f" (ID mau: {sample_index})"


            record = {
                "id": f"S{sample_index:04d}",
                "split": split,
                "scenario": scenario,
                "template_id": template_id,
                "text": text,
                "entities": entities,
                "risk_level": calculate_risk(entities),
                "has_sensitive": bool(entities),
                "no_diacritics": not bool(
        re.search(r"[à-ỹÀ-ỸđĐ]", text)
    ),
    "review_status": "DRAFT",
    "reviewer": "",
    "note": "Dữ liệu tổng hợp tự động; cần rà soát thủ công.",
}

records.append(record)


# =========================================================
# KIEM TRA CHAT LUONG DU LIEU
# =========================================================

def validate_dataset(records):
    errors = []

    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        errors.append("Có ID mẫu bị trùng.")

    seen_texts = {}

    for index, record in enumerate(records):
        text_value = record["text"]

        if text_value in seen_texts:
            errors.append(
                f"Văn bản bị trùng tại mẫu {seen_texts[text_value]} "
                f"và mẫu {index}: {text_value[:150]}"
        )
        else:
            seen_texts[text_value] = index

    template_splits = {}

    for record in records:
        template_id = record["template_id"]
        split = record["split"]

        if template_id in template_splits:
            if template_splits[template_id] != split:
                errors.append(
                    f"Template {template_id} xuất hiện ở nhiều split."
                )
        else:
            template_splits[template_id] = split

        text = record["text"]

        if text != unicodedata.normalize("NFC", text):
            errors.append(f"{record['id']}: văn bản chưa chuẩn hóa NFC.")

        previous_end = -1

        for entity in sorted(
            record["entities"],
            key=lambda item: item["start"]
        ):
            start = entity["start"]
            end = entity["end"]
            label = entity["label"]

            if label not in LABELS:
                errors.append(
                    f"{record['id']}: nhãn không hợp lệ {label}."
                )

            if start < 0 or end > len(text) or start >= end:
                errors.append(
                    f"{record['id']}: offset không hợp lệ."
                )
                continue

            if text[start:end] != entity["text"]:
                errors.append(
                    f"{record['id']}: offset không khớp {entity['text']}."
                )

            if start < previous_end:
                errors.append(
                    f"{record['id']}: có thực thể chồng lấn."
                )

            previous_end = end

        if record["has_sensitive"] != bool(record["entities"]):
            errors.append(
                f"{record['id']}: has_sensitive không khớp entities."
            )

    if len(records) != TOTAL_SAMPLES:
        errors.append(
            f"Số mẫu không đúng: {len(records)} thay vì {TOTAL_SAMPLES}."
        )

    return errors


# =========================================================
# LUU JSONL, CSV VA THONG KE
# =========================================================

def save_outputs(records):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with JSONL_PATH.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

    with CSV_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "split",
                "scenario",
                "template_id",
                "text",
                "entities",
                "risk_level",
                "has_sensitive",
                "no_diacritics",
            ],
        )
        writer.writeheader()

        for record in records:
            row = record.copy()
            row["entities"] = json.dumps(
                record["entities"],
                ensure_ascii=False
            )
            writer.writerow({
                key: row[key]
                for key in writer.fieldnames
            })

    split_stats = {}
    label_stats = Counter()
    scenario_stats = Counter()
    risk_stats = Counter()

    for split in ["train", "dev", "test"]:
        subset = [
            record for record in records
            if record["split"] == split
        ]

        entity_count = sum(
            len(record["entities"])
            for record in subset
        )

        split_stats[split] = {
            "samples": len(subset),
            "entities": entity_count,
            "sensitive_samples": sum(
                record["has_sensitive"] for record in subset
            ),
            "empty_samples": sum(
                not record["has_sensitive"] for record in subset
            ),
        }

    for record in records:
        scenario_stats[record["scenario"]] += 1
        risk_stats[record["risk_level"]] += 1

        for entity in record["entities"]:
            label_stats[entity["label"]] += 1

    stats = {
        "version": "draft-1.0",
        "seed": SEED,
        "total_samples": len(records),
        "total_entities": sum(
            len(record["entities"]) for record in records
        ),
        "split_stats": split_stats,
        "label_stats": dict(label_stats),
        "scenario_stats": dict(scenario_stats),
        "risk_stats": dict(risk_stats),
        "note": (
            "Du lieu tong hop tu dong, chua duoc xac nhan thu cong."
        ),
    }

    with STATS_PATH.open("w", encoding="utf-8") as file:
        json.dump(stats, file, ensure_ascii=False, indent=4)

    return stats


def main():
    print("=" * 60)
    print("TAO BO DU LIEU NHAY CAM TONG HOP")
    print("=" * 60)

    records = generate_dataset()
    errors = validate_dataset(records)

    if errors:
        print("\nPHAT HIEN LOI:")
        for error in errors:
            print("-", error)

        print("\nChua luu bo du lieu. Hay sua loi truoc.")
        return

    stats = save_outputs(records)

    print("\nKIEM TRA DU LIEU: DAT")
    print("Tong so mau:", stats["total_samples"])
    print("Tong so thuc the:", stats["total_entities"])

    print("\nPHAN BO TRAIN / DEV / TEST:")
    for split, values in stats["split_stats"].items():
        print(
            f"- {split}: {values['samples']} mau, "
            f"{values['entities']} thuc the"
        )

    print("\nSO LUONG THEO NHAN:")
    for label, count in sorted(stats["label_stats"].items()):
        print(f"- {label}: {count}")

    print("\nDa tao cac tep:")
    print("-", JSONL_PATH)
    print("-", CSV_PATH)
    print("-", STATS_PATH)


if __name__ == "__main__":
    main()
