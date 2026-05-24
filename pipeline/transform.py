import json
import config

def transform(results: list) -> tuple[list, list]:
    high = []
    low = []

    for frame_idx, result in enumerate(results):
        for box in result.boxes:
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            x, y, w, h = box.xywh[0].tolist()

            row = {
                "frame_idx": frame_idx,
                "class_name": class_name,
                "confidence": confidence,
                "bbox_x": x,
                "bbox_y": y,
                "bbox_w": w,
                "bbox_h": h,
            }

            if confidence >= config.CONFIDENCE_THRESHOLD:
                high.append(row)
            else:
                low.append(row)
    return high, low

def save_low_confidence(low: list):
    config.LOW_CONF_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(config.LOW_CONF_JSON, "w", encoding="utf-8") as f:
        json.dump(low, f, ensure_ascii=False, indent=2)