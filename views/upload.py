import streamlit as st
from models.loader import load_model
from pipeline.ingest import iter_frames
from pipeline.inference  import run_inference
from pipeline.transform import transform, save_low_confidence
from utils.slack import notify_detection_complete
from utils.export import render_download_button
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
            model = load_model()
            progress = st.progress(0, text="추론 중 ...")
            col_video, col_log = st.columns([2, 1])
            frame_placeholder = col_video.empty()
            log_placeholder = col_log.empty()
            log_entries = []
            high_all = []
            low_all = []

            for frame_idx, result, total in run_inference(iter_frames(tmp_path), model):
                pct = min(int((frame_idx+1) / total * 100), 100)
                progress.progress(pct, text=f"추론 중... {pct}%")
                h, l = transform([result])
                high_all.extend(h)
                low_all.extend(l)

                frame_placeholder.image(result.plot(), channels="BGR")

                for det in h + l:
                    log_entries.append(f"[{frame_idx}] {det['class_name']} {det['confidence']:.2f}")
                log_placeholder.text("\n".join(log_entries[-30:]))
            
            progress.empty()
            save_low_confidence(low_all)
            st.success(f"완료! {len(high_all)}개 탐지 완료 (low confidence: {len(low_all)}개)")
            notify_detection_complete(uploaded_file.name, len(high_all), len(low_all))
            render_download_button(high_all, f"{uploaded_file.name}_detections.csv")

        finally:
            os.remove(tmp_path)