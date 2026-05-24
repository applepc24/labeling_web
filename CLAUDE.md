# YOLOv8 영상 객체 탐지 웹 서비스

## 프로젝트 개요
Streamlit 기반 YOLOv8 영상 객체 탐지 서비스.
영상을 업로드하면 프레임별 추론 → SQLite 적재 → 대시보드 시각화까지 처리한다.

## 기술 스택
- **프론트/서버**: Streamlit
- **AI**: YOLOv8 (ultralytics), `best.pt` 모델
- **DB**: SQLite (스타 스키마)
- **알림**: Slack Webhook
- **배포**: Streamlit Cloud

## 폴더 구조
```
labeling_web/
├── app.py              # 메인 진입점, 탭 구성
├── config.py           # 전역 상수 (임계값, 경로 등)
├── requirements.txt
├── data/
│   ├── raw/videos/     # 업로드된 원본 영상
│   └── low_confidence_data.json  # confidence < 0.8 결과
├── db/
│   ├── schema.sql      # 테이블 생성 SQL (T-06)
│   └── database.py     # DB 연결 및 CRUD (T-07, T-08)
├── pipeline/
│   ├── ingest.py       # 영상 수집 및 큐 등록 (T-02, T-03)
│   ├── inference.py    # YOLO 추론 (T-02)
│   ├── transform.py    # 결과 정규화 및 검증 (T-03)
│   ├── load.py         # SQLite 적재 (T-03, T-07)
│   └── retry.py        # 자동 재시도 로직 (T-04)
├── views/
│   ├── upload.py       # 업로드 & 탐지 페이지 (T-02)
│   ├── history.py      # 히스토리 조회 페이지 (T-08)
│   ├── dashboard.py    # 통계 대시보드 페이지 (T-12, T-13)
│   └── reprocess.py    # 수동 재처리 페이지 (T-10)
├── utils/
│   ├── slack.py        # Slack Webhook 알림 (T-14)
│   └── export.py       # CSV 내보내기 (T-15)
└── models/
    └── loader.py       # best.pt 로드 및 캐싱 (T-01)
```

## DB 스키마 (스타 스키마)
- `dim_videos`: 업로드 영상 메타데이터 (id, video_name, file_size, fps, duration, upload_at)
- `fact_detections`: 프레임별 탐지 결과 (id, video_id, frame_idx, class_name, confidence, bbox_x/y/w/h, created_at)
- `agg_stats`: 영상×클래스 집계 (id, video_id, class_name, count, avg_confidence, date)
- `pipeline_logs`: 파이프라인 실행 로그 (id, video_name, status, error_msg, retry_count, created_at)

## 핵심 설정값 (`config.py`)
| 상수 | 기본값 | 설명 |
|------|--------|------|
| `CONFIDENCE_THRESHOLD` | 0.8 | 이 값 미만은 low_confidence로 분류 |
| `MAX_RETRY` | 3 | 파이프라인 실패 시 최대 재시도 횟수 |
| `IMAGE_SIZE` | 640 | YOLO 입력 이미지 크기 |
| `DB_PATH` | db/detections.db | SQLite 파일 경로 |

## 티켓 배분

### 본인 (아키텍처/파이프라인)
| 티켓 | 내용 | 담당 파일 |
|------|------|-----------|
| T-01 | 환경 세팅 및 YOLO 연동 | `models/loader.py` |
| T-02 | 영상 업로드 → 프레임 분리 → 추론 → 결과 표시 | `pipeline/ingest.py`, `pipeline/inference.py`, `views/upload.py` |
| T-03 | ETL 파이프라인 구현 | `pipeline/transform.py`, `pipeline/load.py` |
| T-04 | 실패 처리 자동 재시도 로직 | `pipeline/retry.py` |
| T-05 | 전체 통합 테스트 및 배포 | - |

### 팀원 A (DB 담당)
| 티켓 | 내용 | 담당 파일 |
|------|------|-----------|
| T-06 | 스타 스키마 테이블 생성 SQL | `db/schema.sql` |
| T-07 | 탐지 결과 SQLite 적재 함수 | `db/database.py`, `pipeline/load.py` |
| T-08 | 히스토리 조회 쿼리 및 Streamlit 표시 | `db/database.py`, `views/history.py` |
| T-09 | Confidence 임계값 이하 데이터 별도 저장 | `pipeline/transform.py` → `data/low_confidence_data.json` |
| T-10 | 수동 재처리 UI | `views/reprocess.py` |

### 팀원 B (기능 담당)
| 티켓 | 내용 | 담당 파일 |
|------|------|-----------|
| T-11 | 테스트 영상 수집 및 포맷 통일 | `data/raw/videos/` |
| T-12 | 클래스 분포 차트 (Plotly) | `views/dashboard.py` |
| T-13 | 시간대별 탐지량 차트 (Plotly) | `views/dashboard.py` |
| T-14 | Slack Webhook 알림 구현 | `utils/slack.py` |
| T-15 | CSV 내보내기 기능 | `utils/export.py` |

## 의존 관계
```
app.py
  └── views/*.py
        ├── pipeline/*.py   ← 추론/ETL 로직
        ├── db/database.py  ← CRUD
        ├── utils/*.py      ← Slack, CSV
        └── config.py       ← 공통 상수
```

## 주의사항
- `best.pt`, `*.db`, `data/raw/videos/*` 는 `.gitignore` 대상 — 커밋 금지
- 각 page 모듈은 반드시 `render()` 함수를 노출해야 `app.py`에서 호출 가능
- DB 연결은 `db/database.py`의 `get_conn()` 컨텍스트 매니저만 사용
- Confidence 임계값은 항상 `config.CONFIDENCE_THRESHOLD`를 참조 (하드코딩 금지)
