CREATE TABLE IF NOT EXISTS dim_videos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    video_name  TEXT    NOT NULL,
    file_size   INTEGER,
    fps         REAL,
    duration    REAL,
    upload_at   TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS fact_detections (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id    INTEGER NOT NULL,
    frame_idx   INTEGER NOT NULL,
    class_name  TEXT    NOT NULL,
    confidence  REAL    NOT NULL,
    bbox_x      REAL,
    bbox_y      REAL,
    bbox_w      REAL,
    bbox_h      REAL,
    created_at  TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (video_id) REFERENCES dim_videos(id)
);

CREATE TABLE IF NOT EXISTS agg_stats (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id        INTEGER NOT NULL,
    class_name      TEXT    NOT NULL,
    count           INTEGER NOT NULL,
    avg_confidence  REAL    NOT NULL,
    date            TEXT    NOT NULL,
    FOREIGN KEY (video_id) REFERENCES dim_videos(id)
);

CREATE TABLE IF NOT EXISTS pipeline_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    video_name  TEXT    NOT NULL,
    status      TEXT    NOT NULL,
    error_msg   TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at  TEXT    DEFAULT (datetime('now'))
);
