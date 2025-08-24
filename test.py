# Streamlit 학습 플래너 (장기 계획 + 하루 시간표 자동 생성)
# ------------------------------------------------------
# 사용법
# 1) 왼쪽 사이드바에서 기간, 하루 공부 시간, 시작 시각 등을 설정
# 2) 과목/중요도/시험일 등을 표로 입력 (예시 데이터 버튼 제공)
# 3) "계획 생성"을 누르면 날짜별 배분표와 하루 시간표(타임라인)가 생성됩니다.
# 4) CSV로 다운로드 가능
# ------------------------------------------------------

import math
import io
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Optional

import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="학습 플래너 | 시간표 자동 생성",
    page_icon="📅",
    layout="wide",
)

# -----------------------------
# 유틸
# -----------------------------
IMPORTANCE_MAP = {
    "매우 낮음": 1,
    "낮음": 2,
    "보통": 3,
    "높음": 4,
    "매우 높음": 5,
}

IMPORTANCE_ORDER = list(IMPORTANCE_MAP.keys())

@st.cache_data(show_spinner=False)
def _make_empty_subject_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "과목": [""],
            "중요도": ["보통"],
            "목표 총 학습시간(시간)": [np.nan],  # 비우면 자동배분
            "시험일(선택)": [pd.NaT],
        }
    )

@st.cache_data(show_spinner=False)
def _example_subject_df() -> pd.DataFrame:
    today = date.today()
    return pd.DataFrame(
        {
            "과목": ["국어", "수학", "영어", "사회"],
            "중요도": ["보통", "매우 높음", "높음", "낮음"],
            "목표 총 학습시간(시간)": [np.nan, 20, np.nan, 6],
            # 예시 시험일: 앞으로 7, 10, 14, 21일
            "시험일(선택)": [
                pd.to_datetime(today + timedelta(days=7)),
                pd.to_datetime(today + timedelta(days=10)),
                pd.to_datetime(today + timedelta(days=14)),
                pd.NaT,
            ],
        }
    )


def daterange(start: date, end: date) -> List[date]:
    days = []
    d = start
    while d <= end:
        days.append(d)
        d += timedelta(days=1)
    return days


def human_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# -----------------------------
# 사이드바 입력
# -----------------------------
with st.sidebar:
    st.header("⚙️ 설정")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("시작일", value=date.today())
    with col2:
        target_date = st.date_input("목표일", value=date.today() + timedelta(days=14), min_value=start_date)

    st.markdown("---")
    st.subheader("⏱️ 하루 공부 설정")
    colh1, colh2 = st.columns(2)
    with colh1:
        daily_hours_weekday = st.number_input("평일 공부시간(시간/일)", min_value=0.0, max_value=24.0, value=4.0, step=0.5)
    with colh2:
        daily_hours_weekend = st.number_input("주말 공부시간(시간/일)", min_value=0.0, max_value=24.0, value=6.0, step=0.5)

    start_clock = st.time_input("하루 시작 시각", value=time(9, 0))

    st.markdown("---")
    st.subheader("🍅 집중/휴식 블록")
    colb1, colb2 = st.columns(2)
    with colb1:
        focus_minutes = st.number_input("공부 블록(분)", min_value=20, max_value=180, value=50, step=5)
    with colb2:
        break_minutes = st.number_input("휴식(분)", min_value=0, max_value=60, value=10, step=5)

    st.markdown("---")
    st.subheader("⚖️ 배분 로직 가중치")
    urgency_strength = st.slider("시험 임박 가중치", min_value=0.0, max_value=3.0, value=1.2, step=0.1,
                               help="시험일이 가까울수록 더 많은 시간을 배정하는 정도")
    importance_strength = st.slider("중요도 가중치", min_value=0.0, max_value=3.0, value=1.0, step=0.1,
                                  help="중요도가 높을수록 시간을 더 많이 배정하는 정도")

# -----------------------------
# 본문 - 과목 입력
# -----------------------------
st.title("📅 학습 플래너: 장기 계획 + 하루 시간표")

st.markdown(
    """
**설명**
- 기간(시작~목표), 과목/중요도/시험일을 입력하면 날짜별로 공부시간이 자동 분배됩니다.
- 하루 시작 시각과 집중/휴식 블록을 기반으로 **실제 시간표(타임라인)** 도 생성합니다.
- 과목의 `목표 총 학습시간`을 비워두면 전체 기간/가중치에 따라 자동으로 분배됩니다.
    """
)

st.caption("Tip: 표 우측 상단 + 버튼으로 행을 추가/삭제할 수 있어요. 날짜 셀을 클릭하면 달력이 뜹니다.")

if "subjects_df" not in st.session_state:
    st.session_state["subjects_df"] = _make_empty_subject_df()

colE1, colE2 = st.columns([3, 1])
with colE1:
    edited_df = st.data_editor(
        st.session_state["subjects_df"],
        use_container_width=True,
        column_config={
            "중요도": st.column_config.SelectboxColumn(options=IMPORTANCE_ORDER, required=True),
            "시험일(선택)": st.column_config.DateColumn(step=1),
            "목표 총 학습시간(시간)": st.column_config.NumberColumn(step=1, min_value=0),
        },
        num_rows="dynamic",
        hide_index=True,
        key="subjects_editor",
    )
with colE2:
    st.write("")
    st.write("")
    if st.button("예시 데이터 불러오기", use_container_width=True):
        st.session_state["subjects_df"] = _example_subject_df()
        st.experimental_rerun()

# 업데이트 반영
subjects_df: pd.DataFrame = edited_df.copy()

# 유효성 검사
subjects_df["과목"] = subjects_df["과목"].fillna("").astype(str)
subjects_df = subjects_df[subjects_df["과목"].str.strip() != ""]

if subjects_df.empty:
    st.info("과목을 한 개 이상 입력해 주세요.")
    st.stop()

# 날짜 처리
start_dt = start_date
end_dt = target_date
if start_dt > end_dt:
    st.error("시작일이 목표일보다 늦을 수 없습니다.")
    st.stop()

all_days = daterange(start_dt, end_dt)

# 하루 공부시간: 평일/주말 구분
per_day_hours: Dict[date, float] = {}
for d in all_days:
    if d.weekday() < 5:  # 0=월 ... 4=금
        per_day_hours[d] = float(daily_hours_weekday)
    else:
        per_day_hours[d] = float(daily_hours_weekend)

# -----------------------------
# 가중치 계산 함수
# -----------------------------

def compute_daily_weights(day: date, df: pd.DataFrame) -> Dict[str, float]:
    """주어진 날짜에 대해 과목별 가중치를 계산합니다.
    - 중요도(1~5)
    - 시험 임박도: 시험일까지 남은 일수가 적을수록 가중↑ (urgency_strength)
    - 시험일이 지난 과목은 배정X
    - 시험일이 없으면 완만한 가중
    """
    weights = {}
    for _, row in df.iterrows():
        subj = row["과목"].strip()
        if not subj:
            continue
        imp_label = row.get("중요도", "보통")
        imp_score = IMPORTANCE_MAP.get(str(imp_label), 3)
        exam = row.get("시험일(선택)")
        # 시험일 파싱
        if pd.isna(exam):
            days_to_exam = None
        else:
            exd = pd.to_datetime(exam).date()
            if day > exd:
                # 시험 지난 날에는 배정하지 않음
                continue
            days_to_exam = (exd - day).days

        # 기본 중요도 가중
        w = (imp_score ** (1.0 + importance_strength * 0.25))

        # 임박 가중 (시험이 없는 과목은 완만한 상수 가중 추가)
        if days_to_exam is None:
            w *= 1.0
        else:
            # 남은 일수가 적을수록 커지는 형태 (1 / (days+1))^k
            w *= (1.0 / (days_to_exam + 1.0)) ** max(0.0, urgency_strength)
            # 시험 3일 전 버프(부스팅)
            if days_to_exam <= 3:
                w *= 1.5
        weights[subj] = weights.get(subj, 0.0) + float(w)
    return weights


# -----------------------------
# 총 목표시간(있으면 우선) 대비, 없으면 자동 분배
# -----------------------------
subjects_df["목표 총 학습시간(시간)"] = pd.to_numeric(subjects_df["목표 총 학습시간(시간)"], errors="coerce")

# 전체 가능한 시간 합
total_available_hours = sum(per_day_hours.values())

# 사용자가 일부 과목에 총 목표시간을 명시한 경우 그 시간은 고정으로 두고,
# 나머지 과목은 가중치 기반으로 자동 분배
fixed_hours = subjects_df["목표 총 학습시간(시간)"].fillna(0).sum()
auto_hours_pool = max(0.0, total_available_hours - fixed_hours)

# 날짜별 배분표를 구축
rows = []

for d in all_days:
    day_hours = per_day_hours[d]
    if day_hours <= 0:
        continue

    # 우선, 고정 분량(총 목표시간을 가진 과목들)을 기간 전체에 균등 배분
    fixed_alloc = {}
    for _, row in subjects_df.iterrows():
        subj = row["과목"].strip()
        if not subj:
            continue
        fixed_total = row["목표 총 학습시간(시간)"]
        if pd.notna(fixed_total) and total_available_hours > 0:
            # 전체 기간 시간 대비 비율로 오늘 분량을 산출
            fixed_alloc[subj] = (fixed_total / total_available_hours) * day_hours

    # 자동 배분 대상
    auto_df = subjects_df[pd.isna(subjects_df["목표 총 학습시간(시간)")]]
    auto_weights = compute_daily_weights(d, auto_df)

    auto_alloc = {}
    remain_hours_for_auto = max(0.0, day_hours - sum(fixed_alloc.values()) )
    if auto_weights and remain_hours_for_auto > 0:
        s = sum(auto_weights.values())
        if s > 0:
            for subj, w in auto_weights.items():
                auto_alloc[subj] = remain_hours_for_auto * (w / s)

    # 합치기
    all_subjs = set(list(fixed_alloc.keys()) + list(auto_alloc.keys()))
    for subj in all_subjs:
        rows.append({
            "날짜": d,
            "과목": subj,
            "계획시간(시간)": fixed_alloc.get(subj, 0.0) + auto_alloc.get(subj, 0.0),
        })

plan_df = pd.DataFrame(rows)

if plan_df.empty:
    st.warning("배분할 시간이 없습니다. 평일/주말 공부시간을 확인해 주세요.")
    st.stop()

# 보기 좋게 정렬
plan_df = plan_df.sort_values(["날짜", "과목"]).reset_index(drop=True)

# 집계 요약
summary = plan_df.groupby("과목")["계획시간(시간)"].sum().reset_index().sort_values("계획시간(시간)", ascending=False)

# -----------------------------
# 출력 - 좌: 요약, 우: 일자별 테이블
# -----------------------------
left, right = st.columns([1, 2])
with left:
    st.subheader("📊 과목별 총 배정 시간")
    st.dataframe(summary, use_container_width=True)

    # 파이 차트 (간단)
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.pie(summary["계획시간(시간)"], labels=summary["과목"], autopct="%1.1f%%")
        ax.set_title("배정 비율")
        st.pyplot(fig, use_container_width=True)
    except Exception as e:
        st.caption(f"차트 오류: {e}")

with right:
    st.subheader("🗓️ 날짜별 배분표")
    st.dataframe(plan_df, use_container_width=True, height=420)

# -----------------------------
# 하루 시간표(타임라인) 생성
# -----------------------------

def make_day_timeline(day: date, df: pd.DataFrame, start_t: time,
                      focus_min: int, break_min: int) -> pd.DataFrame:
    day_rows = df[df["날짜"] == day]
    if day_rows.empty:
        return pd.DataFrame(columns=["시작", "끝", "유형", "과목", "비고"])

    # 분 단위로 변환
    subj_minutes = {
        r["과목"]: int(round(float(r["계획시간(시간)"])*60)) for _, r in day_rows.iterrows()
    }
    total_minutes = sum(subj_minutes.values())

    blocks = []
    current_dt = datetime.combine(day, start_t)

    # 각 과목에 대해 focus 블록 단위로 나눔
    # 라운드-로빈 방식으로 과목을 번갈아가며 한 블록씩 할당
    subjects_cycle = list(subj_minutes.keys())
    idx = 0

    while sum(subj_minutes.values()) > 0:
        subj = subjects_cycle[idx % len(subjects_cycle)]
        if subj_minutes[subj] <= 0:
            idx += 1
            # 모든 과목이 0인 경우 종료 방지
            if idx > 100000:
                break
            continue

        this_focus = min(focus_min, subj_minutes[subj])
        start_dt = current_dt
        end_dt = start_dt + timedelta(minutes=this_focus)
        blocks.append({
            "시작": start_dt,
            "끝": end_dt,
            "유형": "공부",
            "과목": subj,
            "비고": f"{this_focus}분 집중"
        })
        current_dt = end_dt
        subj_minutes[subj] -= this_focus

        # 남은 총 분이 0이 아니면 휴식 삽입
        if sum(subj_minutes.values()) > 0 and break_min > 0:
            b_start = current_dt
            b_end = b_start + timedelta(minutes=break_min)
            blocks.append({
                "시작": b_start,
                "끝": b_end,
                "유형": "휴식",
                "과목": "-",
                "비고": f"{break_min}분 휴식"
            })
            current_dt = b_end

        idx += 1

    tl_df = pd.DataFrame(blocks)
    if not tl_df.empty:
        tl_df["시작"] = tl_df["시작"].dt.strftime("%H:%M")
        tl_df["끝"] = tl_df["끝"].dt.strftime("%H:%M")
    return tl_df

# 오늘 타임라인 미리보기 (기간 내일 경우)
now_d = date.today()
preview_day = now_d if (start_dt <= now_d <= end_dt) else start_dt
st.subheader(f"🕒 하루 시간표 (타임라인) — {preview_day.strftime('%Y-%m-%d')}")
preview_tl = make_day_timeline(preview_day, plan_df, start_clock, focus_minutes, break_minutes)
if preview_tl.empty:
    st.info("해당 날짜에는 배정된 공부가 없습니다.")
else:
    st.dataframe(preview_tl, use_container_width=True, height=380)

# -----------------------------
# 다운로드
# -----------------------------

colD1, colD2 = st.columns(2)
with colD1:
    csv = plan_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 날짜별 배분표 CSV 다운로드",
        data=csv,
        file_name="study_plan_daily.csv",
        mime="text/csv",
        use_container_width=True,
    )
with colD2:
    # 하루 시간표도 CSV로 다운로드 (미리보기 날짜 기준)
    tl_csv = preview_tl.to_csv(index=False).encode("utf-8-sig") if not preview_tl.empty else b""
    st.download_button(
        label="📥 하루 시간표 CSV 다운로드",
        data=tl_csv,
        file_name=f"timeline_{preview_day.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=preview_tl.empty,
    )

st.success("✅ 계획 생성 완료! 설정을 바꾸면 표가 즉시 갱신됩니다.")
