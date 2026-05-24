import streamlit as st
from ultralytics import YOLO
import gdown
import config

@st.cache_resource
def load_model() -> YOLO:
    if not config.MODEL_PATH.exists():
        _download_model()
    return YOLO(str(config.MODEL_PATH))

def _download_model():
    if not config.MODEL_GDRIVE_ID:
        raise FileNotFoundError("best.pt 파일이 없고, MODEL_GDRIVE_ID도 설정되지 않았습니다.")
    gdown.download(id=config.MODEL_GDRIVE_ID, output=str(config.MODEL_PATH), quiet=False)

