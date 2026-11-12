import re

def detect_ner(text):
    from underthesea import ner

    tokens = ner(text)

    parsed_tokens = []
    search_from = 0

    # Tim vi tri tung token trong van ban goc
    for token in tokens:
        word = token[0]
        tag = token[3]

        start = text.find(word, search_from)

        if start == -1:
            continue

        end = start + len(word)
        search_from = end

        parsed_tokens.append({
            "word": word,
            "tag": tag,
            "start": start,
            "end": end
        })

    groups = []
    current = None

    # Gom cac token PERSON va LOC theo nhan BIO
    for token in parsed_tokens:
        tag = token["tag"]

        if tag in ("B-PER", "B-LOC"):
            if current:
                groups.append(current)

            current = {
                "type": tag[2:],
                "start": token["start"],
                "end": token["end"]
            }

        elif tag in ("I-PER", "I-LOC"):
            entity_type = tag[2:]

            if current and current["type"] == entity_type:
                current["end"] = token["end"]
            else:
                if current:
                    groups.append(current)

                current = {
                    "type": entity_type,
                    "start": token["start"],
                    "end": token["end"]
                }

        else:
            if current:
                groups.append(current)
                current = None

    if current:
        groups.append(current)

    # Tach nhom PERSON va LOC
    person_groups = [
        group for group in groups
        if group["type"] == "PER"
    ]

    location_groups = [
        group for group in groups
        if group["type"] == "LOC"
    ]

    # Chi xem LOC la dia chi khi co ngu canh dia chi
    address_keywords = [
        "địa chỉ",
        "dia chi",
        "nơi ở",
        "noi o",
        "địa chỉ liên hệ",
        "address",
        "thường trú",
        "thuong tru"
    ]

    def has_nearby_address_context(start, window=60):
        context = text[max(0, start - window):start].lower()

        return any(
            keyword in context
            for keyword in address_keywords
        )

    # Gop cac vung LOC neu chung cach nhau boi dau phay
    merged_locations = []

    for group in location_groups:
        if not merged_locations:
            merged_locations.append(group.copy())
            continue

        previous = merged_locations[-1]
        gap = text[previous["end"]:group["start"]]

        if gap.strip() in (",", ""):
            previous["end"] = group["end"]
        else:
            merged_locations.append(group.copy())

    results = []

    # Cac tu khong duoc xem la ten nguoi
    # Cac tu khong duoc xem la ten nguoi
    person_exclusions = {
        "cccd",
        "cmnd",
        "gpa",
        "email",
        "api",
        "log",
        "mssv",
        "password",
        "điểm",
        "hồ sơ",
        "mã"
    }

    # Tao ket qua PERSON_NAME sau khi loc tu khoa
    for group in person_groups:
        person_text = text[group["start"]:group["end"]]
        normalized_person = person_text.strip().lower()

        if normalized_person in person_exclusions:
            continue

        results.append({
            "label": "PERSON_NAME",
            "text": person_text,
            "start": group["start"],
            "end": group["end"],
            "confidence": 0.80,
            "method": "NER"
        })

    # Tao ket qua ADDRESS neu co ngu canh phu hop
    for group in merged_locations:
        if has_nearby_address_context(group["start"]):
            start = group["start"]
            end = group["end"]

            # Mo rong lay so nha neu co ngay truoc ten duong
            prefix_start = max(0, start - 10)
            prefix = text[prefix_start:start]
            match = re.search(r"(\d+[A-Za-z]?)\s+$", prefix)

            if match:
                start = prefix_start + match.start(1)

            results.append({
                "label": "ADDRESS",
                "text": text[start:end],
                "start": start,
                "end": end,
                "confidence": 0.75,
                "method": "NER"
            })

    results.sort(key=lambda item: item["start"])

    return results