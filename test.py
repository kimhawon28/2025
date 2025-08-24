import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta

# ------------------------------
# 유틸 함수
# ------------------------------
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

def fmt_hm(minutes):
    """분 단위를 HH:MM 문자열로 변환"""
    if pd.isna(minutes):
        return ""
    try:
        minutes = int(minutes)
        h, m = divmod(minutes, 60)
        return f"{h:02d}:{m:02d}"
    except Exception:
        return str(minutes)

# ------------------------------
# 더미 일정 데이터 생성
# ------------------------------
def load_plan():
    today = date.today()
    start = today.replace(day=1)
    all_days = [start + timedelta(days=i) for i in range(31) if (start + timedelta(days=i)).month == start.month]

    # 예시 일정 데이터프레임
    rows = []
    for d in all_days:
        if d.day % 5 == 0:  # 5일마다 예시 일정 생성
            rows.append({
                "날짜": d.strftime("%Y-%m-%d"),
                "시작": "09:00",
                "종료": "10:30",
                "과목": "수학",
                "범위": "미적분",
                "분": 90
            })
            rows.append({
                "날짜": d.strftime("%Y-%m-%d"),
                "시작": "14:00",
                "종료": "15:00",
                "과목": "영어",
                "범위": "독해",
                "분": 60
            })
    return all_days, pd.DataFrame(rows)

# ------------------------------
# Streamlit UI
# ------------------------------
st.title("📘 학습 다이어리")

# 일정 불러오기
all_days, plan_scoped_df = load_plan()

# ------------------------------
# 📅 월간 달력 테이블 출력
# ------------------------------
st.header("📅 월간 달력 보기")

data = [["날짜", "일정"]]
for d in all_days:
    daily_plan = plan_scoped_df[plan_scoped_df["날짜"] == d.strftime("%Y-%m-%d")]
    if daily_plan.empty:
        data.append([d.strftime("%m/%d (%a)"), ""])
    else:
        schedules = []
        for _, row in daily_plan.iterrows():
            subj = row.get("과목", "")
            rg = row.get("범위", "")
            minutes = row.get("분", 0)
            schedules.append(f"{row['시작']}~{row['종료']} {subj} - {rg} ({fmt_hm(minutes)})")
        data.append([d.strftime("%m/%d (%a)"), "\n".join(schedules)])

calendar_df = pd.DataFrame(data[1:], columns=data[0])
st.table(calendar_df)
