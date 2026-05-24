import streamlit as st

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
    from views.upload import render
    render()

with tab_history:
    from views.history import render
    render()

with tab_dashboard:
    from views.dashboard import render
    render()

with tab_reprocess:
    from views.reprocess import render
    render()
