import streamlit as st
import random
import folium
from streamlit_folium import st_folium

# ------------------------------
# 책 데이터
# ------------------------------
BOOKS = [
    {
        "title": "노인과 바다",
        "emotion": "우울",
        "lesson": "인간은 패배하도록 만들어지지 않았다. 인간은 파괴될 수는 있어도 패배하지 않는다.",
        "character": {"name": "산티아고", "mbti": "INTJ"},
        "location": (23.1136, -82.3666),  # 쿠바 아바나 근처
        "music": "https://www.youtube.com/embed/1q6S7Cz8H7U"
    },
    {
        "title": "데미안",
        "emotion": "사색",
        "lesson": "새는 알을 깨고 나온다. 스스로를 찾는 자의 투쟁.",
        "character": {"name": "싱클레어", "mbti": "INFP"},
        "location": (49.4875, 8.4660),  # 독일 만하임
        "music": "https://www.youtube.com/embed/Bbz8i4V8XqU"
    },
    {
        "title": "해리포터와 마법사의 돌",
        "emotion": "행복",
        "lesson": "행복은 가장 어두운 순간에도 빛을 찾는 자의 것이다.",
        "character": {"name": "해리 포터", "mbti": "ENFJ"},
        "location": (51.7520, -1.2577),  # 옥스퍼드
        "music": "https://www.youtube.com/embed/Htaj3o3JD8I"
    }
]

# ------------------------------
# 세션 상태 초기화
# ------------------------------
if "completed" not in st.session_state:
    st.session_state["completed"] = []
if "book" not in st.session_state:
    st.session_state["book"] = None

# ------------------------------
# UI
# ------------------------------
st.title("📚 감정 기반 책 추천기 + 독서 여정 지도")

menu = st.sidebar.radio("메뉴 선택", ["홈", "추천 받기", "내 독서 여정 지도"])

# ------------------------------
# 홈 화면
# ------------------------------
if menu == "홈":
    st.write("안녕하세요! 😀")
    st.write("오늘의 감정과 MBTI를 선택하면 책을 추천해드리고, 교훈·음악·캐릭터 정보까지 보여줍니다.")
    st.write("책을 다 읽으면 '독서 완료' 버튼을 눌러 나의 독서 여정을 지도에 기록할 수 있어요!")

# ------------------------------
# 추천 받기
# ------------------------------
elif menu == "추천 받기":
    emotion = st.selectbox("오늘 기분은?", ["행복", "우울", "사색"])
    mbti = st.selectbox("내 MBTI는?", ["INTJ", "INFP", "ENFJ"])

    if st.button("책 추천 받기"):
        candidates = [b for b in BOOKS if b["emotion"] == emotion]
        if candidates:
            book = random.choice(candidates)
            st.session_state["book"] = book
            st.session_state["mbti"] = mbti

    if st.session_state["book"]:
        book = st.session_state["book"]
        st.subheader(f"추천 책: {book['title']}")
        st.write(f"**오늘의 교훈:** {book['lesson']}")

        # MBTI 매칭
        same_mbti = "❌ 없음"
        if book["character"]["mbti"] == st.session_state["mbti"]:
            same_mbti = f"✅ {book['character']['name']} ({book['character']['mbti']})"
        st.write(f"**당신과 같은 MBTI 캐릭터:** {same_mbti}")

        # 음악
        st.components.v1.iframe(book["music"], width=400, height=225)

        if st.button("📖 독서 완료!"):
            if book not in st.session_state["completed"]:
                st.session_state["completed"].append(book)
            st.success("독서 완료! 지도에 기록되었습니다 ✅")

# ------------------------------
# 독서 여정 지도
# ------------------------------
elif menu == "내 독서 여정 지도":
    st.subheader("🌍 나의 독서 여정 지도")
    if not st.session_state["completed"]:
        st.info("아직 완료한 책이 없습니다. 먼저 책을 추천받고 완료해주세요!")
    else:
        m = folium.Map(location=[20, 0], zoom_start=2)
        for b in st.session_state["completed"]:
            lat, lng = b["location"]
            folium.Marker([lat, lng], popup=b["title"]).add_to(m)
        st_folium(m, width=700, height=500)
