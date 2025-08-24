# Streamlit 학습 플래너 (장기 계획 + 하루 시간표 + 시험범위 + 고정일정/이동시간)
# ---------------------------------------------------------------------------------
# 주요 기능
# - 시작~목표 기간 입력, 과목/중요도/시험일/시험범위(텍스트 & 숫자) 입력
# - 중요도 & 시험 임박도 가중치로 날짜별 과목 시간 자동 배분
# - 총 목표시간(있으면 고정), 나머지는 자동분배
# - 모든 시간은 분 단위 내부계산 후 **5분 단위 반올림**, 출력은 "X시간 Y분"
# - 고정 일정(학교/학원 등) + 이동시간(버퍼) 반영하여 **빈 시간대에 공부 배치**
# - 집중/휴식 블록(예: 50/10) 기준으로 실제 타임라인 생성
# - 결과는 **다이어리 카드 스타일**로 예쁘게 렌더링 + CSV 다운로드
# ---------------------------------------------------------------------------------

import math
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="학습 플래너 | 시간표 자동 생성",
    page_icon="📅",
    layout="wide",
)

# ---------------------------------
# 상수/유틸
# ---------------------------------
IMPORTANCE_MAP = {"매우 낮음": 1, "낮음": 2, "보통": 3, "높음": 4, "매우 높음": 5}
IMPORTANCE_ORDER = list(IMPORTANCE_MAP.keys())
WEEKDAYS_LABEL = ["월", "화", "수", "목", "금", "토", "일"]

# 5분 단위 반올림

def round5(minutes: int) -> int:
    return int(round(minutes / 5) * 5)


def format_minutes(minutes: int) -> str:
    """분을 "X시간 Y분" 포맷으로. 5분 단위 반올림 포함."""
    if minutes <= 0:
        return ""
    m = round5(minutes)
    h, mm = divmod(m, 60)
    if h > 0 and mm > 0:
        return f"{h}시간 {mm}분"
    elif h > 0:
        return f"{h}시간"
    else:
        return f"{mm}분"


def to_datetime(d: date, t: time) -> datetime:
    return datetime.combine(d, t)


# 시험 범위 파서

def parse_range_text(text: str) -> List[str]:
    """간단한 범위 텍스트 파서.
    지원 예: "1~5단원", "1-5", "Lesson 1~3", "1,3,4", "A,B,C" 등.
    숫자 범위면 각 번호에 접미사(단원/Lesson)를 유지, 텍스트 콤마면 그대로 분할.
    """
    if not isinstance(text, str) or not text.strip():
        return []
    s = text.strip()
    # 구분자 통일
    s = s.replace("–", "-").replace("—", "-")
    # 단원/Lesson 같은 접미사/접두어 추출 시도
    import re
    # 패턴: (prefix)(start)(~ or -)(end)(suffix)
    m = re.search(r"^(?P<prefix>[^0-9]*?)\s*(?P<start>\d+)\s*[~-]\s*(?P<end>\d+)\s*(?P<suffix>[^0-9]*)$", s)
    if m:
        prefix = m.group("prefix") or ""
        start = int(m.group("start"))
        end = int(m.group("end"))
        suffix = m.group("suffix") or ""
        if start > end:
            start, end = end, start
        items = []
        for n in range(start, end + 1):
            label = f"{prefix}{n}{suffix}".strip()
            items.append(label)
        return items
    # 콤마 분할
    parts = [p.strip() for p in re.split(r"[,/]|\s{2,}", s) if p.strip()]
    return parts


# 빈 데이터프레임 생성
@st.cache_data(show_spinner=False)
def _make_empty_subject_df() -> pd.DataFrame:
    return pd.DataFrame({
        "과목": [""],
        "중요도": ["보통"],
        "목표 총 학습시간(시간)": [np.nan],  # 비우면 자동
        "시험일(선택)": [pd.NaT],
        "시험범위(텍스트)": [""],
        "범위_시작(숫자)": [np.nan],
        "범위_끝(숫자)": [np.nan],
    })

@st.cache_data(show_spinner=False)
def _example_subject_df() -> pd.DataFrame:
    today = date.today()
    return pd.DataFrame({
        "과목": ["국어", "수학", "영어", "사회"],
        "중요도": ["보통", "매우 높음", "높음", "낮음"],
        "목표 총 학습시간(시간)": [np.nan, 20, np.nan, 6],
        "시험일(선택)": [pd.to_datetime(today + timedelta(days=7)),
                     pd.to_datetime(today + timedelta(days=10)),
                     pd.to_datetime(today + timedelta(days=14)),
                     pd.NaT],
        "시험범위(텍스트)": ["지문 1~5", "1~5단원", "Lesson 1~3", "-"],
        "범위_시작(숫자)": [np.nan, 1, 1, np.nan],
        "범위_끝(숫자)": [np.nan, 5, 3, np.nan],
    })


def daterange(start: date, end: date) -> List[date]:
    d = start
    out = []
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


# ---------------------------------
# 사이드바 입력
# ---------------------------------
with st.sidebar:
    st.header("⚙️ 기본 설정")
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("시작일", value=date.today())
    with c2:
        target_date = st.date_input("목표일", value=date.today() + timedelta(days=14), min_value=start_date)

    st.subheader("⏰ 하루 시간대")
    day_start = st.time_input("일과 시작", value=time(6, 0))
    day_end = st.time_input("일과 종료", value=time(23, 0))

    st.subheader("📈 하루 공부 최대치(캡)")
    cc1, cc2 = st.columns(2)
    with cc1:
        daily_hours_weekday = st.number_input("평일 최대(시간)", min_value=0.0, max_value=24.0, value=4.0, step=0.5)
    with cc2:
        daily_hours_weekend = st.number_input("주말 최대(시간)", min_value=0.0, max_value=24.0, value=6.0, step=0.5)

    st.subheader("🍅 집중/휴식 블록")
    b1, b2 = st.columns(2)
    with b1:
        focus_minutes = int(st.number_input("공부 블록(분)", min_value=20, max_value=180, value=50, step=5))
    with b2:
        break_minutes = int(st.number_input("휴식(분)", min_value=0, max_value=60, value=10, step=5))

    st.subheader("⚖️ 배분 가중치")
    urgency_strength = st.slider("시험 임박 가중치", 0.0, 3.0, 1.2, 0.1)
    importance_strength = st.slider("중요도 가중치", 0.0, 3.0, 1.0, 0.1)

# ---------------------------------
# 본문 UI
# ---------------------------------
st.title("📅 맞춤 학습 다이어리")

st.markdown(
    """
**설명**
- 과목/중요도/시험일과 **시험범위(텍스트 또는 시작/끝 숫자)**를 입력하세요.
- 고정 일정(학교/학원/약속 등)과 **이동시간(버퍼)**을 입력하면 빈 시간에 공부가 배치됩니다.
- 모든 시간은 **5분 단위**로 반올림되어 표시됩니다.
    """
)

# 과목 표
if "subjects_df" not in st.session_state:
    st.session_state["subjects_df"] = _make_empty_subject_df()

colA, colB = st.columns([3, 1])
with colA:
    subjects_df = st.data_editor(
        st.session_state["subjects_df"],
        use_container_width=True,
        column_config={
            "중요도": st.column_config.SelectboxColumn(options=IMPORTANCE_ORDER, required=True),
            "시험일(선택)": st.column_config.DateColumn(step=1),
            "목표 총 학습시간(시간)": st.column_config.NumberColumn(step=1, min_value=0),
            "범위_시작(숫자)": st.column_config.NumberColumn(step=1, min_value=1),
            "범위_끝(숫자)": st.column_config.NumberColumn(step=1, min_value=1),
        },
        num_rows="dynamic",
        hide_index=True,
        key="subjects_editor",
    )
with colB:
    if st.button("예시 과목 불러오기", use_container_width=True):
        st.session_state["subjects_df"] = _example_subject_df()
        st.experimental_rerun()

# 고정 일정 입력
st.subheader("📌 고정 일정 + 이동시간")
st.caption("예: 학교 09:00~15:00 (월~금), 학원 18:00~20:00 (화/목), 각 일정 전후 이동 10분")

num_events = st.number_input("반복 일정 개수", min_value=0, max_value=10, value=1, step=1)
recurring_events: List[Dict] = []
for i in range(int(num_events)):
    with st.expander(f"반복 일정 {i+1}", expanded=(i == 0)):
        col1, col2 = st.columns([2, 1])
        with col1:
            title = st.text_input(f"이름 {i+1}", value="학교" if i == 0 else "")
        with col2:
            buffer_min = int(st.number_input(f"이동/버퍼(분) {i+1}", min_value=0, max_value=120, value=10, step=5))
        c3, c4, c5 = st.columns(3)
        with c3:
            ev_start = st.time_input(f"시작 {i+1}", value=time(9, 0))
        with c4:
            ev_end = st.time_input(f"종료 {i+1}", value=time(15, 0))
        with c5:
            weekdays = st.multiselect(
                f"요일 {i+1}", WEEKDAYS_LABEL, default=["월", "화", "수", "목", "금"] if i == 0 else []
            )
        recurring_events.append({
            "title": title,
            "start": ev_start,
            "end": ev_end,
            "buffer": buffer_min,
            "weekdays": weekdays,
        })

# 유효성 및 전처리
subjects_df = subjects_df.copy()
subjects_df["과목"] = subjects_df["과목"].fillna("").astype(str).str.strip()
subjects_df = subjects_df[subjects_df["과목"] != ""]
if subjects_df.empty:
    st.info("과목을 한 개 이상 입력해 주세요.")
    st.stop()

start_dt = start_date
end_dt = target_date
if start_dt > end_dt:
    st.error("시작일이 목표일보다 늦을 수 없습니다.")
    st.stop()

all_days = daterange(start_dt, end_dt)

# 하루 최대 공부 분(캡)
per_day_cap_min: Dict[date, int] = {}
for d in all_days:
    cap_h = daily_hours_weekday if d.weekday() < 5 else daily_hours_weekend
    per_day_cap_min[d] = int(round(cap_h * 60))

# 고정 일정 → 하루의 사용 불가 구간 생성
weekday_to_idx = {label: i for i, label in enumerate(WEEKDAYS_LABEL)}


def build_busy_intervals_for_day(d: date) -> List[Tuple[datetime, datetime]]:
    busy = []
    for ev in recurring_events:
        if not ev.get("weekdays"):
            continue
        wd_labels = ev["weekdays"]
        if WEEKDAYS_LABEL[d.weekday()] not in wd_labels:
            continue
        start_dt = to_datetime(d, ev["start"]) - timedelta(minutes=ev.get("buffer", 0))
        end_dt = to_datetime(d, ev["end"]) + timedelta(minutes=ev.get("buffer", 0))
        if end_dt > start_dt:
            busy.append((start_dt, end_dt))
    # 일과 범위를 넘어서는 것은 자르기
    day_s = to_datetime(d, day_start)
    day_e = to_datetime(d, day_end)
    clipped = []
    for s, e in busy:
        s2 = max(s, day_s)
        e2 = min(e, day_e)
        if e2 > s2:
            clipped.append((s2, e2))
    # 병합
    if not clipped:
        return []
    clipped.sort()
    merged = [clipped[0]]
    for s, e in clipped[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))
    return merged


def invert_busy_to_free(d: date, busy: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    day_s = to_datetime(d, day_start)
    day_e = to_datetime(d, day_end)
    free = []
    cur = day_s
    for s, e in busy:
        if s > cur:
            free.append((cur, s))
        cur = max(cur, e)
    if cur < day_e:
        free.append((cur, day_e))
    return free

# 가중치 계산 (자동 배분용)

def compute_daily_weights(day: date, df: pd.DataFrame) -> Dict[str, float]:
    weights = {}
    for _, row in df.iterrows():
        subj = row["과목"].strip()
        if not subj:
            continue
        imp_label = row.get("중요도", "보통")
        imp_score = IMPORTANCE_MAP.get(str(imp_label), 3)
        exam = row.get("시험일(선택)")
        if pd.isna(exam):
            days_to_exam = None
        else:
            exd = pd.to_datetime(exam).date()
            if day > exd:
                # 시험 지나면 배정 X
                continue
            days_to_exam = (exd - day).days
        w = (imp_score ** (1.0 + importance_strength * 0.25))
        if days_to_exam is None:
            w *= 1.0
        else:
            w *= (1.0 / (days_to_exam + 1.0)) ** max(0.0, urgency_strength)
            if days_to_exam <= 3:
                w *= 1.5
        weights[subj] = weights.get(subj, 0.0) + float(w)
    return weights

# 과목별 범위 목록 만들기

def build_ranges_for_subject(row: pd.Series) -> List[str]:
    items = []
    # 숫자 시작/끝 우선
    try:
        s = int(row.get("범위_시작(숫자)") or 0)
        e = int(row.get("범위_끝(숫자)") or 0)
    except Exception:
        s, e = 0, 0
    if s > 0 and e > 0:
        if s > e:
            s, e = e, s
        # 접미사 추정: 텍스트 범위에서 단원/lesson 단어 추출 시도
        suffix = "단원" if "단원" in str(row.get("시험범위(텍스트)") or "") else ""
        items = [f"{n}{suffix}".strip() for n in range(s, e + 1)]
    else:
        txt = str(row.get("시험범위(텍스트)") or "").strip()
        items = parse_range_text(txt) if txt else []
    # 비어있으면 기본 한 덩어리
    return items or ["전 범위"]

# 총 가능한 공부 분(캡 기준) 합
cap_total_min = sum(per_day_cap_min.values())

# 사용자 고정 총 목표시간(분)
subjects_df["목표 총 학습시간(시간)"] = pd.to_numeric(subjects_df["목표 총 학습시간(시간)"], errors="coerce")
fixed_total_min = int(round((subjects_df["목표 총 학습시간(시간)"].fillna(0).sum()) * 60))
auto_pool_min = max(0, cap_total_min - fixed_total_min)

# 날짜별 과목 분배(분)
rows_daily = []
for d in all_days:
    cap_min = per_day_cap_min[d]
    if cap_min <= 0:
        continue
    # 하루 고정분(총 목표시간이 있는 과목) 균등 배분
    fixed_alloc: Dict[str, int] = {}
    for _, row in subjects_df.iterrows():
        subj = row["과목"].strip()
        fix_h = row.get("목표 총 학습시간(시간)")
        if pd.notna(fix_h) and cap_total_min > 0:
            share = (float(fix_h) * 60.0) * (cap_min / cap_total_min)
            fixed_alloc[subj] = fixed_alloc.get(subj, 0) + round5(int(round(share)))
    # 자동 배분
    auto_df = subjects_df[pd.isna(subjects_df["목표 총 학습시간(시간)")]]
    auto_weights = compute_daily_weights(d, auto_df)
    auto_alloc: Dict[str, int] = {}
    remain = max(0, cap_min - sum(fixed_alloc.values()))
    if auto_weights and remain > 0:
        s = sum(auto_weights.values())
        if s > 0:
            for subj, w in auto_weights.items():
                auto_alloc[subj] = round5(int(round(remain * (w / s))))
    # 합치고 5분 단위 스냅
    all_subj = set(list(fixed_alloc.keys()) + list(auto_alloc.keys()))
    for subj in all_subj:
        minutes = fixed_alloc.get(subj, 0) + auto_alloc.get(subj, 0)
        minutes = round5(minutes)
        if minutes > 0:
            rows_daily.append({"날짜": d, "과목": subj, "분": minutes})

plan_minutes_df = pd.DataFrame(rows_daily)
if plan_minutes_df.empty:
    st.warning("배분할 시간이 없습니다. 평일/주말 최대 공부시간 또는 과목 설정을 확인해 주세요.")
    st.stop()

# 과목별 전체 분
subject_total = plan_minutes_df.groupby("과목")["분"].sum().reset_index().sort_values("분", ascending=False)

# 과목별 범위 목록 및 범위 당 목표 분(총/개수)
subject_ranges: Dict[str, List[str]] = {}
subject_range_target_min: Dict[str, int] = {}
for _, row in subjects_df.iterrows():
    subj = row["과목"].strip()
    ranges = build_ranges_for_subject(row)
    subject_ranges[subj] = ranges
    total_min = int(plan_minutes_df[plan_minutes_df["과목"] == subj]["분"].sum())
    n = max(1, len(ranges))
    subject_range_target_min[subj] = max(5, round5(int(math.ceil(total_min / n))))

# 일자별 과목 분을 범위 단위로 세분화 (누적 진척 반영)
progress_used_min: Dict[Tuple[str, str], int] = {}  # (과목, 범위) -> 누적분
rows_scoped = []
for d in all_days:
    day_rows = plan_minutes_df[plan_minutes_df["날짜"] == d]
    for _, r in day_rows.iterrows():
        subj = r["과목"]
        remain = int(r["분"])
        ranges = subject_ranges.get(subj, ["전 범위"]) or ["전 범위"]
        target_each = subject_range_target_min.get(subj, max(5, round5(remain)))
        # 순차 할당
        idx = 0
        # 현재 진행 중인 범위부터 시작
        # 진행 중 범위 찾기
        for i, rg in enumerate(ranges):
            used = progress_used_min.get((subj, rg), 0)
            if used < target_each:
                idx = i
                break
        while remain > 0 and idx < len(ranges):
            rg = ranges[idx]
            used = progress_used_min.get((subj, rg), 0)
            need = max(0, target_each - used)
            if need <= 0:
                idx += 1
                continue
            take = min(need, remain)
            take = round5(take)
            if take <= 0:
                # 강제로 5분 스냅
                take = min(remain, 5)
                take = round5(take)
            if take <= 0:
                break
            rows_scoped.append({"날짜": d, "과목": subj, "범위": rg, "분": int(take)})
            progress_used_min[(subj, rg)] = used + int(take)
            remain -= int(take)
            if progress_used_min[(subj, rg)] >= target_each:
                idx += 1

plan_scoped_df = pd.DataFrame(rows_scoped)

# -----------------------------
# 타임라인(하루) 만들기: 고정 일정 제외 후 공부 블록 배치
# -----------------------------

def make_day_timeline(d: date, scoped_df: pd.DataFrame) -> pd.DataFrame:
    # 자유 시간대 계산
    busy = build_busy_intervals_for_day(d)
    free = invert_busy_to_free(d, busy)
    blocks = []
    # 먼저 고정 일정부터 카드로 출력하기 위해 저장
    for s, e in busy:
        blocks.append({
            "시작": s, "끝": e, "유형": "고정", "제목": "고정 일정", "과목": "-", "범위": "-"
        })

    # 해당 날짜 공부 항목
    day_items = scoped_df[scoped_df["날짜"] == d]
    # 각 항목을 focus/break 블록으로 쪼개서 free 구간에 채우기
    # free는 시간 순으로 배치
    free_idx = 0
    for _, row in day_items.iterrows():
        subj = row["과목"]
        rg = row["범위"]
        remain = int(row["분"])  # 이미 5분 단위
        while remain > 0 and free_idx < len(free):
            f_s, f_e = free[free_idx]
            cur = f_s
            while cur < f_e and remain > 0:
                # 한 focus 블록
                focus = min(focus_minutes, remain, int((f_e - cur).total_seconds() // 60))
                focus = round5(focus)
                if focus <= 0:
                    break
                s = cur
                e = s + timedelta(minutes=focus)
                blocks.append({
                    "시작": s, "끝": e, "유형": "공부", "제목": subj, "과목": subj, "범위": rg
                })
                cur = e
                remain -= focus
                # 휴식
                if remain > 0:
                    br = min(break_minutes, int((f_e - cur).total_seconds() // 60))
                    br = round5(br)
                    if br > 0:
                        blocks.append({
                            "시작": cur, "끝": cur + timedelta(minutes=br), "유형": "휴식", "제목": "휴식",
                            "과목": "-", "범위": "-"
                        })
                        cur = cur + timedelta(minutes=br)
            if cur >= f_e or int((f_e - cur).total_seconds() // 60) <= 0:
                free_idx += 1
            else:
                # 아직 free 안 끝났지만 이 항목이 끝남 → 다음 항목 이어서 같은 free에 배치
                free[free_idx] = (cur, f_e)
        # free를 다 써서 remain 남으면 그냥 다음 날짜로 이월은 하지 않음 (캡에 의해 제한)
    # 정렬 및 문자열 포맷
    if not blocks:
        return pd.DataFrame(columns=["시작", "끝", "유형", "제목", "과목", "범위", "소요"])
    blocks.sort(key=lambda x: x["시작"])
    out = []
    for b in blocks:
        dur = int(((b["끝"] - b["시작"]).total_seconds()) // 60)
        out.append({
            "시작": b["시작"].strftime("%H:%M"),
            "끝": b["끝"].strftime("%H:%M"),
            "유형": b["유형"],
            "제목": b["제목"],
            "과목": b["과목"],
            "범위": b["범위"],
            "소요": format_minutes(dur),
        })
    return pd.DataFrame(out)

# ---------------------------------
# 출력: 다이어리 카드 스타일
# ---------------------------------

def render_day_card(d: date, timeline_df: pd.DataFrame):
    # 간단한 색상 규칙
    bg = "#FFF8E7" if d.weekday() >= 5 else "#F6F9FF"
    border = "#F0D9B5" if d.weekday() >= 5 else "#C9D7FF"
    day_label = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
    st.markdown(
        f"""
        <div style="background:{bg}; border:2px solid {border}; border-radius:18px; padding:16px; margin-bottom:16px; box-shadow:0 2px 8px rgba(0,0,0,.06)">
          <div style="font-size:18px; font-weight:700; margin-bottom:8px;">📅 {d.strftime('%Y-%m-%d')} ({day_label})</div>
        """,
        unsafe_allow_html=True,
    )
    if timeline_df.empty:
        st.markdown("<div style='padding:8px;'>계획 없음</div>", unsafe_allow_html=True)
    else:
        for _, b in timeline_df.iterrows():
            icon = "🏫" if b["유형"] == "고정" else ("🧠" if b["유형"] == "공부" else "🌿")
            title = b["제목"] if b["유형"] != "공부" else f"{b['과목']} · {b['범위']}"
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:12px; background:white; margin:6px 0; border:1px solid #eee;">
                    <div style="font-size:20px; width:28px; text-align:center;">{icon}</div>
                    <div style="flex:1;">
                        <div style="font-weight:600;">{title}</div>
                        <div style="font-size:13px; color:#555;">{b['시작']} ~ {b['끝']} · {b['소요']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

# 좌: 요약 / 우: 다이어리
left, right = st.columns([1, 2])
with left:
    st.subheader("📊 과목별 총 배정 (분)")
    tmp = subject_total.copy()
    tmp["시간"] = tmp["분"].apply(format_minutes)
    st.dataframe(tmp.rename(columns={"분": "총 분", "시간": "총 시간표시"}), use_container_width=True)

with right:
    st.subheader("🗓️ 계획표 (다이어리)")
    # 오늘이 기간 내면 오늘부터 7일, 아니면 시작일부터 7일 미리보기
    start_view = date.today() if (start_dt <= date.today() <= end_dt) else start_dt
    view_days = [d for d in all_days if d >= start_view][:7] or all_days[:7]
    for d in view_days:
        tl = make_day_timeline(d, plan_scoped_df)
        render_day_card(d, tl)

# -----------------------------
# 다운로드 (일자별 과목/범위/분, 그리고 특정일 타임라인)
# -----------------------------
st.subheader("📥 다운로드")
plan_csv = plan_scoped_df.copy()
plan_csv["분 포맷"] = plan_csv["분"].apply(format_minutes)
csv_bytes = plan_csv.to_csv(index=False).encode("utf-8-sig")
st.download_button("📄 세부 계획 CSV (과목·범위·분)", data=csv_bytes, file_name="study_plan_scoped.csv", mime="text/csv")

# 타임라인은 미리보기 첫 날 기준으로 저장
preview_day = view_days[0]
preview_tl_df = make_day_timeline(preview_day, plan_scoped_df)
tl_bytes = preview_tl_df.to_csv(index=False).encode("utf-8-sig") if not preview_tl_df.empty else b""
st.download_button(
    f"🕒 타임라인 CSV ({preview_day.strftime('%Y%m%d')})",
    data=tl_bytes,
    file_name=f"timeline_{preview_day.strftime('%Y%m%d')}.csv",
    mime="text/csv",
    disabled=preview_tl_df.empty,
)

st.success("✅ 계획 생성 완료! 설정을 바꾸면 즉시 갱신됩니다.")
