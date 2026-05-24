import streamlit as st
import config

@st.cache_resource
def load_model():
    import os
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    os.environ['OMP_NUM_THREADS'] = '1'
    from ultralytics import YOLO
    if not config.MODEL_PATH.exists():
        _download_model()
    return YOLO(str(config.MODEL_PATH))

def _download_model():
    import gdown
    if not config.MODEL_GDRIVE_ID:
        raise FileNotFoundError("best.pt 파일이 없고, MODEL_GDRIVE_ID도 설정되지 않았습니다.")
    gdown.download(id=config.MODEL_GDRIVE_ID, output=str(config.MODEL_PATH), quiet=False)

