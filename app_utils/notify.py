import streamlit as st
import config


def notify_detection_complete(video_name: str, high_count: int, low_count: int) -> None:
    st.toast(
        f"탐지 완료: {video_name}\n"
        f"고신뢰도 {high_count}건 / 저신뢰도 {low_count}건",
        icon="✅",
    )


def notify_pipeline_error(video_name: str, error: str) -> None:
    st.toast(f"오류 발생: {video_name}\n{error}", icon="🚨")
