def iter_frames(video_path: str, sample_rate: int = 30):
    import cv2
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    idx = 0

    try:
          while True:
              ret, frame = cap.read()
              if not ret:
                  break
              if idx % sample_rate == 0:
                  yield idx, frame, total
              idx += 1
    finally:
        cap.release()