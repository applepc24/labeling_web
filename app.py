import streamlit as st
from views.upload import render as render_upload
from views.history import render as render_history
from views.dashboard import render as render_dashboard
from views.reprocess import render as render_reprocess

st.set_page_config(
    page_title="YOLOv8 Object Detection",
    page_icon="🎯",
    layout="wide",
)

st.title("YOLOv8 영상 객체 탐지")

tab_upload, tab_history, tab_dashboard, tab_reprocess = st.tabs(
    ["📤 업로드 & 탐지", "📋 탐지 히스토리", "📊 통계 대시보드", "🔄 실패 재처리"]
)

with tab_upload:
    render_upload()

with tab_history:
    render_history()

with tab_dashboard:
    render_dashboard()

with tab_reprocess:
    render_reprocess()
