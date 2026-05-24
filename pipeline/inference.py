import config

def run_inference(frames: list, model) -> list:
    results = []

    for frame in frames:
        result = model.predict(
            source=frame,
            conf=config.CONFIDENCE_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            imgsz=config.IMAGE_SIZE,
            verbose=False,
        )
        results.append(result[0])
    return results