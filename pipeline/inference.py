import config

def run_inference(frame_iter, model):
    for frame_idx, frame, total in frame_iter:
        result = model.predict(
            source=frame,
            conf=config.CONFIDENCE_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            imgsz=config.IMAGE_SIZE,
            verbose=False,
        )
        yield frame_idx, result[0], total