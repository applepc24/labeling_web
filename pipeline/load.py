from datetime import date

import db.database as db


def load_to_db(
    video_name: str,
    file_size: int,
    fps: float,
    duration: float,
    detections: list[dict],
) -> int:
    db.init_db()
    video_id = db.insert_video(video_name, file_size, fps, duration)
    if detections:
        db.insert_detections(video_id, detections)
        db.upsert_agg_stats(video_id, detections, date.today().isoformat())
    return video_id
