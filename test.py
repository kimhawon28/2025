import os
import requests
import streamlit as st
import random
from typing import Dict, List

# 🔑 Google Books API 키 (환경변수 또는 직접 입력)
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY") or "YOUR_API_KEY_HERE"

# --- 페이지 설정 & 스타일 ---
st.set_page_config(page_title="AI 독서 추천 웹앱", page_icon="📖✨", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #26365c; color: #ffffff; font-family: 'Pretendard','Arial Rounded MT Bold',sans-serif; }
h1,h2,h3,h4,h5 { color:#ffffff; }
.card { padding:1rem; margin-bottom:1rem; border-radius:1rem; background-color: rgba(255,255,255,0.08); box-shadow:0 4px 10px rgba(0,0,0,0.3); color:#ffffff; }
.small-note { font-size:0.9rem; color:#dddddd; }
.stButton>button { background-color:#445 !important; color:#ffffff !important; border-radius:12px !important; padding:0.6rem 1.2rem !important; font-weight:700 !important; }
.stButton>button:hover { background-color:#667 !important; }
section[data-testid="stSidebar"] { background-color: #f7f8fa !important; }
section[data-testid="stSidebar"] * { color: #000000 !important; }
.stTextInput input, .stTextArea textarea { color:#000000 !important; background:#ffffff !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: rgba(0,0,0,0.55) !important; }
</style>
<audio autoplay loop style="display:none">
  <source src="https://upload.wikimedia.org/wikipedia/commons/0/0e/Beethoven_Moonlight_1st_movement.ogg" type="audio/ogg">
</audio>
""", unsafe_allow_html=True)

# --- 성향 유형 & 책 데이터 ---
TYPES = {
    "감성적 몰입형": "책 속에 완전히 빠져드는 타입. 감정을 따라가는 독서를 즐깁니다.",
    "분석적 탐구형": "내용을 깊이 분석하고 생각하는 걸 선호합니다.",
    "모험적 탐험형": "새로운 장르, 색다른 책에 호기심이 많습니다.",
    "사색적 성찰형": "읽고 난 뒤 오래 곱씹는 사색가적 독자입니다.",
    "사회적 교류형": "책을 매개로 사람들과 나누는 걸 좋아합니다.",
    "현실적 실용형": "실질적으로 도움 되는 지식을 찾는 타입입니다.",
    "예술적 감각형": "문체, 디자인, 감각적인 요소에 끌립니다.",
    "치유적 위로형": "책에서 위로와 공감을 얻고 싶어 합니다.",
    "속독적 효율형": "빠르게 핵심을 파악하는 걸 선호합니다.",
    "지적 완벽형": "체계적으로 읽고 완전히 이해하려는 성향입니다."
}

BOOKS = {
    "감성적 몰입형": ["파친코", "연의 편지", "모든 순간이 너였다"],
    "분석적 탐구형": ["총균쇠", "사피엔스", "정의란 무엇인가"],
    "모험적 탐험형": ["오만과 편견", "이방인", "드래곤라자"],
    "사색적 성찰형": ["데미안", "인생 수업", "노인과 바다"],
    "사회적 교류형": ["트렌드 코리아", "넛지", "미디어의 이해"],
    "현실적 실용형": ["업글 인간", "성공하는 사람들의 7가지 습관", "에세이 글쓰기"],
    "예술적 감각형": ["달과 6펜스", "윤동주 시집", "나미야 잡화점의 기적"],
    "치유적 위로형": ["아몬드", "죽고 싶지만 떡볶이는 먹고 싶어", "오늘도 펭수, 내일도 펭수"],
    "속독적 효율형": ["하루 3분 책읽기", "스피드 리딩", "Essential Grammar"],
    "지적 완벽형": ["칸트 순수이성비판", "자본론", "플라톤 전집"]
}

QUESTIONS = [
    {"q": "책을 읽을 때 가장 중요한 건?", "options": {
        "감정이입": {"감성적 몰입형": 2, "치유적 위로형": 1},
        "정보와 지식": {"분석적 탐구형": 2, "현실적 실용형": 1},
        "새로운 경험": {"모험적 탐험형": 2, "예술적 감각형": 1},
    }},
    {"q": "책을 다 읽고 난 후 당신은?", "options": {
        "여운과 감정을 곱씹는다": {"사색적 성찰형": 2, "감성적 몰입형": 1},
        "핵심 내용을 정리한다": {"속독적 효율형": 2, "지적 완벽형": 1},
        "주변 사람과 이야기를 나눈다": {"사회적 교류형": 2},
    }},
    {"q": "당신이 고르는 책의 기준은?", "options": {
        "실용성, 도움이 되는가": {"현실적 실용형": 2, "분석적 탐구형": 1},
        "표지, 문체 등 감각적 요소": {"예술적 감각형": 2},
        "읽으며 위로를 받을 수 있는가": {"치유적 위로형": 2, "감성적 몰입형": 1},
    }},
]

# --- 성향 테스트 계산 함수 ---
def score_types(answers: Dict[int, str]) -> Dict[str, int]:
    scores = {t: 0 for t in TYPES.keys()}
    for i, ans in answers.items():
        for t, pts in QUESTIONS[i]["options"][ans].items():
            scores[t] += pts
    return scores

def best_types(scores: Dict[str, int], topn: int = 2) -> List[str]:
    return sorted(scores, key=lambda x: -scores[x])[:topn]

def recommend_by_types(types: List[str], k: int = 3) -> Dict[str, List[str]]:
    rec = {}
    for t in types:
        rec[t] = random.sample(BOOKS.get(t, []), min(k, len(BOOKS.get(t, []))))
    return rec

def recommend_by_genre(genre: str, k: int = 5) -> List[str]:
    return random.sample(BOOKS.get(genre, []), min(k, len(BOOKS.get(genre, []))))

# --- Google Books API 기반 추천 ---
def recommend_by_keyword_api(keyword: str, max_results: int = 5) -> List[Dict]:
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": keyword, "key": API_KEY, "printType": "books", "maxResults": max_results}
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return []
    data = res.json()
    results = []
    for item in data.get("items", []):
        info = item.get("volumeInfo", {})
        results.append({
            "title": info.get("title", "—"),
            "authors": ", ".join(info.get("authors", ["—"])),
            "description": info.get("description", "설명 없음"),
        })
    return results

# --- UI 구성 ---
st.sidebar.title("메뉴")
menu = st.sidebar.radio("선택하세요", ["홈", "성향 테스트", "장르별 추천", "키워드 온라인 추천"])

if menu == "홈":
    st.header("📖✨ 독서 성향 맞춤 추천 앱")
    st.write("👉 성향 테스트, 장르 추천, 온라인 실시간 추천 기능을 제공합니다.")

elif menu == "성향 테스트":
    st.header("🧭 독서 성향 테스트")
    answers = {}
    for i, q in enumerate(QUESTIONS):
        ans = st.radio(q["q"], list(q["options"].keys()), key=f"q{i}")
        answers[i] = ans
    if st.button("결과 보기"):
        scores = score_types(answers)
        tops = best_types(scores)
        recs = recommend_by_types(tops)
        for t in tops:
            st.markdown(f"<div class='card'><b>{t}</b> - {TYPES[t]}<br>추천 책: {', '.join(recs[t])}</div>", unsafe_allow_html=True)

elif menu == "장르별 추천":
    st.header("🎨 장르별 추천")
    genre = st.selectbox("장르를 선택하세요", list(BOOKS.keys()))
    if st.button("추천 받기"):
        recs = recommend_by_genre(genre)
        st.markdown(f"<div class='card'><b>{genre}</b> 추천 책: {', '.join(recs)}</div>", unsafe_allow_html=True)

else:  # 온라인 추천
    st.header("🔎 온라인 키워드 기반 책 추천")
    kw = st.text_input("관심 있는 주제를 입력해 보세요", "")
    if st.button("추천 검색"):
        if not kw.strip():
            st.warning("키워드를 입력해 주세요.")
        else:
            recs = recommend_by_keyword_api(kw, max_results=6)
            if not recs:
                st.info("관련 도서를 찾기 어려웠어요.")
            else:
                for b in recs:
                    st.markdown(
                        f"<div class='card'><b>{b['title']}</b><br>"
                        f"<span class='small-note'>저자: {b['authors']}</span><br>"
                        f"{b['description'][:200]}...</div>",
                        unsafe_allow_html=True
                    )

st.caption("ⓒ AI 독서 추천 · Google Books API 기반")
