import streamlit as st
from models.loader import load_model
from pipeline.ingest import extract_frames
from pipeline.inference  import run_inference
from pipeline.transform import transform, save_low_confidence
import tempfile
import os


def render():
    st.header("📤 업로드 & 탐지")
    
    uploaded_file = st.file_uploader("영상 파일을 업로드하세요", type=["mp4", "avi", "mov"])

    if uploaded_file is None:
        return
    
    if st.button("탐지시작"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        
        try:
            with st.spinner("프레임 추출 중 ..."):
                frames = extract_frames(tmp_path)
            
            with st.spinner(f"추론 중 ... (총 {len(frames)}프레임)"):
                model = load_model()
                results = run_inference(frames, model)
            
            high, low = transform(results)
            save_low_confidence(low)
            st.success(f"완료! {len(high)}개 탐지 완료 (low confidence: {len(low)}개)")
        finally:
            os.remove(tmp_path)