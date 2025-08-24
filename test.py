import os
import requests
import streamlit as st
import random
from typing import Dict, List, Tuple

API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY") or "YOUR_API_KEY_HERE"

# --- 페이지 설정 및 스타일 ---
st.set_page_config(page_title="AI 독서 추천 웹앱", page_icon="📖✨", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #26365c; color: #ffffff; font-family: 'Pretendard', 'Arial Rounded MT Bold', sans-serif; }
h1,h2,h3,h4 { color: #ffffff; }
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

# --- 데이터 정의 (기존 코드 유지) ---
TYPES = { ... }  # 생략 (이전 코드와 동일)
BOOKS = { ... }  # 생략
QUESTIONS = [ ... ]  # 생략

def score_types(...): ...  # 이전 함수 유지
def best_types(...): ...
def recommend_by_types(...): ...
def recommend_by_genre(...): ...

# --- 외부 API 기반 추천 기능 ---
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
    st.header("독서 성향 맞춤 추천 앱")
    st.write("성향 테스트, 장르 추천, 온라인 실시간 추천 기능을 제공합니다.")

elif menu == "성향 테스트":
    # 기존 설문 + 추천 로직 유지...
    pass

elif menu == "장르별 추천":
    # 기존 장르별 UI 유지...
    pass

else:  # 키워드 기반 외부 API 추천
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
                        f"<div class='card'><b>{b['title']}</b><br><span class='small-note'>저자: {b['authors']}</span><br>{b['description'][:200]}...</div>",
                        unsafe_allow_html=True
                    )

st.caption("ⓒ AI 독서 추천 · Google Books API 기반")
