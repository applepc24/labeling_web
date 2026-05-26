"""T-12/T-13/T-15 단위 테스트"""
import datetime
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import config

# 임시 DB로 격리
_tmp_db = pathlib.Path(tempfile.mktemp(suffix=".db"))
config.DB_PATH = _tmp_db

from db.database import (
    get_agg_stats,
    get_all_videos,
    init_db,
    insert_detections,
    insert_video,
    upsert_agg_stats,
)
from utils.export import detections_to_csv

MOCK_DETS = [
    {"frame_idx": 0, "class_name": "cat", "confidence": 0.95, "bbox_x": 1, "bbox_y": 2, "bbox_w": 3, "bbox_h": 4},
    {"frame_idx": 1, "class_name": "dog", "confidence": 0.88, "bbox_x": 5, "bbox_y": 6, "bbox_w": 7, "bbox_h": 8},
    {"frame_idx": 2, "class_name": "cat", "confidence": 0.91, "bbox_x": 9, "bbox_y": 10, "bbox_w": 11, "bbox_h": 12},
]


def test_export_csv():
    csv_bytes = detections_to_csv(MOCK_DETS)
    text = csv_bytes.decode("utf-8-sig")
    lines = [l.strip() for l in text.strip().splitlines()]
    assert "class_name" in lines[0], f"header missing: {lines[0]}"
    assert "confidence" in lines[0]
    assert len(lines) == 4, f"expected 4 lines (header+3 rows), got {len(lines)}"
    print("PASS  export.detections_to_csv — 헤더/행 수 정상")


def test_db_videos():
    init_db()
    vid_id = insert_video("test.mp4", 1024, 30.0, 5.0)
    insert_detections(vid_id, MOCK_DETS)
    upsert_agg_stats(vid_id, MOCK_DETS, str(datetime.date.today()))

    videos = get_all_videos()
    assert len(videos) == 1, f"video count: {len(videos)}"
    assert videos[0]["detection_count"] == 3, f"detection_count: {videos[0]['detection_count']}"
    print("PASS  get_all_videos — detection_count=3 정상")


def test_db_stats():
    stats = get_agg_stats()
    assert len(stats) == 2, f"class count: {len(stats)}"

    cat = next(s for s in stats if s["class_name"] == "cat")
    assert cat["count"] == 2, f"cat count: {cat['count']}"
    assert abs(cat["avg_confidence"] - 0.93) < 0.01, f"avg_conf: {cat['avg_confidence']}"
    print("PASS  get_agg_stats — cat count=2, avg_confidence≈0.93 정상")


def test_dashboard_aggregation():
    import pandas as pd
    stats = get_agg_stats()
    df = pd.DataFrame(stats)

    # T-12: 클래스 분포 집계
    class_df = df.groupby("class_name", as_index=False)["count"].sum()
    assert class_df[class_df["class_name"] == "cat"]["count"].values[0] == 2
    assert class_df[class_df["class_name"] == "dog"]["count"].values[0] == 1
    print("PASS  T-12 클래스 집계 로직 정상")

    # T-13-2: confidence 집계
    conf_df = df.groupby("class_name", as_index=False)["avg_confidence"].mean()
    assert len(conf_df) == 2
    print("PASS  T-13 confidence 집계 로직 정상")

    # T-13-3: 고/저 신뢰도 비율
    high_count = sum(s["count"] for s in stats)
    assert high_count == 3
    print("PASS  T-13 고신뢰도 카운트 정상")


def test_dashboard_empty():
    """빈 DB에서 stats가 빈 리스트인지 확인"""
    empty_db = pathlib.Path(tempfile.mktemp(suffix=".db"))
    config.DB_PATH = empty_db
    init_db()
    stats = get_agg_stats()
    assert stats == [], f"empty stats expected, got: {stats}"
    videos = get_all_videos()
    assert videos == []
    print("PASS  빈 DB 조회 — 빈 리스트 반환 정상")
    empty_db.unlink()
    config.DB_PATH = _tmp_db


if __name__ == "__main__":
    try:
        test_export_csv()
        test_db_videos()
        test_db_stats()
        test_dashboard_aggregation()
        test_dashboard_empty()
        print("\n모든 테스트 통과")
    finally:
        if _tmp_db.exists():
            _tmp_db.unlink()
