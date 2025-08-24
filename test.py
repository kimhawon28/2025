import streamlit as st
import pandas as pd
import datetime
import calendar
from io import BytesIO

# ReportLab
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# --------------------------
# PDF 폰트 설정 (한글 지원)
# --------------------------
pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

# --------------------------
# 분 → "X시간 Y분" 변환 함수
# --------------------------
def format_minutes(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    if h > 0:
        return f"{h}시간 {m}분" if m > 0 else f"{h}시간"
    else:
        return f"{m}분"

# --------------------------
# 달력 PDF 생성
# --------------------------
def create_calendar_pdf(plan, year, month):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    month_days = list(cal.itermonthdates(year, month))

    cell_width = width / 7
    cell_height = height / 6

    # 요일 헤더
    c.setFont("HYSMyeongJo-Medium", 14)
    days = ["일", "월", "화", "수", "목", "금", "토"]
    for i, d in enumerate(days):
        c.drawCentredString((i + 0.5) * cell_width, height - 20, d)

    # 날짜별 일정 채우기
    c.setFont("HYSMyeongJo-Medium", 9)
    for idx, day in enumerate(month_days):
        row = idx // 7
        col = idx % 7
        x = col * cell_width
        y = height - (row + 1) * cell_height

        # 날짜 표시
        c.rect(x, y, cell_width, cell_height)
        c.drawString(x + 5, y + cell_height - 15, str(day.day))

        # 일정 넣기 (최대 4줄)
        if day in plan:
            yy = y + cell_height - 30
            for ev in plan[day][:4]:
                if ev["type"] == "event":
                    text = f"🏫 {ev['title']}"
                elif ev["type"] == "study":
                    text = f"✏️ {ev['title']} ({format_minutes(ev['minutes'])})"
                elif ev["type"] == "exam":
                    text = f"🔁 {ev['title']} ({format_minutes(ev['minutes'])})"
                else:
                    text = ev["title"]
                c.drawString(x + 5, yy, text[:20])  # 긴 텍스트 자르기
                yy -= 12

    c.save()
    buffer.seek(0)
    return buffer

# --------------------------
# Streamlit UI
# --------------------------
st.title("📅 공부 계획 + 월간 달력 생성기")

st.sidebar.header("1. 기간 설정")
start_date = st.sidebar.date_input("시작 날짜", datetime.date.today())
end_date = st.sidebar.date_input("목표 날짜", start_date + datetime.timedelta(days=30))

st.sidebar.header("2. 과목 입력")
st.sidebar.write("시험 범위 또는 목표 학습시간을 입력하세요.")

if "subjects" not in st.session_state:
    st.session_state["subjects"] = []

subject_name = st.sidebar.text_input("과목명")
subject_range = st.sidebar.text_input("시험 범위 (예: 1~3단원, Lesson 1-2)")
subject_hours = st.sidebar.number_input("목표 학습시간(시간 단위)", min_value=0, value=0, step=1)
importance = st.sidebar.slider("중요도", 1, 5, 3)
exam_date = st.sidebar.date_input("시험일 (선택)", value=None)

if st.sidebar.button("➕ 과목 추가"):
    st.session_state["subjects"].append({
        "name": subject_name,
        "range": subject_range,
        "hours": subject_hours,
        "importance": importance,
        "exam_date": exam_date if exam_date != datetime.date.today() else None
    })

st.sidebar.write("현재 과목 목록:")
for s in st.session_state["subjects"]:
    st.sidebar.write(f"- {s['name']} ({s['range'] if s['range'] else str(s['hours'])+'시간'})")

st.sidebar.header("3. 개인 일정 입력")
if "events" not in st.session_state:
    st.session_state["events"] = []

event_title = st.sidebar.text_input("일정명 (예: 학교, 학원, 이동)")
event_date = st.sidebar.date_input("날짜", value=start_date)
event_start = st.sidebar.time_input("시작 시간", datetime.time(9,0))
event_end = st.sidebar.time_input("종료 시간", datetime.time(10,0))

if st.sidebar.button("➕ 일정 추가"):
    st.session_state["events"].append({
        "title": event_title,
        "date": event_date,
        "start": event_start,
        "end": event_end
    })

st.sidebar.write("현재 일정 목록:")
for e in st.session_state["events"]:
    st.sidebar.write(f"- {e['date']} {e['title']} {e['start']}~{e['end']}")

# --------------------------
# 계획 자동 생성 (단순 예시)
# --------------------------
def make_plan(subjects, events, start_date, end_date):
    plan = {}
    days = pd.date_range(start=start_date, end=end_date)

    # 이벤트 반영
    for e in events:
        d = e["date"]
        if d not in plan: plan[d] = []
        plan[d].append({
            "type": "event",
            "title": e["title"],
            "start": datetime.datetime.combine(d, e["start"]),
            "end": datetime.datetime.combine(d, e["end"])
        })

    # 공부 반영 (단순 분배)
    for s in subjects:
        total_minutes = s["hours"] * 60 if s["hours"] > 0 else 120  # 기본 2시간
        per_day = max(30, total_minutes // len(days))
        for d in days:
            if d not in plan: plan[d] = []
            plan[d].append({
                "type": "study",
                "title": f"{s['name']} {s['range']}",
                "minutes": per_day
            })

        if s["exam_date"]:
            if s["exam_date"] not in plan: plan[s["exam_date"]] = []
            plan[s["exam_date"]].append({
                "type": "exam",
                "title": f"{s['name']} 시험 복습",
                "minutes": 60
            })
    return plan

if st.button("📌 계획 짜기"):
    plan = make_plan(st.session_state["subjects"], st.session_state["events"], start_date, end_date)

    st.success("✅ 계획이 생성되었습니다!")

    today = datetime.date.today()
    pdf_buffer = create_calendar_pdf(plan, today.year, today.month)

    st.download_button(
        label="📥 달력 PDF 다운로드",
        data=pdf_buffer,
        file_name="study_calendar.pdf",
        mime="application/pdf"
    )
