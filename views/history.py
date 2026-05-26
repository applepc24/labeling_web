import pandas as pd
import streamlit as st

import db.database as db


def render():
    st.header("📋 탐지 히스토리")

    videos = db.get_all_videos()
    if not videos:
        st.info("업로드된 영상이 없습니다.")
        return

    df_videos = pd.DataFrame(videos).rename(columns={
        "id": "ID",
        "video_name": "영상명",
        "file_size": "파일크기(bytes)",
        "fps": "FPS",
        "duration": "길이(초)",
        "upload_at": "업로드 시각",
        "detection_count": "탐지 수",
    })

    st.subheader("업로드된 영상 목록")
    st.dataframe(df_videos, use_container_width=True)

    st.subheader("영상별 탐지 상세")
    video_options = {v["video_name"]: v["id"] for v in videos}
    selected = st.selectbox("영상 선택", list(video_options.keys()))

    if selected:
        detections = db.get_detections_by_video(video_options[selected])
        if detections:
            df = pd.DataFrame(detections).drop(columns=["id", "video_id"], errors="ignore")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("이 영상에 대한 탐지 결과가 없습니다.")
