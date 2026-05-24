from pathlib import Path

# --- 경로 ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_VIDEO_DIR = DATA_DIR / "raw" / "videos"
LOW_CONF_JSON = DATA_DIR / "low_confidence_data.json"
DB_PATH = BASE_DIR / "db" / "detections.db"
MODEL_PATH = BASE_DIR / "best.pt"

# --- 추론 ---
CONFIDENCE_THRESHOLD = 0.8
IOU_THRESHOLD = 0.45
IMAGE_SIZE = 640

# --- 파이프라인 ---
MAX_RETRY = 3

# --- Slack ---
SLACK_WEBHOOK_URL = ""  # st.secrets["SLACK_WEBHOOK_URL"] 로 교체 예정

# --- gdown ---
MODEL_GDRIVE_ID = ""  # best.pt Google Drive 파일 ID
