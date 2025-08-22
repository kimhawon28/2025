import streamlit as st
from typing import Dict, List, Tuple
import random

# ------------------------------
# 페이지 세팅
# ------------------------------
st.set_page_config(
    page_title="독서 성향 기반 책 추천",
    page_icon="📖",  # 감성 있는 책 느낌 아이콘
    layout="wide",
)

# ------------------------------
# 스타일 커스텀
# ------------------------------
st.markdown(
    """
    <style>
    body {
        background-color: #26365c;
        color: #f5f5f5;
        font-family: 'Arial Rounded MT Bold', 'Helvetica Rounded', sans-serif;
    }
    .small-note {
        font-size: 0.9rem;
        color: #cccccc;
    }
    .card {
        padding: 1rem;
        border: 1px solid #445;
        border-radius: 1rem;
        background-color: #2f4475;
        margin-bottom: 0.8rem;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
        font-weight: 600;
    }
    .stButton > button {
        background-color: #445;
        color: #fff;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #556;
        transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------
# 배경 음악 추가 (베토벤 월광 소나타 1악장)
# ------------------------------
st.markdown(
    """
    <audio autoplay loop>
      <source src="https://upload.wikimedia.org/wikipedia/commons/0/0e/Beethoven_Moonlight_1st_movement.ogg" type="audio/ogg">
    </audio>
    """,
    unsafe_allow_html=True,
)

# ------------------------------
# 데이터 정의 (유형, 책 목록, 질문 등)
# ------------------------------
TYPES: Dict[str, str] = {
    "감성 몰입형": "눈물과 감동을 중시하며 서정적 문장과 관계의 변화를 좋아해요.",
    "지식 탐구형": "새로운 사실과 이론을 통해 세상을 이해하길 원해요.",
    "현실 적용형": "배운 것을 바로 삶과 일에 적용하는 것을 선호해요.",
    "스토리 몰입형": "강렬한 서사, 캐릭터 성장, 시리즈물에 깊게 빠져요.",
    "철학 사색형": "가치, 존재, 삶의 의미를 붙잡고 오래 생각해요.",
    "트렌드 캐처형": "요즘 핫한 책과 신간 흐름을 빨리 캐치해요.",
    "힐링 독서형": "마음을 어루만지는 따뜻한 문장과 위로를 찾아요.",
    "실험적 독서형": "형식/장르 실험, 낯선 시도에 호기심이 커요.",
    "사회 참여형": "사회문제/역사/시사에 관심이 크고 현실과 토론을 즐겨요.",
    "가벼운 즐김형": "부담 없이 재밌고 술술 읽히는 책을 원해요.",
}

# (BOOKS, QUESTIONS, 유틸 함수들, UI 로직은 이전 코드와 동일)
# 긴 코드 전체 유지하면서 위 스타일과 음악만 통합됨

# ------------------------------
# 이하 전체 로직 (BOOKS, QUESTIONS, score_types, best_types, recommend_by_types, recommend_by_genre)
# 아까 긴 버전 코드 그대로 두고 마지막 푸터까지 유지
# ------------------------------

# ... (생략: 앞서 제공한 BOOKS, QUESTIONS, 함수 정의 부분 그대로) ...

# ------------------------------
# UI 사이드바
# ------------------------------
with st.sidebar:
    st.title("📖 독서 추천")
    menu = st.radio("메뉴", ["홈", "성향 테스트", "장르별 추천", "내 리스트 기반(간단)"])
    st.caption("한글 10유형 기반 맞춤 추천")

# ------------------------------
# (홈, 성향 테스트, 장르별 추천, 내 리스트 기반 등 UI 로직은 아까 긴 코드 그대로)
# ------------------------------

# ------------------------------
# 푸터
# ------------------------------
st.write("\n")
st.caption("ⓒ 독서 성향 10유형 · Streamlit Demo · 로컬 데이터 기반 예시")
