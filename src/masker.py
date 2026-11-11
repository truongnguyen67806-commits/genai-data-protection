
def mask_sensitive_data(input_text, entities):
    """
    Che dữ liệu nhạy cảm dựa trên danh sách thực thể đã phát hiện.

    Thay thế thực thể bằng [TÊN_NHÃN].
    """

    masked_text = input_text

    # Sắp xếp từ vị trí cuối về đầu để không làm sai lệch
    # vị trí của những thực thể đứng trước.
    sorted_entities = sorted(
        entities,
        key=lambda item: item["start"],
        reverse=True
    )

    for entity in sorted_entities:
        start = entity["start"]
        end = entity["end"]
        label = entity["label"]

        replacement = f"[{label}]"

        masked_text = (
            masked_text[:start]
            + replacement
            + masked_text[end:]
        )

    return masked_text
