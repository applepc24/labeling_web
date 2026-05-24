# YOLOv8 영상 객체 탐지 웹 서비스

Streamlit 기반 YOLOv8 영상 객체 탐지 서비스입니다.  
영상을 업로드하면 프레임별 추론 → SQLite 적재 → 대시보드 시각화까지 처리합니다.

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| 프론트/서버 | Streamlit |
| AI | YOLOv8 (ultralytics), `best.pt` |
| DB | SQLite (스타 스키마) |
| 시각화 | Plotly |
| 알림 | Slack Webhook |
| 배포 | Streamlit Cloud |

---

## 폴더 구조

```
labeling_web/
├── app.py              # 메인 진입점, 탭 구성
├── config.py           # 전역 상수 (임계값, 경로 등)
├── requirements.txt
├── CLAUDE.md           # AI 협업용 프로젝트 컨텍스트
├── .streamlit/
│   └── config.toml     # Streamlit 서버 설정 (업로드 용량, headless 등)
├── data/
│   ├── raw/videos/     # 업로드된 원본 영상 (gitignore)
│   └── low_confidence_data.json  # confidence 임계값 미만 결과
├── db/
│   ├── schema.sql      # 테이블 생성 SQL
│   └── database.py     # DB 연결 및 CRUD
├── pipeline/
│   ├── ingest.py       # 프레임 추출 (제너레이터, 샘플링)
│   ├── inference.py    # YOLO OBB 추론
│   ├── transform.py    # 결과 정규화 및 검증 (OBB 지원)
│   ├── load.py         # SQLite 적재
│   └── retry.py        # 자동 재시도 로직
├── views/
│   ├── upload.py       # 업로드 & 실시간 탐지 페이지
│   ├── history.py      # 히스토리 조회 페이지
│   ├── dashboard.py    # 통계 대시보드 페이지
│   └── reprocess.py    # 수동 재처리 페이지
├── utils/
│   ├── slack.py        # Slack Webhook 알림
│   └── export.py       # CSV 내보내기
└── models/
    └── loader.py       # best.pt 로드 및 캐싱 (lazy import)
```

---

## 로컬 실행 방법

```bash
# 1. 레포 클론
git clone <repo-url>
cd labeling_web

# 2. Python 3.10 이상 가상환경 생성
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 모델 파일 준비
# best.pt를 프로젝트 루트에 직접 복사하거나 <- 현재는 그냥 이렇게 진행
# config.py의 MODEL_GDRIVE_ID 설정 후 자동 다운로드

# 5. 앱 실행
streamlit run app.py

# Mac Apple Silicon(M1/M2/M3) 사용 시
# PyTorch OMP 초기화 hang 방지를 위해 아래 명령어 사용
# (models/loader.py에서 자동 설정되므로 일반적으로 불필요)
streamlit run app.py
```

> **첫 실행 시 주의**  
> 첫 탐지 시 PyTorch 및 YOLO 모델 로드로 수십 초~수 분이 걸릴 수 있습니다. 이후 실행부터는 캐시되어 빠릅니다.
>
> **Mac Apple Silicon(M1/M2/M3) 추가 설정**  
> PyTorch + MPS 초기화 hang 방지를 위해 아래 설정을 권장합니다.
> ```bash
> mkdir -p ~/.config/Ultralytics && echo "sync: false" >> ~/.config/Ultralytics/settings.yaml
> ```

---

## 티켓 배분

### 본인 (아키텍처/파이프라인)

| 티켓 | 내용 | 담당 파일 |
|------|------|-----------|
| T-01 | 환경 세팅 및 YOLO 연동 | `models/loader.py` |
| T-02 | 영상 업로드 → 프레임 분리 → 추론 → 결과 표시 | `pipeline/ingest.py`, `pipeline/inference.py`, `views/upload.py` |
| T-03 | ETL 파이프라인 구현 | `pipeline/transform.py`, `pipeline/load.py` |
| T-04 | 실패 처리 자동 재시도 로직 | `pipeline/retry.py` |
| T-05 | 전체 통합 테스트 및 배포 | - |

### 이재민 (DB 담당)

| 티켓 | 내용 | 담당 파일 |
|------|------|-----------|
| T-06 | 스타 스키마 테이블 생성 SQL | `db/schema.sql` |
| T-07 | 탐지 결과 SQLite 적재 함수 | `db/database.py`, `pipeline/load.py` |
| T-08 | 히스토리 조회 쿼리 및 Streamlit 표시 | `db/database.py`, `views/history.py` |
| T-09 | Confidence 임계값 이하 데이터 별도 저장 | `pipeline/transform.py` |
| T-10 | 수동 재처리 UI | `views/reprocess.py` |

### 이영준 (기능 담당)

| 티켓 | 내용 | 담당 파일 |
|------|------|-----------|
| T-11 | 테스트 영상 수집 및 포맷 통일 | `data/raw/videos/` |
| T-12 | 클래스 분포 차트 (Plotly) | `views/dashboard.py` |
| T-13 | 시간대별 탐지량 차트 (Plotly) | `views/dashboard.py` |
| T-14 | Slack Webhook 알림 구현 | `utils/slack.py` |
| T-15 | CSV 내보내기 기능 | `utils/export.py` |

---

## 주의사항

- `best.pt`, `*.db`, `data/raw/videos/*` 는 `.gitignore` 대상 — 커밋 금지
- 각 views 모듈은 반드시 `render()` 함수를 노출해야 `app.py`에서 호출 가능
- DB 연결은 `db/database.py`의 `get_conn()` 컨텍스트 매니저만 사용
- Confidence 임계값은 항상 `config.CONFIDENCE_THRESHOLD` 참조 (하드코딩 금지)

---

## Git 협업 가이드 (처음 하시는 분들을 위해)

> Git이 처음이어도 괜찮아요. 아래 순서대로 따라 하시면 됩니다.

---

### 1단계 — 프로젝트 내 컴퓨터로 가져오기 (git clone)

Git에서 **clone**은 "인터넷에 있는 프로젝트를 내 컴퓨터에 복사해 온다"는 뜻입니다.  
마치 공유 드라이브에 있는 파일을 내 PC에 내려받는 것과 같아요.

```bash
# 터미널(Mac) 또는 명령 프롬프트(Windows)를 열고 입력하세요
git clone https://github.com/계정이름/저장소이름.git

# 복사된 폴더로 이동
cd labeling_web
```

> **어디서 URL을 복사하나요?**  
> GitHub 저장소 페이지에서 초록색 `<> Code` 버튼을 클릭하면 주소가 나옵니다.  
> 그 주소를 복사해서 `git clone` 뒤에 붙여넣으면 됩니다.

---

### 2단계 — 내 작업 공간 만들기 (git branch)

**branch(브랜치)**는 "나만의 작업 공간"이라고 생각하면 됩니다.  
여러 사람이 동시에 같은 파일을 수정해도 서로 충돌이 나지 않도록, 각자 별도의 공간에서 작업하는 방식이에요.

예를 들어 Google Docs에서 "사본 만들기"를 해서 내 버전을 따로 편집하는 것과 비슷합니다.

```bash
# 브랜치를 새로 만들고 그 브랜치로 이동합니다
# 브랜치 이름은 내가 하는 작업을 알 수 있게 짓는 게 좋아요
git checkout -b feature/내작업이름

# 예시
git checkout -b feature/slack-notification   # 슬랙 알림 기능 작업할 때
git checkout -b feature/dashboard-chart      # 대시보드 차트 작업할 때
```

> `checkout -b`는 "이 이름의 브랜치를 새로 만들고 거기로 이동해줘"라는 명령입니다.  
> 이제부터 내가 수정하는 내용은 이 브랜치에만 저장되고, 팀의 공용 코드(`main`)는 건드리지 않아요.

---

### 3단계 — 수정한 내용 저장하고 올리기 (git push)

작업을 다 마쳤으면 변경 내용을 GitHub에 올려야 합니다.  
3개의 명령을 순서대로 실행하면 됩니다.

```bash
# ① 내가 수정한 파일들을 "올릴 목록"에 추가합니다
#    (점(.) 하나는 "현재 폴더의 모든 변경 파일"을 의미해요)
git add .

# ② 변경 내용에 설명(메모)을 붙여서 저장합니다
#    큰따옴표 안에 무엇을 수정했는지 간단하게 적어주세요
git commit -m "슬랙 알림 기능 구현 완료"

# ③ 내 브랜치를 GitHub(원격 저장소)에 올립니다
#    처음 올릴 때는 아래처럼 브랜치 이름을 함께 써야 합니다
git push origin feature/내작업이름
```

> **비유로 이해하기**
> - `git add` = 택배 상자에 물건 넣기
> - `git commit` = 상자에 운송장(메모) 붙이기
> - `git push` = 택배 회사에 맡기기 (GitHub에 전송)

---

### 4단계 — 팀 코드에 합쳐달라고 요청하기 (Pull Request)

GitHub에 내 브랜치를 올렸다면, 이제 팀장(또는 리뷰어)에게  
"내 코드를 공용 코드(`main`)에 합쳐주세요"라고 요청해야 합니다.  
이걸 **Pull Request(PR)** 라고 부릅니다.

**방법:**

1. GitHub 저장소 페이지에 접속합니다.
2. 상단에 **"Compare & pull request"** 라는 노란 버튼이 자동으로 뜹니다 — 클릭!  
   (버튼이 안 보이면 `Pull requests` 탭 → `New pull request` 버튼을 클릭하세요)
3. **제목**과 **내용**을 작성합니다.
   - 제목: 무슨 작업을 했는지 한 줄 요약 (예: `슬랙 알림 기능 구현`)
   - 내용: 어떤 파일을 수정했는지, 테스트는 어떻게 했는지 간단히 설명
4. `Create pull request` 버튼을 누르면 완료!

> 이후 팀장이 코드를 확인하고 문제가 없으면 `Merge`(합치기)를 눌러서  
> 여러분의 코드가 공용 코드에 반영됩니다.

---

### 전체 흐름 한눈에 보기

```
① git clone     → 프로젝트를 내 PC로 가져오기 (최초 1회)
② git checkout  → 내 작업 브랜치 만들기
③ (코드 수정)
④ git add       → 변경 파일 목록에 추가
⑤ git commit    → 변경 내용에 메모 달기
⑥ git push      → GitHub에 올리기
⑦ Pull Request  → 팀 코드에 합쳐달라고 요청
```
