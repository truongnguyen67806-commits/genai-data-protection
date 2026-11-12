
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

# =========================================================
# SINH NOI DUNG AM TINH DA DANG
# =========================================================

def build_negative_text(scenario, is_hard_negative, variant_index):
    """Sinh câu âm tính theo kịch bản, không chứa thực thể nhạy cảm."""

    clean_templates = {
        "hoc_tap": [
            "Nhóm sinh viên đang thảo luận về {} trong buổi học.",
            "Giảng viên yêu cầu lớp tìm hiểu thêm về {}.",
            "Bài tập tuần này tập trung phân tích {}.",
            "Tài liệu học tập trình bày kiến thức về {}.",
            "Các thành viên cùng trao đổi phương pháp {}.",
            "Buổi thảo luận hôm nay đề cập đến {}.",
            "Nhóm nghiên cứu đang hoàn thiện nội dung về {}.",
            "Sinh viên cần đọc thêm tài liệu liên quan đến {}.",
        ],
        "hanh_chinh": [
            "Phòng đào tạo đang cập nhật hướng dẫn về {}.",
            "Biểu mẫu hành chính được thiết kế để phục vụ {}.",
            "Bộ phận hỗ trợ đang rà soát quy trình {}.",
            "Thông báo mới trình bày các bước thực hiện {}.",
            "Nhà trường đang cải tiến quy trình {}.",
            "Tài liệu hướng dẫn giải thích cách thực hiện {}.",
            "Cuộc họp hôm nay tập trung vào nội dung {}.",
            "Bộ phận hành chính đang tổng hợp thông tin về {}.",
        ],
        "cntt": [
            "Nhóm phát triển đang kiểm thử chức năng {}.",
            "Máy chủ thử nghiệm được cấu hình để phục vụ {}.",
            "Bài thực hành hướng dẫn cách triển khai {}.",
            "Hệ thống cần tối ưu quy trình {}.",
            "Lập trình viên đang nghiên cứu phương pháp {}.",
            "Tài liệu kỹ thuật mô tả hoạt động của {}.",
            "Nhóm CNTT đang đánh giá hiệu năng {}.",
            "Cơ sở dữ liệu thử nghiệm được dùng để minh họa {}.",
        ],
    }

    clean_topics = {
        "hoc_tap": [
            "học máy", "phân loại văn bản", "trí tuệ nhân tạo",
            "phương pháp nghiên cứu", "xử lý ngôn ngữ tự nhiên",
            "học trực tuyến", "phân tích dữ liệu", "làm việc nhóm",
        ],
        "hanh_chinh": [
            "đăng ký học phần", "quản lý tài liệu", "tiếp nhận yêu cầu",
            "xử lý biểu mẫu", "lưu trữ hồ sơ", "quản lý lịch học",
            "cải tiến dịch vụ", "số hóa quy trình",
        ],
        "cntt": [
            "sắp xếp dữ liệu", "kiểm thử phần mềm", "truy vấn SQL",
            "tối ưu thuật toán", "xử lý ngoại lệ", "sao lưu dữ liệu",
            "phân tích nhật ký", "quản lý phiên bản",
        ],
    }

    hard_templates = {
        "hoc_tap": [
            "Tài liệu môn học dùng mã minh họa {} để giải thích định dạng.",
            "Bài thực hành trình bày chuỗi ví dụ {}.",
            "Giảng viên sử dụng giá trị giả lập {} trong bài giảng.",
            "Nội dung học tập giải thích ý nghĩa của ký hiệu {}.",
        ],
        "hanh_chinh": [
            "Biểu mẫu hướng dẫn sử dụng ký hiệu giữ chỗ {}.",
            "Tài liệu quy trình ghi giá trị minh họa {}.",
            "Thông báo giải thích định dạng mẫu {}.",
            "Hướng dẫn hành chính dùng chuỗi giả lập {} để minh họa.",
        ],
        "cntt": [
            "Log kiểm thử ghi nhận giá trị ví dụ {}.",
            "Môi trường lab sử dụng chuỗi giả lập {}.",
            "Tài liệu kỹ thuật giải thích định dạng {}.",
            "Bài thực hành dùng giá trị minh họa {} để kiểm tra xử lý.",
        ],
    }

    hard_examples = [
        "VERSION-EXAMPLE",
        "PORT-EXAMPLE",
        "COURSE-CODE-EXAMPLE",
        "IP-EXAMPLE",
        "PHONE-PLACEHOLDER",
        "STUDENT-ID-PLACEHOLDER",
        "ORDER-ID-EXAMPLE",
        "UUID-EXAMPLE",
        "EMAIL-EXAMPLE",
        "ERROR-CODE-EXAMPLE",
        "HASH-EXAMPLE",
        "PUBLIC-HOTLINE-REFERENCE",
    ]

    if is_hard_negative:
        variants = [
            template.format(example)
            for template in hard_templates[scenario]
            for example in hard_examples
        ]
    else:
        variants = [
            template.format(topic)
            for template in clean_templates[scenario]
            for topic in clean_topics[scenario]
        ]

    return variants[variant_index % len(variants)]

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
    negative_variant_counters = {
        (scenario, is_hard): 0
        for scenario in SCENARIOS
        for is_hard in (True, False)
    }

    for split, total, positive_count, negative_count in split_plan:

        # Mỗi split có mã template riêng để tránh dùng chung template_id.
        for local_index in range(total):
            sample_index += 1

            if local_index < positive_count:
                # Moi mau co 2-4 nhan khac nhau.
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

                scenario = SCENARIOS[negative_index % len(SCENARIOS)]

                variant_key = (scenario, is_hard_negative)
                variant_index = negative_variant_counters[variant_key]

                text = build_negative_text(
                    scenario,
                    is_hard_negative,
                    variant_index,
                )

                negative_variant_counters[variant_key] += 1

                template_type = "HARD" if is_hard_negative else "CLEAN"
                entities = []

                template_id = (
                    f"{split.upper()}-NEG-{template_type}-{scenario.upper()}"
                )

            text = unicodedata.normalize("NFC", text)

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
                    re.search(
                        r"[\u00e0-\u1ef9\u00c0-\u1ef8\u0111\u0110]",
                        text,
                    )
                ),
                "review_status": "DRAFT",
                "reviewer": "",
                "note": "Synthetic data; manual review required.",
            }

            records.append(record)
    return records


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
