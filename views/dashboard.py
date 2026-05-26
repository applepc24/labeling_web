import json

import pandas as pd
import plotly.express as px
import streamlit as st

import config
from db.database import get_agg_stats, get_all_videos


def _class_chart(stats: list[dict]):
    """T-12: 클래스 분포 — 막대 + 파이"""
    df = pd.DataFrame(stats)
    class_df = df.groupby("class_name", as_index=False)["count"].sum()
    class_df = class_df.sort_values("count", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            class_df,
            x="class_name", y="count",
            title="클래스별 탐지 건수",
            labels={"class_name": "클래스", "count": "탐지 건수"},
            color="class_name",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.pie(class_df, names="class_name", values="count", title="클래스 분포")
        st.plotly_chart(fig, use_container_width=True)


def _video_detection_chart(videos: list[dict]):
    """T-13-1: 영상별 탐지 수"""
    df = pd.DataFrame(videos)[["video_name", "detection_count"]]
    df = df.sort_values("detection_count", ascending=False)
    fig = px.bar(
        df,
        x="video_name", y="detection_count",
        title="영상별 탐지 수",
        labels={"video_name": "영상", "detection_count": "탐지 건수"},
        color="video_name",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _confidence_chart(stats: list[dict]):
    """T-13-2: 클래스별 평균 confidence"""
    df = pd.DataFrame(stats)
    conf_df = df.groupby("class_name", as_index=False)["avg_confidence"].mean()
    conf_df = conf_df.sort_values("avg_confidence", ascending=False)
    fig = px.bar(
        conf_df,
        x="class_name", y="avg_confidence",
        title="클래스별 평균 Confidence",
        labels={"class_name": "클래스", "avg_confidence": "평균 Confidence"},
        range_y=[0, 1],
        color="avg_confidence",
        color_continuous_scale="RdYlGn",
    )
    st.plotly_chart(fig, use_container_width=True)


def _low_conf_ratio_chart(stats: list[dict]):
    """T-13-3: 고/저 신뢰도 비율"""
    high_count = sum(s["count"] for s in stats)

    low_count = 0
    if config.LOW_CONF_JSON.exists():
        try:
            data = json.loads(config.LOW_CONF_JSON.read_text(encoding="utf-8"))
            low_count = len(data) if isinstance(data, list) else 0
        except (json.JSONDecodeError, OSError):
            pass

    total = high_count + low_count
    if total == 0:
        st.info("데이터가 없습니다.")
        return

    fig = px.pie(
        names=["고신뢰도", "저신뢰도"],
        values=[high_count, low_count],
        title=f"고/저 신뢰도 비율 (기준 {config.CONFIDENCE_THRESHOLD})",
        color_discrete_sequence=["#2ecc71", "#e74c3c"],
    )
    st.plotly_chart(fig, use_container_width=True)


def render():
    st.header("📊 통계 대시보드")

    stats = get_agg_stats()
    videos = get_all_videos()

    if not stats:
        st.info("아직 탐지된 데이터가 없습니다. 영상을 업로드하고 탐지를 실행해주세요.")
        return

    total = sum(s["count"] for s in stats)
    c1, c2, c3 = st.columns(3)
    c1.metric("전체 탐지 건수", f"{total:,}")
    c2.metric("처리된 영상 수", len(videos))
    c3.metric("탐지된 클래스 수", len({s["class_name"] for s in stats}))

    st.divider()

    # T-12
    st.subheader("클래스 분포")
    _class_chart(stats)

    st.divider()

    # T-13
    st.subheader("상세 분석")
    _video_detection_chart(videos)

    col_conf, col_ratio = st.columns(2)
    with col_conf:
        _confidence_chart(stats)
    with col_ratio:
        _low_conf_ratio_chart(stats)
