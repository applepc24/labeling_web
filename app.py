import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import db.database as db
from views.upload import render as render_upload
from views.history import render as render_history
from views.dashboard import render as render_dashboard
from views.reprocess import render as render_reprocess

db.init_db()

st.set_page_config(
    page_title="YOLOv8 Object Detection",
    page_icon="🎯",
    layout="wide",
)

if "page" not in st.session_state:
    st.session_state.page = "upload"

with st.sidebar:
    st.title("🎯 YOLOv8 탐지")
    st.divider()
    if st.button("📤 업로드 & 탐지", use_container_width=True):
        st.session_state.page = "upload"
    if st.button("📋 탐지 히스토리", use_container_width=True):
        st.session_state.page = "history"
    if st.button("📊 통계 대시보드", use_container_width=True):
        st.session_state.page = "dashboard"
    if st.button("🔄 실패 재처리", use_container_width=True):
        st.session_state.page = "reprocess"

if st.session_state.page == "upload":
    render_upload()
elif st.session_state.page == "history":
    render_history()
elif st.session_state.page == "dashboard":
    render_dashboard()
elif st.session_state.page == "reprocess":
    render_reprocess()
