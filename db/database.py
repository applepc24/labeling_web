import sqlite3
import sys
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import config

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


@contextmanager
def get_conn():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.executescript(sql)


# ── dim_videos ──────────────────────────────────────────────────────────────

def insert_video(video_name: str, file_size: int, fps: float, duration: float) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO dim_videos (video_name, file_size, fps, duration) VALUES (?, ?, ?, ?)",
            (video_name, file_size, fps, duration),
        )
        return cur.lastrowid


def get_all_videos() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT v.*, COUNT(d.id) AS detection_count
               FROM dim_videos v
               LEFT JOIN fact_detections d ON v.id = d.video_id
               GROUP BY v.id
               ORDER BY v.upload_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]


# ── fact_detections ──────────────────────────────────────────────────────────

def insert_detections(video_id: int, detections: list[dict]):
    rows = [
        (
            video_id,
            d["frame_idx"],
            d["class_name"],
            d["confidence"],
            d["bbox_x"],
            d["bbox_y"],
            d["bbox_w"],
            d["bbox_h"],
        )
        for d in detections
    ]
    with get_conn() as conn:
        conn.executemany(
            """INSERT INTO fact_detections
               (video_id, frame_idx, class_name, confidence, bbox_x, bbox_y, bbox_w, bbox_h)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )


def get_detections_by_video(video_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM fact_detections WHERE video_id = ? ORDER BY frame_idx",
            (video_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# ── agg_stats ────────────────────────────────────────────────────────────────

def upsert_agg_stats(video_id: int, detections: list[dict], date: str):
    stats = defaultdict(lambda: {"count": 0, "total_conf": 0.0})
    for d in detections:
        cls = d["class_name"]
        stats[cls]["count"] += 1
        stats[cls]["total_conf"] += d["confidence"]

    rows = [
        (video_id, cls, v["count"], v["total_conf"] / v["count"], date)
        for cls, v in stats.items()
    ]
    with get_conn() as conn:
        conn.executemany(
            """INSERT INTO agg_stats (video_id, class_name, count, avg_confidence, date)
               VALUES (?, ?, ?, ?, ?)""",
            rows,
        )


def get_agg_stats(video_id: int | None = None) -> list[dict]:
    with get_conn() as conn:
        if video_id is not None:
            rows = conn.execute(
                "SELECT * FROM agg_stats WHERE video_id = ?", (video_id,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM agg_stats").fetchall()
        return [dict(r) for r in rows]


# ── pipeline_logs ────────────────────────────────────────────────────────────

def log_pipeline(video_name: str, status: str, error_msg: str = None, retry_count: int = 0) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO pipeline_logs (video_name, status, error_msg, retry_count) VALUES (?, ?, ?, ?)",
            (video_name, status, error_msg, retry_count),
        )
        return cur.lastrowid


def update_pipeline_log(log_id: int, status: str, error_msg: str = None, retry_count: int = None):
    with get_conn() as conn:
        if retry_count is not None:
            conn.execute(
                "UPDATE pipeline_logs SET status=?, error_msg=?, retry_count=? WHERE id=?",
                (status, error_msg, retry_count, log_id),
            )
        else:
            conn.execute(
                "UPDATE pipeline_logs SET status=?, error_msg=? WHERE id=?",
                (status, error_msg, log_id),
            )


def get_failed_logs() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM pipeline_logs WHERE status = 'failed' ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_logs() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM pipeline_logs ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
