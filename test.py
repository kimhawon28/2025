# 📅 Streamlit 학습 다이어리 플래너 (달력/다이어리 스타일)
# ------------------------------------------------------------
# 요구사항 전부 반영:
# - 과목/중요도/시험일/시험범위 입력(텍스트 또는 숫자 시작~끝)
# - 시작~목표 기간에 맞춰 자동 배분 (가중치: 중요도, 임박도)
# - 하루 시간대(시작/종료) + 반복 고정 일정(학교/학원 등) + 이동(버퍼) 반영
# - 빈 시간대에 공부 블록 배치 (집중/휴식 블록 적용)
# - 모든 시간은 5분 단위 반올림, 출력은 "1시간 20분" 형식
# - 출력은 **다이어리/달력 스타일 라인** (예시 형식과 동일)
# - KeyError 등 오류 없는 안전한 분기 처리
# ------------------------------------------------------------

from __future__ import annotations
import math
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Tuple, Optional

import numpy as np
import pandas as pd
import streamlit as st

import os
import requests
from io import BytesIO
from fpdf import FPDF

from datetime import datetime, date, time, timedelta

# -------------------------
# Utility: 문자열/숫자/시간 -> datetime 변환
# -------------------------
def to_dt(d: date, hm_str):
    """주어진 날짜 d(date)와 'HH:MM' 문자열/시간 객체/숫자를 datetime으로 변환"""
    if isinstance(hm_str, str):
        return datetime.combine(d, datetime.strptime(hm_str, "%H:%M").time())
    elif isinstance(hm_str, datetime):
        return hm_str
    elif hasattr(hm_str, "hour"):  # time 객체 같은 것
        return datetime.combine(d, hm_str)
    elif isinstance(hm_str, (int, float)):  # 분 단위 숫자일 때
        h, m = divmod(int(hm_str), 60)
        return datetime.combine(d, time(hour=h, minute=m))
    else:
        raise ValueError(f"지원하지 않는 시간 형식: {hm_str} (type={type(hm_str)})")

def fmt_hm(minutes: int) -> str:
    """분(minute) 단위를 'HH:MM' 문자열로 변환"""
    if pd.isna(minutes):
        return ""
    try:
        minutes = int(minutes)
        h, m = divmod(minutes, 60)
        return f"{h:02d}:{m:02d}"
    except Exception as e:
        return str(minutes)  # 혹시 숫자가 아닌 값이 들어오면 그대로 반환

# -------------------------
# Example: 하루의 바쁜 구간 계산
# -------------------------
def build_busy_intervals_for_day(d: date):
    day_start = "08:00"
    day_end = "22:00"
    # ✅ 여기서 to_dt 호출
    day_s, day_e = to_dt(d, day_start), to_dt(d, day_end)
    return [(day_s, day_e)], []  # (예시로 전체 구간 바쁨 처리)


# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="📅 학습 다이어리 플래너", page_icon="📅", layout="wide")

WEEK_LABEL = ["월", "화", "수", "목", "금", "토", "일"]
IMPORTANCE_MAP = {"매우 낮음":1, "낮음":2, "보통":3, "높음":4, "매우 높음":5}
IMPORTANCE_ORDER = list(IMPORTANCE_MAP.keys())

# -----------------------------
# 유틸
# -----------------------------

def round5(m: int) -> int:
    return int(round(m/5)*5)


def fmt_hm(x):
    """분(int)을 HH:MM 문자열로 변환"""
    if pd.isna(x):
        return ""
    try:
        minutes = int(x)
        hours, mins = divmod(minutes, 60)
        return f"{hours:02d}:{mins:02d}"
    except Exception:
        return str(x)

# 시험 범위 파서 (텍스트/숫자 범위 모두 지원)
import re

def parse_range_text(text: str) -> List[str]:
    if not isinstance(text, str):
        return []
    s = text.strip()
    if not s:
        return []
    s = s.replace("–", "-").replace("—", "-").replace(" ", "")
    # 패턴: (prefix)(start)(~ or -)(end)(suffix)
    m = re.search(r"^(?P<prefix>[^0-9]*?)(?P<start>\d+)\s*[~-]\s*(?P<end>\d+)(?P<suffix>[^0-9]*)$", s)
    if m:
        prefix = m.group("prefix") or ""
        start = int(m.group("start"))
        end = int(m.group("end"))
        if start > end:
            start, end = end, start
        suffix = m.group("suffix") or ""
        return [f"{prefix}{i}{suffix}".strip() for i in range(start, end+1)]
    # 콤마 분리
    parts = [p for p in re.split(r"[,/]", s) if p]
    return parts or []
def fmt_hm(minutes: int):
    """분 -> '1시간 20분' 같은 문자열 변환"""
    h, m = divmod(minutes, 60)
    if h and m:
        return f"{h}시간 {m}분"
    elif h:
        return f"{h}시간"
    else:
        return f"{m}분"

WEEK_LABEL = ["월", "화", "수", "목", "금", "토", "일"]

def ensure_font():
    """NotoSansKR-Regular.otf 없으면 자동 다운로드"""
    font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansKR-Regular.otf"
    font_path = "NotoSansKR-Regular.otf"
    if not os.path.exists(font_path):
        print("👉 NotoSansKR-Regular.otf 다운로드 중...")
        r = requests.get(font_url)
        with open(font_path, "wb") as f:
            f.write(r.content)
    return font_path


# -----------------------------
# 사이드바 입력
# -----------------------------
with st.sidebar:
    st.header("⚙️ 기본 설정")
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("시작일", value=date.today())
    with c2:
        target_date = st.date_input("목표일", value=date.today() + timedelta(days=14), min_value=start_date)

    st.subheader("⏰ 하루 범위")
    d1, d2 = st.columns(2)
    with d1:
        day_start = st.time_input("일과 시작", value=time(6,0))
    with d2:
        day_end = st.time_input("일과 종료", value=time(23,0))

    st.subheader("🍅 집중/휴식")
    b1, b2 = st.columns(2)
    with b1:
        focus_min = int(st.number_input("공부 블록(분)", min_value=20, max_value=180, value=50, step=5))
    with b2:
        break_min = int(st.number_input("휴식(분)", min_value=0, max_value=60, value=10, step=5))

    st.subheader("📈 공부 상한(캡)")
    h1, h2 = st.columns(2)
    with h1:
        weekday_cap_h = st.number_input("평일 최대(시간)", min_value=0.0, max_value=24.0, value=4.0, step=0.5)
    with h2:
        weekend_cap_h = st.number_input("주말 최대(시간)", min_value=0.0, max_value=24.0, value=6.0, step=0.5)

    st.subheader("🎯 시험일 옵션")
    review_on_exam_min = int(st.number_input("시험 당일 복습(분)", min_value=0, max_value=240, value=45, step=5))

    st.subheader("⚖️ 가중치")
    urgency_strength = st.slider("임박 가중치", 0.0, 3.0, 1.2, 0.1)
    importance_strength = st.slider("중요도 가중치", 0.0, 3.0, 1.0, 0.1)

# -----------------------------
# 본문: 과목/범위 테이블
# -----------------------------
st.title("📅 학습 다이어리 플래너")

@st.cache_data(show_spinner=False)
def empty_subject_df() -> pd.DataFrame:
    return pd.DataFrame({
        "과목":[""],
        "중요도":["보통"],
        "목표 총 학습시간(시간)": [np.nan],
        "시험일(선택)": [pd.NaT],
        "시험범위(텍스트)": [""],
        "범위_시작(숫자)": [np.nan],
        "범위_끝(숫자)": [np.nan],
    })

@st.cache_data(show_spinner=False)
def example_subject_df() -> pd.DataFrame:
    today = date.today()
    return pd.DataFrame({
        "과목":["국어","수학","영어","사회"],
        "중요도":["보통","매우 높음","높음","낮음"],
        "목표 총 학습시간(시간)": [np.nan, 20, np.nan, 6],
        "시험일(선택)": [pd.to_datetime(today+timedelta(days=7)), pd.to_datetime(today+timedelta(days=10)), pd.to_datetime(today+timedelta(days=14)), pd.NaT],
        "시험범위(텍스트)": ["지문1~5","1~5단원","Lesson1~3","-"],
        "범위_시작(숫자)": [np.nan,1,1,np.nan],
        "범위_끝(숫자)": [np.nan,5,3,np.nan],
    })

if "subjects_df" not in st.session_state:
    st.session_state["subjects_df"] = empty_subject_df()

colA, colB = st.columns([3,1])
with colA:
    subjects_df = st.data_editor(
        st.session_state["subjects_df"],
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "중요도": st.column_config.SelectboxColumn(options=IMPORTANCE_ORDER, required=True),
            "시험일(선택)": st.column_config.DateColumn(step=1),
            "목표 총 학습시간(시간)": st.column_config.NumberColumn(step=1, min_value=0),
            "범위_시작(숫자)": st.column_config.NumberColumn(step=1, min_value=1),
            "범위_끝(숫자)": st.column_config.NumberColumn(step=1, min_value=1),
        },
        key="subjects_editor",
    )
with colB:
    if st.button("예시 과목 불러오기", use_container_width=True):
        st.session_state["subjects_df"] = example_subject_df()
        st.rerun()

# 전처리/유효성
subjects_df = subjects_df.copy()
subjects_df["과목"] = subjects_df["과목"].fillna("").astype(str).str.strip()
subjects_df = subjects_df[subjects_df["과목"] != ""]
if subjects_df.empty:
    st.info("과목을 한 개 이상 입력해 주세요.")
    st.stop()

start_dt, end_dt = start_date, target_date
if start_dt > end_dt:
    st.error("시작일이 목표일보다 늦을 수 없습니다.")
    st.stop()

# 기간 날짜 목록
all_days: List[date] = []
cur = start_dt
while cur <= end_dt:
    all_days.append(cur)
    cur += timedelta(days=1)

# 하루 공부 상한(분)
per_day_cap: Dict[date, int] = {}
for d in all_days:
    cap_h = weekday_cap_h if d.weekday() < 5 else weekend_cap_h
    per_day_cap[d] = int(round(cap_h*60))

# -----------------------------
# 고정 일정 (반복) 입력
# -----------------------------
st.subheader("🏫 반복 고정 일정 + 이동(버퍼)")
st.caption("예: 학교 09:00~15:00 (월~금), 학원 18:00~20:00 (화/목), 버퍼 10분")
num_events = st.number_input("반복 일정 개수", min_value=0, max_value=10, value=1, step=1)
recurring_events: List[Dict] = []
for i in range(int(num_events)):
    with st.expander(f"반복 일정 {i+1}", expanded=(i==0)):
        t1, t2 = st.columns([2,1])
        with t1:
            title = st.text_input(f"이름 {i+1}", value=("학교" if i==0 else ""))
        with t2:
            buffer_min = int(st.number_input(f"이동/버퍼(분) {i+1}", min_value=0, max_value=120, value=10, step=5))
        c3, c4, c5 = st.columns(3)
        with c3:
            ev_start = st.time_input(f"시작 {i+1}", value=time(9,0))
        with c4:
            ev_end = st.time_input(f"종료 {i+1}", value=time(15,0))
        with c5:
            weekdays = st.multiselect(f"요일 {i+1}", WEEK_LABEL, default=["월","화","수","목","금"] if i==0 else [])
        recurring_events.append({"title":title, "start":ev_start, "end":ev_end, "buffer":buffer_min, "weekdays":weekdays})

# -----------------------------
# 바쁜 구간/자유 구간 계산
# -----------------------------

def build_busy_intervals_for_day(d: date) -> Tuple[List[Tuple[datetime,datetime]], List[Dict]]:
    """하루 바쁜 구간과, 다이어리 출력용 이벤트 라인 목록 반환"""
    day_s, day_e = to_dt(d, day_start), to_dt(d, day_end)
    busy: List[Tuple[datetime,datetime]] = []
    event_lines: List[Dict] = []
    for ev in recurring_events:
        if WEEK_LABEL[d.weekday()] not in (ev.get("weekdays") or []):
            continue
        ev_s = to_dt(d, ev["start"]) ; ev_e = to_dt(d, ev["end"]) ; buf = int(ev.get("buffer",0))
        # 클리핑
        if ev_e <= day_s or ev_s >= day_e:
            continue
        ev_s = max(ev_s, day_s)
        ev_e = min(ev_e, day_e)
        # 바쁜구간(버퍼 포함)
        bs = max(day_s, ev_s - timedelta(minutes=buf))
        be = min(day_e, ev_e + timedelta(minutes=buf))
        if be > bs:
            busy.append((bs, be))
        # 출력용 원 이벤트 시각 & 이동(사후)
        event_lines.append({"type":"event","title":ev.get("title") or "일정","start":ev_s,"end":ev_e,"buffer":buf})
        if buf>0:
            mv_s = ev_e ; mv_e = min(day_e, ev_e + timedelta(minutes=buf))
            if mv_e > mv_s:
                event_lines.append({"type":"move","title":"이동","start":mv_s,"end":mv_e})
    # 병합
    busy.sort()
    merged: List[Tuple[datetime,datetime]] = []
    for s,e in busy:
        if not merged:
            merged.append((s,e))
        else:
            ls, le = merged[-1]
            if s <= le:
                merged[-1] = (ls, max(le, e))
            else:
                merged.append((s,e))
    return merged, event_lines


def invert_busy_to_free(d: date, busy: List[Tuple[datetime,datetime]]) -> List[Tuple[datetime,datetime]]:
    day_s, day_e = to_dt(d, day_start), to_dt(d, day_end)
    if not busy:
        return [(day_s, day_e)] if day_e>day_s else []
    free: List[Tuple[datetime,datetime]] = []
    cur = day_s
    for s,e in busy:
        if s>cur:
            free.append((cur, s))
        cur = max(cur, e)
    if cur<day_e:
        free.append((cur, day_e))
    return free

# -----------------------------
# 가중치/분배
# -----------------------------

def compute_daily_weights(d: date, df: pd.DataFrame) -> Dict[str,float]:
    w: Dict[str,float] = {}
    for _, row in df.iterrows():
        subj = str(row["과목"]).strip()
        if not subj: continue
        imp = IMPORTANCE_MAP.get(str(row.get("중요도","보통")), 3)
        exam = row.get("시험일(선택)")
        if pd.isna(exam):
            days_to = None
        else:
            exd = pd.to_datetime(exam).date()
            if d > exd:
                continue
            days_to = (exd - d).days
        # 중요도
        val = (imp ** (1.0 + 0.25*importance_strength))
        # 임박도
        if days_to is not None:
            val *= (1.0/(days_to+1.0)) ** max(0.0, urgency_strength)
            if days_to <= 3:
                val *= 1.5
        w[subj] = w.get(subj,0.0)+float(val)
    return w

# 과목별 범위 리스트 만들기

def build_ranges_for_subject(row: pd.Series) -> List[str]:
    ranges: List[str] = []
    try:
        s = int(row.get("범위_시작(숫자)") or 0)
        e = int(row.get("범위_끝(숫자)") or 0)
    except Exception:
        s, e = 0, 0
    if s>0 and e>0:
        if s>e: s,e = e,s
        suffix_guess = "단원" if "단원" in str(row.get("시험범위(텍스트)") or "") else ""
        ranges = [f"{i}{suffix_guess}".strip() for i in range(s,e+1)]
    else:
        txt = str(row.get("시험범위(텍스트)") or "").strip()
        ranges = parse_range_text(txt) if txt else []
    return ranges or ["전 범위"]

# -----------------------------
# 1) 하루별 총 가능 공부 분 (자유시간 ∩ 상한)
# 2) 과목별 '총 목표시간(시간)' 있는 경우는 과목별 유효일(시험일까지) 캡 비율로 배분
# 3) 나머지는 중요도/임박도 가중치로 배분 → 분으로 저장
# -----------------------------

# 먼저 각 날짜의 자유시간 계산 (고정일정은 아직 입력 안 했을 수도 있으니 함수로 재계산)

def day_free_cap_minutes(d: date) -> int:
    busy, _ = build_busy_intervals_for_day(d)
    free = invert_busy_to_free(d, busy)
    free_total = sum(int((e-s).total_seconds()//60) for s,e in free)
    cap = per_day_cap[d]
    return max(0, min(free_total, cap))

cap_total_min = sum(day_free_cap_minutes(d) for d in all_days)

# 고정 목표시간 분 (과목 지정치 합)
subjects_df["목표 총 학습시간(시간)"] = pd.to_numeric(subjects_df["목표 총 학습시간(시간)"], errors="coerce")

# 과목별 유효일(시험일까지) 자유시간 합
subject_valid_cap_sum: Dict[str,int] = {}
for _, row in subjects_df.iterrows():
    subj = row["과목"].strip()
    exam = row.get("시험일(선택)")
    valid_days = [d for d in all_days if (pd.isna(exam) or d <= pd.to_datetime(exam).date())]
    subject_valid_cap_sum[subj] = sum(day_free_cap_minutes(d) for d in valid_days)

rows_daily: List[Dict] = []
for d in all_days:
    day_cap = day_free_cap_minutes(d)
    if day_cap <= 0:
        continue
    # 2) 과목별 고정 배분 (유효일 비율)
    fixed_alloc: Dict[str,int] = {}
    for _, row in subjects_df.iterrows():
        subj = row["과목"].strip()
        if not subj: continue
        total_h = row.get("목표 총 학습시간(시간)")
        if pd.isna(total_h):
            continue
        # 시험 지나면 0
        exam = row.get("시험일(선택)")
        if (not pd.isna(exam)) and (d > pd.to_datetime(exam).date()):
            continue
        valid_sum = subject_valid_cap_sum.get(subj, 0)
        if valid_sum <= 0:
            continue
        share = (float(total_h)*60.0) * (day_cap/valid_sum)
        fixed_alloc[subj] = fixed_alloc.get(subj,0) + round5(int(round(share)))

    # 3) 자동 배분
    auto_df = subjects_df[pd.isna(subjects_df["목표 총 학습시간(시간)"])]
    auto_weights = compute_daily_weights(d, auto_df)
    remain = max(0, day_cap - sum(fixed_alloc.values()))
    auto_alloc: Dict[str,int] = {}
    if auto_weights and remain>0:
        s = sum(auto_weights.values())
        if s>0:
            for subj, w in auto_weights.items():
                auto_alloc[subj] = round5(int(round(remain * (w/s))))

    # 합치기
    all_subj = set(list(fixed_alloc.keys()) + list(auto_alloc.keys()))
    for subj in all_subj:
        minutes = fixed_alloc.get(subj,0) + auto_alloc.get(subj,0)
        minutes = round5(minutes)
        if minutes>0:
            rows_daily.append({"날짜": d, "과목": subj, "분": minutes})

plan_minutes_df = pd.DataFrame(rows_daily)
if plan_minutes_df.empty:
    st.warning("배분할 시간이 없습니다. 설정(상한/일과/고정일정)을 확인해 주세요.")
    st.stop()

# 과목별 범위 및 범위 당 목표분
subject_ranges: Dict[str,List[str]] = {}
subject_range_target: Dict[str,int] = {}
for _, row in subjects_df.iterrows():
    subj = row["과목"].strip()
    rngs = build_ranges_for_subject(row)
    subject_ranges[subj] = rngs
    total_min = int(plan_minutes_df[plan_minutes_df["과목"]==subj]["분"].sum())
    n = max(1, len(rngs))
    subject_range_target[subj] = max(5, round5(int(math.ceil(total_min/n))))

# 범위 단위로 세분화 + 누적 진척
progress_used: Dict[Tuple[str,str], int] = {}
rows_scoped: List[Dict] = []
for d in all_days:
    day_rows = plan_minutes_df[plan_minutes_df["날짜"]==d]
    for _, r in day_rows.iterrows():
        subj = r["과목"] ; remain = int(r["분"]) ; rngs = subject_ranges.get(subj,["전 범위"]) or ["전 범위"]
        target = subject_range_target.get(subj, max(5, round5(remain)))
        # 진행 중인 범위부터
        idx = 0
        for i, rg in enumerate(rngs):
            used = progress_used.get((subj,rg),0)
            if used < target:
                idx = i ; break
        while remain>0 and idx < len(rngs):
            rg = rngs[idx]
            used = progress_used.get((subj,rg),0)
            need = max(0, target - used)
            if need <= 0:
                idx += 1 ; continue
            take = min(need, remain)
            take = round5(take) if take>=5 else 5
            rows_scoped.append({"날짜": d, "과목": subj, "범위": rg, "분": int(take)})
            progress_used[(subj,rg)] = used + int(take)
            remain -= int(take)
            if progress_used[(subj,rg)] >= target:
                idx += 1

plan_scoped_df = pd.DataFrame(rows_scoped)

# 시험 당일 복습 추가
if review_on_exam_min > 0:
    extra = []
    for _, row in subjects_df.iterrows():
        ex = row.get("시험일(선택)")
        if pd.isna(ex):
            continue
        d = pd.to_datetime(ex).date()
        if (d < start_dt) or (d > end_dt):
            continue
        extra.append({"날짜": d, "과목": row["과목"].strip(), "범위": "복습", "분": round5(review_on_exam_min)})
    if extra:
        plan_scoped_df = pd.concat([plan_scoped_df, pd.DataFrame(extra)], ignore_index=True)

# -----------------------------
# 타임라인 배치 (자유구간에 공부 블록 배치, 휴식은 출력 생략)
# -----------------------------

def make_day_timeline(d: date, scoped_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
    busy, event_lines = build_busy_intervals_for_day(d)
    free = invert_busy_to_free(d, busy)
    items = scoped_df[scoped_df["날짜"]==d]

    blocks: List[Dict] = []
    free_idx = 0
    for _, it in items.iterrows():
        subj = it["과목"] ; rg = it["범위"] ; remain = int(it["분"])  # 5분 단위 가정
        while remain>0 and free_idx < len(free):
            fs, fe = free[free_idx]
            cur = fs
            while cur < fe and remain>0:
                # 한 번에 넣을 분량 (focus)
                possible = int((fe - cur).total_seconds()//60)
                if possible <= 0: break
                amt = min(focus_min, remain, possible)
                amt = round5(amt)
                if amt <= 0: break
                s = cur ; e = s + timedelta(minutes=amt)
                blocks.append({"type":"study","start":s,"end":e,"subj":subj,"range":rg,"minutes":amt})
                cur = e
                remain -= amt
                # 휴식(출력 생략, 공간만 차지)
                if remain>0 and break_min>0:
                    br = min(break_min, int((fe - cur).total_seconds()//60))
                    br = round5(br)
                    if br>0:
                        cur = cur + timedelta(minutes=br)
            if cur >= fe or int((fe - cur).total_seconds()//60) <= 0:
                free_idx += 1
            else:
                free[free_idx] = (cur, fe)
        # 남은 분은 이월하지 않음(상한/자유시간에 의해 제한)

    # 정렬
    blocks.sort(key=lambda x: x["start"])
    return pd.DataFrame(blocks), event_lines

# -----------------------------
# 다이어리 렌더링 (라인 스타일)
# -----------------------------

def icon_for_event(title: str) -> str:
    t = (title or "").lower()
    if "학교" in t:
        return "🏫"
    if "학원" in t:
        return "🎯"
    if "시험" in t:
        return "📝"
    return "🗓️"


def render_day_diary(d: date, tl_df: pd.DataFrame, event_lines: List[Dict]):
    day_label = WEEK_LABEL[d.weekday()]
    st.markdown(f"### 📅 {d.strftime('%m/%d')} ({day_label})")
    # 출력용 아이템 통합(이벤트 + 이동 + 공부)
    outputs: List[Dict] = []
    for ev in event_lines:
        if ev.get("type") == "event":
            outputs.append({
                "start": ev["start"],
                "end": ev["end"],
                "line": f"{icon_for_event(ev.get('title',''))} {ev['start'].strftime('%H:%M')} ~ {ev['end'].strftime('%H:%M')} {ev.get('title','일정')}"
            })
        elif ev.get("type") == "move":
            outputs.append({
                "start": ev["start"],
                "end": ev["end"],
                "line": f"🚌 {ev['start'].strftime('%H:%M')} ~ {ev['end'].strftime('%H:%M')} 이동"
            })
    if not tl_df.empty:
        for _, r in tl_df.iterrows():
            s: datetime = r["start"] ; e: datetime = r["end"]
            subj = r["subj"] ; rg = r["range"] ; mins = int(r["minutes"])
            icon = "🔁" if str(rg).strip()=="복습" else "✏️"
            outputs.append({
                "start": s,
                "end": e,
                "line": f"{icon} {s.strftime('%H:%M')} ~ {e.strftime('%H:%M')} {subj} - {rg} ({fmt_hm(mins)})"
            })
    if not outputs:
        st.write("- (계획 없음)")
        return
    outputs.sort(key=lambda x: x["start"]) 
    for o in outputs:
        st.write(o["line"])  # 라인 출력
# PDF 생성
# ✅ 월간 달력 PDF 생성 함수
from fpdf import FPDF
from io import BytesIO
import streamlit as st
import os

def fmt_hm(dt):
    return dt.strftime("%H:%M")

def make_calendar_pdf(all_days, plan_df):
    pdf = FPDF()
    pdf.add_page()

    # ✅ 한글/이모지 지원 폰트 등록
    # NotoSansCJK (또는 NanumGothic 등) TTF 경로 필요
    # 로컬 또는 서버에 설치된 폰트 경로 확인 필요
    font_path = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    if os.path.exists(font_path):
        pdf.add_font("NotoSans", "", font_path, uni=True)
        pdf.set_font("NotoSans", size=16)
    else:
        # fallback (서버에 폰트 없는 경우)
        pdf.set_font("Arial", size=16)

    # 제목
    pdf.cell(0, 10, "📅 학습 다이어리 (월간 달력)", ln=True, align="C")
    pdf.ln(5)

    # 요일 헤더
    pdf.set_font("NotoSans", "", 12) if "NotoSans" in pdf.fonts else pdf.set_font("Arial", size=12)
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    col_w = 277 / 7  # A4 가로폭
    row_h = 30
    for wd in weekdays:
        pdf.cell(col_w, 10, wd, border=1, align="C")
    pdf.ln()

    # 날짜별 박스
    day_idx = 0
    for week in range(6):  # 최대 6주
        for wd in range(7):
            if day_idx < len(all_days):
                d = all_days[day_idx]
                events = plan_df[plan_df["날짜"] == d]
                cell_text = f"{d.day}\n"
                for _, ev in events.iterrows():
                    stime = fmt_hm(ev["시작"])
                    etime = fmt_hm(ev["끝"])
                    title = ev["과목"]
                    detail = ev.get("세부", "")
                    duration = int((ev["끝"] - ev["시작"]).total_seconds() // 60)
                    hours, mins = divmod(duration, 60)
                    dur_str = f"{hours}시간 {mins}분" if hours else f"{mins}분"
                    cell_text += f"{stime}~{etime} {title} {detail} ({dur_str})\n"
                pdf.multi_cell(col_w, 5, cell_text, border=1)
            else:
                pdf.cell(col_w, row_h, "", border=1)
            day_idx += 1
        pdf.ln()

    # PDF를 Bytes로 반환
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes

# -----------------------------
# 좌: 요약, 우: 다이어리 미리보기(전체 기간)
# -----------------------------
left, right = st.columns([1,2])
with left:
    st.subheader("📊 과목별 총 배정")
    summary = plan_minutes_df.groupby("과목")["분"].sum().reset_index().sort_values("분", ascending=False)
    summary["표시"] = summary["분"].apply(fmt_hm)
    st.dataframe(summary.rename(columns={"분":"총 분", "표시":"총 시간"}), use_container_width=True)

with right:
    st.subheader("🗓️ 다이어리 보기")
    for d in all_days:
        tl_df, ev_lines = make_day_timeline(d, plan_scoped_df)
        render_day_diary(d, tl_df, ev_lines)

# -----------------------------
# 다운로드
st.subheader("📥 다운로드")

# CSV 다운로드
plan_csv = plan_scoped_df.copy()
plan_csv["분(표시)"] = plan_csv["분"].apply(fmt_hm)
st.download_button(
    "과목·범위·분 CSV",
    data=plan_csv.to_csv(index=False).encode("utf-8-sig"),
    file_name="study_plan_scoped.csv",
    mime="text/csv"
)

# PDF 다운로드
pdf_bytes = make_calendar_pdf(all_days, plan_scoped_df)
st.download_button(
    label="📥 월간 학습 다이어리 PDF 다운로드",
    data=pdf_bytes,
    file_name="study_calendar.pdf",
    mime="application/pdf"
)
