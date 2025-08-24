import streamlit as st
import pandas as pd
import datetime

# ------------------------------
# 유틸 함수
# ------------------------------
def format_minutes(minutes: int) -> str:
    """분 단위를 'X시간 Y분'으로 변환, 5분 단위 반올림"""
    if minutes <= 0:
        return ""
    minutes = round(minutes / 5) * 5
    h, m = divmod(minutes, 60)
    if h > 0 and m > 0:
        return f"{h}시간 {m}분"
    elif h > 0:
        return f"{h}시간"
    else:
        return f"{m}분"

def parse_range(text: str):
    """시험 범위 텍스트 파싱 (예: '1~3단원' -> [1,2,3])"""
    text = text.replace(" ", "")
    if "~" in text:
        prefix = ''.join([c for c in text if not c.isdigit() and c != "~"])
        nums = [int(s) for s in text.replace(prefix, "").split("~")]
        return [f"{prefix}{i}" for i in range(nums[0], nums[1] + 1)]
    elif "," in text:
        return [t for t in text.split(",")]
    else:
        return [text]

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="📅 학습 다이어리 플래너", layout="wide")
st.title("📅 학습 다이어리 플래너")

# 입력: 기간
st.sidebar.header("📌 학습 기간 설정")
start_date = st.sidebar.date_input("시작일", datetime.date.today())
end_date = st.sidebar.date_input("목표일", start_date + datetime.timedelta(days=7))

# 입력: 과목
st.sidebar.header("📚 과목 입력")
num_subjects = st.sidebar.number_input("과목 수", 1, 10, 2)
subjects = []
for i in range(num_subjects):
    st.sidebar.subheader(f"과목 {i+1}")
    name = st.sidebar.text_input(f"과목명 {i+1}", f"과목{i+1}")
    importance = st.sidebar.slider(f"중요도 {i+1}", 1, 5, 3)
    exam_date = st.sidebar.date_input(f"시험일 {i+1}", end_date)
    total_time = st.sidebar.number_input(f"목표 총 공부시간(분) {i+1}", 60, 3000, 300, step=30)
    exam_range = st.sidebar.text_input(f"시험 범위 {i+1}", "1~3단원")
    subjects.append({
        "name": name,
        "importance": importance,
        "exam_date": exam_date,
        "total_time": total_time,
        "range": exam_range
    })

# 입력: 고정 일정
st.sidebar.header("🏫 고정 일정")
num_events = st.sidebar.number_input("고정 일정 개수", 0, 10, 2)
events = []
for i in range(num_events):
    st.sidebar.subheader(f"고정 일정 {i+1}")
    title = st.sidebar.text_input(f"일정명 {i+1}", "학교")
    day = st.sidebar.selectbox(f"요일 {i+1}", ["월", "화", "수", "목", "금", "토", "일"])
    start = st.sidebar.time_input(f"시작 시간 {i+1}", datetime.time(9,0))
    end = st.sidebar.time_input(f"종료 시간 {i+1}", datetime.time(15,0))
    buffer = st.sidebar.number_input(f"이동시간(분) {i+1}", 0, 60, 10)
    events.append({"title": title, "day": day, "start": start, "end": end, "buffer": buffer})

# ------------------------------
# 계획 생성 로직
# ------------------------------
if st.button("📅 학습 계획 세우기"):
    st.subheader("📖 생성된 다이어리")

    plan = {}

    for subj in subjects:
        ranges = parse_range(subj["range"])
        total_blocks = len(ranges)
        per_block_time = subj["total_time"] // total_blocks

        # 시험일까지 남은 날 계산
        days = (subj["exam_date"] - start_date).days + 1
        day_gap = max(1, days // total_blocks)

        for i, r in enumerate(ranges):
            study_day = start_date + datetime.timedelta(days=i * day_gap)
            if study_day > subj["exam_date"]:
                study_day = subj["exam_date"] - datetime.timedelta(days=1)

            if study_day not in plan:
                plan[study_day] = []
            plan[study_day].append({
                "type": "study",
                "title": f"{subj['name']} - {r}",
                "minutes": per_block_time
            })

        # 시험 당일 복습
        if subj["exam_date"] not in plan:
            plan[subj["exam_date"]] = []
        plan[subj["exam_date"]].append({
            "type": "exam",
            "title": f"{subj['name']} 시험 복습",
            "minutes": 60
        })

    # 고정 일정 추가
    weekday_map = {"월":0, "화":1, "수":2, "목":3, "금":4, "토":5, "일":6}
    cur_date = start_date
    while cur_date <= end_date:
        wday = cur_date.weekday()
        for ev in events:
            if weekday_map[ev["day"]] == wday:
                if cur_date not in plan:
                    plan[cur_date] = []
                plan[cur_date].append({
                    "type": "event",
                    "title": ev["title"],
                    "time": (ev["start"], ev["end"]),
                    "buffer": ev["buffer"]
                })
        cur_date += datetime.timedelta(days=1)

    # ------------------------------
    # 출력 (다이어리 스타일)
    # ------------------------------
    for day in sorted(plan.keys()):
        st.markdown(f"### 📅 {day.strftime('%m/%d (%a)')}")
        day_plan = plan[day]

        # 고정 일정 먼저 출력
        for ev in [x for x in day_plan if x["type"]=="event"]:
            st.write(f"🏫 {ev['start'].strftime('%H:%M')} ~ {ev['end'].strftime('%H:%M')} {ev['title']}")
            if ev['buffer']>0:
                end_plus = (datetime.datetime.combine(day, ev['end']) + datetime.timedelta(minutes=ev['buffer'])).time()
                st.write(f"🚌 {ev['end'].strftime('%H:%M')} ~ {end_plus.strftime('%H:%M')} 이동")

        # 공부 일정
        for ev in [x for x in day_plan if x["type"]=="study"]:
            st.write(f"✏️ {ev['title']} ({format_minutes(ev['minutes'])})")

        # 시험 복습
        for ev in [x for x in day_plan if x["type"]=="exam"]:
            st.write(f"🔁 {ev['title']} ({format_minutes(ev['minutes'])})")
