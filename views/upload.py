import os
import tempfile

import streamlit as st

import db.database as db
from models.loader import load_model
from pipeline.ingest import iter_frames
from pipeline.inference import run_inference
from pipeline.load import load_to_db
from pipeline.transform import transform, save_low_confidence
from app_utils.export import render_download_button
from app_utils.notify import notify_detection_complete, notify_pipeline_error


def _get_video_meta(path: str) -> tuple[float, float]:
    import cv2
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = frame_count / fps if fps else 0.0
    cap.release()
    return fps, duration


def render():
    st.header("📤 업로드 & 탐지")

    uploaded_file = st.file_uploader("영상 파일을 업로드하세요", type=["mp4", "avi", "mov"])

    if uploaded_file is not None:
        st.session_state['file_bytes'] = uploaded_file.getvalue()
        st.session_state['file_name'] = uploaded_file.name

    if 'file_bytes' not in st.session_state or 'file_name' not in st.session_state:
        return

    file_name = st.session_state['file_name']

    if st.button("탐지 시작"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(st.session_state['file_bytes'])
            tmp_path = tmp.name

        log_id = None
        try:
            import cv2
            log_id = db.log_pipeline(file_name, status="running")
            model = load_model()
            fps, duration = _get_video_meta(tmp_path)
            file_size = os.path.getsize(tmp_path)

            progress = st.progress(0, text="추론 중 ...")
            log_placeholder = st.empty()
            log_entries = []
            high_all = []
            low_all = []
            annotated_frames = []

            for frame_idx, result, total in run_inference(iter_frames(tmp_path), model):
                pct = min(int((frame_idx + 1) / total * 100), 100)
                progress.progress(pct, text=f"추론 중... {pct}%")
                h, l = transform([result])
                high_all.extend(h)
                low_all.extend(l)
                annotated_frames.append(result.plot())

                for det in h + l:
                    log_entries.append(f"[{frame_idx}] {det['class_name']} {det['confidence']:.2f}")
                log_placeholder.text("\n".join(log_entries[-30:]))

            progress.empty()
            log_placeholder.empty()

            if annotated_frames:
                import subprocess
                h_px, w_px = annotated_frames[0].shape[:2]
                raw_path = tmp_path + "_raw.mp4"
                out_path = tmp_path + "_annotated.mp4"
                out = cv2.VideoWriter(raw_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (w_px, h_px))
                for f in annotated_frames:
                    out.write(f)
                out.release()
                subprocess.run(
                    ['ffmpeg', '-y', '-i', raw_path, '-vcodec', 'libx264', '-f', 'mp4', out_path],
                    capture_output=True
                )
                os.remove(raw_path)
                with open(out_path, 'rb') as vf:
                    st.video(vf.read())
                os.remove(out_path)

            save_low_confidence(low_all)

            load_to_db(
                video_name=file_name,
                file_size=file_size,
                fps=fps,
                duration=duration,
                detections=high_all,
            )
            db.update_pipeline_log(log_id, status="success")
            notify_detection_complete(file_name, len(high_all), len(low_all))
            render_download_button(high_all, f"{file_name}_detections.csv")

            st.success(f"완료! {len(high_all)}개 탐지 (low confidence: {len(low_all)}개) — DB 저장 완료")

        except Exception as e:
            if log_id is not None:
                db.update_pipeline_log(log_id, status="failed", error_msg=str(e))
            notify_pipeline_error(file_name, str(e))
            st.error(f"파이프라인 오류: {e}")

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
