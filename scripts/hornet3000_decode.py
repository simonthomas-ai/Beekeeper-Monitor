"""Research-only YOLOv8 raw tensor decoder for the pinned hornet3000 ONNX model.

No licensing approval, camera integration, or validated species identification.
"""
import math

CLASSES = ("amel", "vcra", "vespsp", "vvel", "vzon")
VELUTINA_ID = 3


def _iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / (area_a + area_b - intersection) if area_a + area_b > intersection else 0.0


def decode_raw(output, *, confidence=0.5, iou_threshold=0.45, max_detections=100):
    """Decode [1,9,8400] xywh + 5 class scores; class-aware greedy NMS.

    Coordinates refer to the 640x640 model input, not original camera pixels.
    Output is UNVERIFIED candidate metadata, never a confirmed detection.
    """
    if not (0 < confidence <= 1 and 0 <= iou_threshold < 1 and
            isinstance(max_detections, int) and 1 <= max_detections <= 1000):
        raise ValueError("Invalid thresholds")
    if getattr(output, "shape", None) != (1, 9, 8400):
        raise ValueError("Unexpected model output shape")
    candidates = []
    for i in range(8400):
        values = [float(output[0, channel, i]) for channel in range(9)]
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Non-finite ONNX output")
        x, y, w, h = values[:4]
        scores = values[4:]
        if any(s < 0 or s > 1 for s in scores):
            raise ValueError("Invalid class probability")
        label = max(range(5), key=lambda j: scores[j])
        score = scores[label]
        if score < confidence or w <= 0 or h <= 0:
            continue
        box = [max(0., x - w / 2), max(0., y - h / 2),
               min(640., x + w / 2), min(640., y + h / 2)]
        if box[2] <= box[0] or box[3] <= box[1]:
            continue
        candidates.append({"class_id": label, "class_code": CLASSES[label],
                           "confidence": score, "box_xyxy_input_pixels": box,
                           "verification_status": "unverified"})
    candidates.sort(key=lambda d: d["confidence"], reverse=True)
    selected = []
    for candidate in candidates:
        if all(candidate["class_id"] != kept["class_id"] or
               _iou(candidate["box_xyxy_input_pixels"], kept["box_xyxy_input_pixels"]) <= iou_threshold
               for kept in selected):
            selected.append(candidate)
            if len(selected) == max_detections:
                break
    return selected
