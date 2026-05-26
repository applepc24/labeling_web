import streamlit as st

import config
import db.database as db


def render():
    st.header("🔄 실패 재처리")

    if st.button("새로고침"):
        st.rerun()

    failed_logs = db.get_failed_logs()
    if not failed_logs:
        st.success("실패한 파이프라인이 없습니다.")
        return

    st.warning(f"실패한 파이프라인: {len(failed_logs)}건")

    for log in failed_logs:
        with st.expander(f"[#{log['id']}] {log['video_name']}  —  {log['created_at']}"):
            col1, col2 = st.columns(2)
            col1.metric("상태", log["status"])
            col2.metric("재시도 횟수", log["retry_count"])

            if log["error_msg"]:
                st.error(f"오류 내용: {log['error_msg']}")

            if log["retry_count"] >= config.MAX_RETRY:
                st.error(f"최대 재시도 횟수({config.MAX_RETRY})에 도달했습니다. 수동 확인이 필요합니다.")
            else:
                if st.button("재처리 시작", key=f"retry_{log['id']}"):
                    st.info("재처리 기능은 pipeline/retry.py (T-04) 구현 후 연동됩니다.")
