import streamlit as st


def detections_to_csv(detections: list[dict]) -> bytes:
    import pandas as pd
    df = pd.DataFrame(detections)
    return df.to_csv(index=False).encode("utf-8-sig")


def render_download_button(detections: list[dict], filename: str = "detections.csv") -> None:
    if not detections:
        st.warning("내보낼 탐지 데이터가 없습니다.")
        return
    st.download_button(
        label="📥 CSV 내보내기",
        data=detections_to_csv(detections),
        file_name=filename,
        mime="text/csv",
    )
