---
title: Labeling Web
emoji: 🎯
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.45.1"
python_version: "3.12"
app_file: app.py
pinned: false
---


# 🎯 Labeling Web — YOLOv8 영상 객체 탐지 웹 서비스

> 컨테이너 야적장 영상에서 객체를 자동 탐지하고 결과를 시각화하는 AI 웹 애플리케이션

🔗 **배포 링크**: [https://applepc24-labeling-web.hf.space](https://applepc24-labeling-web.hf.space)

---

## 📌 프로젝트 개요

영상을 업로드하면 YOLOv8 OBB 모델이 프레임별로 객체를 탐지하고,
결과를 SQLite에 적재한 뒤 Plotly 대시보드로 시각화까지 자동 처리합니다.

라벨링 → 모델 학습 → 웹 서비스 배포까지 ML 파이프라인 전 과정을 직접 구현했습니다.

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🎬 영상 업로드 & 실시간 탐지 | 영상 업로드 시 프레임 추출 → YOLOv8 추론 → 결과 표시 |
| 📊 통계 대시보드 | 클래스 분포, 시간대별 탐지량 차트 (Plotly) |
| 🗂 히스토리 조회 | 과거 탐지 결과 조회 및 필터링 |
| 🔁 수동 재처리 | 실패한 영상 수동 재추론 |
| 📤 CSV 내보내기 | 탐지 결과 CSV 다운로드 |

---

## 🗂 라벨링 & 데이터셋

### 라벨링 도구
- **툴**: Label Studio
- **방식**: OBB (Oriented Bounding Box) — 회전된 객체에 최적화된 방향성 바운딩 박스

### 탐지 클래스 (6종)

`person` · `cone` · `container` · `container_code` · `size_code` · `door`

### 데이터셋 구성

| 구분 | 방식 | 이미지 수 |
|------|------|-----------|
| 1차 | 3인이 각도별 50장씩 직접 촬영 & 수작업 라벨링 | 1,350장 |
| 2차 | 프리라벨링 결과를 수동 검수 & 수정 | 9,896장 |
| **합계** | | **11,246장** |

---

## 🤖 모델 학습 결과

### 학습 환경

> 모델 학습은 사내 학습 파이프라인을 활용했으며, 해당 코드는 미포함입니다.

### 학습 설정

| 항목 | 값 |
|------|----|
| task | obb (Oriented Bounding Box) |
| model | yolov8n-obb.pt |
| epochs | 100 |
| batch | 16 |
| imgsz | 640 |
| optimizer | auto |
| iou | 0.7 |

### 성능 비교

| 지표 | 1차 학습 (Best) | 2차 학습 (Best) |
|------|:---:|:---:|
| Best Epoch | 47 / 100 | 16 / 100 |
| mAP@0.5 | **0.7845** | 0.5179 |
| mAP@0.5-0.95 | **0.6083** | 0.3953 |
| Precision | **0.7536** | 0.4622 |
| Recall | 0.7218 | **0.8074** |

> 2차 학습은 데이터 규모(9,896장)를 대폭 늘렸으나 mAP가 하락했습니다.
> 프리라벨링 데이터의 라벨 품질 편차가 원인으로 추정되며, 현재 배포 모델은 1차 학습 결과물(best.pt)을 사용합니다.

---

## 🛠 기술 스택

| 분류 | 기술 |
|------|------|
| 프론트 / 서버 | Streamlit |
| AI | YOLOv8 OBB (ultralytics), best.pt |
| DB | SQLite (스타 스키마) |
| 시각화 | Plotly |
| 배포 | Hugging Face Spaces |

---

## 📁 폴더 구조

```
labeling_web/
├── app.py              # 메인 진입점, 탭 구성
├── config.py           # 전역 상수 (임계값, 경로 등)
├── requirements.txt
├── .streamlit/
│   └── config.toml     # 서버 설정 (업로드 용량, headless 등)
├── data/
│   └── low_confidence_data.json  # confidence 임계값 미만 결과
├── db/
│   ├── schema.sql      # 테이블 생성 SQL
│   └── database.py     # DB 연결 및 CRUD
├── pipeline/
│   ├── ingest.py       # 프레임 추출 (제너레이터, 샘플링)
│   ├── inference.py    # YOLO OBB 추론
│   ├── transform.py    # 결과 정규화 및 검증
│   ├── load.py         # SQLite 적재
│   └── retry.py        # 자동 재시도 로직
├── views/
│   ├── upload.py       # 업로드 & 추론 후 결과 영상 재생
│   ├── history.py      # 히스토리 조회
│   ├── dashboard.py    # 통계 대시보드
│   └── reprocess.py    # 수동 재처리
├── app_utils/
│   ├── notify.py       # 탐지 완료/오류 알림
│   └── export.py       # CSV 내보내기
└── models/
    └── loader.py       # best.pt 로드 및 캐싱
```

---

## 🚀 로컬 실행 방법

```bash
# 1. 레포 클론
git clone <repo-url>
cd labeling_web

# 2. 가상환경 생성 (Python 3.12)
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 모델 파일 준비
# best.pt를 프로젝트 루트에 복사

# 5. 앱 실행
streamlit run app.py
```

> **첫 실행 시**: PyTorch 및 YOLO 모델 로드로 수십 초~수 분이 걸릴 수 있습니다. 이후 실행부터는 캐시되어 빠릅니다.
