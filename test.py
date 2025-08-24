import streamlit as st
import random
import requests
from typing import List, Dict, Tuple

# ------------------------------
# 페이지 설정
# ------------------------------
st.set_page_config(
    page_title="독서 성향 기반 책 추천",
    page_icon="📖✨",
    layout="wide",
)

# ------------------------------
# 전역 스타일 / 폰트 / BGM
# ------------------------------
st.markdown("""
<style>
/* 배경 & 기본 텍스트 */
.stApp {
    background-color: #26365c; /* 네이비 */
    color: #ffffff;
    font-family: 'Arial Rounded MT Bold', 'Helvetica Rounded', 'Pretendard', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
}

/* 본문 내 제목/문단을 흰색으로 고정 */
h1, h2, h3, h4, h5, h6,
.stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div {
    color: #ffffff;
}

/* 카드 스타일 */
.card {
    padding: 1rem;
    border-radius: 1rem;
    background-color: rgba(255,255,255,0.08);
    box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 0.8rem;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.card img { border-radius: 8px; max-width: 80px; }

/* 작은 설명 텍스트 */
.small-note {
    font-size: 0.9rem;
    color: #dddddd;
}

/* 버튼 */
.stButton > button {
    background-color: #445 !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.2rem !important;
    border: none !important;
    font-weight: 700 !important;
    transition: transform 0.2s ease;
}
.stButton > button:hover {
    background-color: #667 !important;
    transform: scale(1.03);
}

/* ===== 메인 영역 UI(라디오/셀렉트/텍스트 등) 텍스트: 흰색 ===== */
div[data-testid="stRadio"] label,
div[data-testid="stSelectbox"] label,
div[data-baseweb="radio"] *:not(input),
div[role="radiogroup"] label,
div[data-testid="stMarkdownContainer"] * {
    color: #ffffff !important;
}

/* ===== 입력창 내부 텍스트/placeholder: 검정 ===== */
.stTextInput input,
.stTextArea textarea,
.stSelectbox [role="combobox"] input,
.stNumberInput input,
.stDateInput input,
.stTimeInput input,
.stMultiSelect input {
    color: #000000 !important;
    background: #ffffff !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: rgba(0,0,0,0.55) !important;
}

/* 드롭다운 팝오버 내 텍스트(옵션) 검정 */
[data-baseweb="popover"] * {
    color: #000000 !important;
}

/* ===== 사이드바: 배경 밝게 + 모든 텍스트 검정 ===== */
section[data-testid="stSidebar"] {
    background-color: #f7f8fa !important;
}
section[data-testid="stSidebar"] * {
    color: #000000 !important;
}
/* 사이드바 라디오 강조 */
section[data-testid="stSidebar"] [data-baseweb="radio"] label {
    font-weight: 600 !important;
}
</style>

<!-- 배경 음악: (선택사항) -->
<audio autoplay loop style="display:none">
  <source src="https://upload.wikimedia.org/wikipedia/commons/0/0e/Beethoven_Moonlight_1st_movement.ogg" type="audio/ogg">
</audio>
""", unsafe_allow_html=True)

# ==============================
# 데이터 정의 (10유형 + 책 데이터)
# ==============================
import os
import random
import requests
import streamlit as st

# -------------------------
# 유형 데이터
# -------------------------
TYPES = {
    "힐링 독서형": "마음을 위로받고 치유받는 독서를 선호해요.",
    "감성 몰입형": "감정을 자극하는 문학 작품을 즐겨요.",
    "철학 사색형": "깊은 사유와 철학적 텍스트를 탐구해요.",
    "사회 참여형": "사회 문제와 역사에 관심이 많아요.",
    "트렌드 캐처형": "베스트셀러와 최신 화제작을 따라가요.",
    "현실 적용형": "실용적이고 자기계발에 도움 되는 책을 좋아해요.",
    "지식 탐구형": "정보, 과학, 지식을 탐구하는 독서가 즐거워요.",
    "가벼운 즐김형": "재미와 오락을 위한 가벼운 책을 즐겨요.",
    "스토리 몰입형": "몰입감 있는 소설을 선호해요.",
    "실험적 독서형": "시, 실험적인 텍스트에 매력을 느껴요.",
}

# -------------------------
# 네이버 도서 API 함수
# -------------------------
def recommend_by_naver_books(keyword: str, max_results: int = 6) -> list:
    CLIENT_ID = os.getenv("NAVER_CLIENT_ID") or "YOUR_CLIENT_ID"
    CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET") or "YOUR_CLIENT_SECRET"
    url = "https://openapi.naver.com/v1/search/book.json"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    params = {"query": keyword, "display": max_results}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    if resp.status_code != 200:
        return []
    items = resp.json().get("items", [])
    results = []
    for it in items:
        results.append({
            "title": it.get("title", "제목 없음"),
            "author": it.get("author", "저자 미상"),
            "publisher": it.get("publisher", ""),
            "description": it.get("description", ""),
            "image": it.get("image", None),
            "pubdate": it.get("pubdate", "")
        })
    return results

# -------------------------
# Streamlit 기본 설정
# -------------------------
st.set_page_config(page_title="독서 성향 추천", page_icon="📚", layout="wide")

# -------------------------
# 사이드바 메뉴
# -------------------------
menu = st.sidebar.radio(
    "메뉴 선택",
    ["성향 테스트", "장르별 추천", "내 리스트 기반 추천", "키워드 온라인 추천(네이버)"]
)

# -------------------------
# 성향 테스트 (간단 버전)
# -------------------------
if menu == "성향 테스트":
    st.header("🧭 독서 성향 테스트")

    st.write("아래 질문에 답해주세요!")

    q1 = st.radio("1. 책을 읽을 때 나는?", ["감정을 크게 느끼는 편이다", "지식을 얻는 것이 더 좋다"])
    q2 = st.radio("2. 나는?", ["철학적이고 사색적인 편", "실용적이고 현실적인 편"])
    q3 = st.radio("3. 책을 고를 때?", ["베스트셀러/트렌드를 본다", "내 취향대로 고른다"])

    if st.button("결과 보기"):
        # 간단한 로직 예시
        if q1 == "감정을 크게 느끼는 편이다":
            result = "감성 몰입형"
        elif q2 == "철학적이고 사색적인 편":
            result = "철학 사색형"
        elif q3 == "베스트셀러/트렌드를 본다":
            result = "트렌드 캐처형"
        else:
            result = random.choice(list(TYPES.keys()))

        st.success(f"당신의 독서 유형은 **{result}** 입니다!")
        st.caption(TYPES[result])

# -------------------------
# 장르별 추천
# -------------------------
elif menu == "장르별 추천":
    st.header("🎯 장르/유형 감성으로 추천 받기")
    choice = st.selectbox("원하는 분위기/유형을 골라주세요", list(TYPES.keys()))
    st.success(f"선택된 유형: {choice}")
    st.caption(TYPES[choice])

# -------------------------
# 내 리스트 기반 추천
# -------------------------
elif menu == "내 리스트 기반 추천":
    st.header("📝 최근 읽은 책/키워드 기반 추천")
    user_text = st.text_area(
        "최근 읽은 책이나 키워드를 입력하세요",
        placeholder="예) 달러구트 꿈 백화점\n예) 인간관계, 위로, 성장",
        height=150
    )
    if st.button("추천 생성"):
        if not user_text.strip():
            st.warning("한 줄 이상 입력해 주세요.")
        else:
            st.success(f"입력하신 키워드 기반 추천 결과를 준비했습니다: {user_text}")
            # 여기서 간단히 랜덤 유형 매칭
            result = random.choice(list(TYPES.keys()))
            st.info(f"추천 유형: **{result}**")
            st.caption(TYPES[result])

# -------------------------
# 네이버 API 기반 추천
# -------------------------
elif menu == "키워드 온라인 추천(네이버)":
    st.header("🌐 네이버 도서 기반 온라인 추천")
    keyword = st.text_input("키워드를 입력하세요", placeholder="예) 심리, 성장, 철학")
    k = st.slider("추천 개수", 3, 10, 6, key="naver_k")

    if st.button("네이버 추천 보기"):
        if not keyword.strip():
            st.warning("키워드를 입력해주세요.")
        else:
            recs = recommend_by_naver_books(keyword, max_results=k)
            if not recs:
                st.info("관련 도서를 찾지 못했습니다.")
            else:
                for b in recs:
                    img_html = f"<img src='{b['image']}' width='80'>" if b.get("image") else ""
                    pub = f"{b['pubdate']} • {b['publisher']}" if b.get("publisher") or b.get("pubdate") else ""
                    st.markdown(
                        f"<div style='margin-bottom:15px;'>"
                        f"{img_html}<br>"
                        f"<b>{b['title']}</b><br>"
                        f"{b['author']}<br><span style='font-size:12px;color:gray'>{pub}</span><br>"
                        f"<span style='font-size:12px;color:gray'>{b.get('description', '')}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

# -------------------------
# 푸터
# -------------------------
st.write("---")
st.caption("ⓒ 독서 성향 10유형 · Streamlit Demo · 네이버 도서 API 연동")
