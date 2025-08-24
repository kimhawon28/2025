import streamlit as st
import random
import requests
from typing import List, Dict

# ==============================
# 구글북스 API 함수 (썸네일 포함)
# ==============================
def recommend_by_keyword_api(keyword: str, max_results: int = 5):
    """
    Google Books API에서 키워드 기반 책 추천 (썸네일 포함)
    """
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": keyword, "maxResults": max_results, "langRestrict": "ko"}
    resp = requests.get(url, params=params)

    if resp.status_code != 200:
        return []

    items = resp.json().get("items", [])
    recs = []
    for it in items:
        info = it.get("volumeInfo", {})
        recs.append({
            "title": info.get("title", "제목 없음"),
            "authors": ", ".join(info.get("authors", ["저자 미상"])),
            "description": info.get("description", "설명 없음"),
            "thumbnail": info.get("imageLinks", {}).get("thumbnail", None)
        })
    return recs

# ==============================
# CSS (네이비 테마 + 흰 글씨 + 둥근 폰트)
# ==============================
st.markdown("""
    <style>
    body, .stApp {
        background-color: #26365c;
        color: white;
        font-family: 'Pretendard', sans-serif;
    }
    .stTextInput input, .stTextArea textarea {
        color: black !important;
        background-color: white !important;
        border-radius: 10px;
        padding: 8px;
    }
    .stSelectbox div, .stRadio div {
        color: white !important;
    }
    .card {
        background: rgba(255,255,255,0.1);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 15px;
        display: flex;
        gap: 12px;
        align-items: flex-start;
    }
    .card img {
        border-radius: 8px;
        max-width: 80px;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================
# 예시 데이터 (간단)
# ==============================
TYPES = {
    "감성 몰입형": "감정 이입이 깊고 문학적 글을 좋아하는 유형",
    "철학 사색형": "철학과 사색을 즐기며 삶의 의미를 탐구",
    "사회 참여형": "사회 문제와 역사에 관심이 많은 유형",
    "트렌드 캐처형": "최신 베스트셀러와 유행을 따르는 유형",
    "현실 적용형": "자기계발과 실용서를 좋아하는 유형",
    "지식 탐구형": "과학, 지식, 정보를 파고드는 유형",
    "가벼운 즐김형": "짧고 재미있는 책을 선호하는 유형",
    "스토리 몰입형": "소설과 이야기 속에 빠지는 유형",
    "실험적 독서형": "시, 실험적 글쓰기를 선호하는 유형",
    "힐링 독서형": "위로와 치유를 얻고 싶어하는 유형",
}

QUESTIONS = [
    {"text": "책에서 가장 중요한 것은?", 
     "options": {"스토리의 재미": "스토리 몰입형", "감정적 울림": "감성 몰입형", "정보/지식": "지식 탐구형"}},
    {"text": "책을 읽는 이유는?", 
     "options": {"현실 적용": "현실 적용형", "세상 이해": "사회 참여형", "위로와 치유": "힐링 독서형"}},
    {"text": "선호하는 책 분위기?", 
     "options": {"철학적/사색적": "철학 사색형", "유행/베스트셀러": "트렌드 캐처형", "가볍고 유쾌한": "가벼운 즐김형"}},
]

def score_types(answers: List[str]) -> Dict[str, int]:
    scores = {t: 0 for t in TYPES}
    for a in answers:
        if a in TYPES:
            scores[a] += 1
    return scores

def best_types(scores: Dict[str, int], topk: int = 2):
    return sorted(scores.items(), key=lambda x: -x[1])[:topk]

def recommend_by_types(type_names: List[str], k=5):
    recs = []
    for t in type_names:
        for i in range(k):
            recs.append({
                "title": f"{t} 도서 {i+1}",
                "author": "저자 미상",
                "reason": f"{t} 성향에 맞는 책"
            })
    random.shuffle(recs)
    return recs[:k]

def recommend_by_genre(type_name: str, k=5):
    return recommend_by_types([type_name], k)

# ==============================
# 메인 UI
# ==============================
st.sidebar.title("📚 메뉴")
menu = st.sidebar.radio("이동하기", ["성향 테스트", "장르별 추천", "내 리스트 기반(간단)", "키워드 온라인 추천"])

# 성향 테스트
if menu == "성향 테스트":
    st.header("🧭 독서 성향 테스트")
    answers: List[str] = []
    for i, q in enumerate(QUESTIONS, 1):
        ans = st.radio(
            f"Q{i}. {q['text']}",
            list(q["options"].values()),
            index=None,
            key=f"q_{i}",
        )
        answers.append(ans if ans else "")

    if st.button("결과 보기 ✨", type="primary"):
        if any(a == "" for a in answers):
            st.warning("모든 문항에 답해주세요.")
        else:
            s = score_types(answers)
            top2 = best_types(s, topk=2)
            top_names = [t for t, _ in top2]

            st.success("당신의 독서 유형")
            for t, v in top2:
                st.subheader(f"{t}")
                st.caption(TYPES[t])
                st.markdown(f"**점수**: {v}")

            st.divider()
            st.subheader("맞춤 추천")
            recs = recommend_by_types(top_names, k=6)
            for b in recs:
                st.markdown(
                    f"<div class='card'><div><b>{b['title']}</b> · {b['author']}<br><span class='small-note'>{b['reason']}</span></div></div>",
                    unsafe_allow_html=True,
                )

# 장르별 추천
elif menu == "장르별 추천":
    st.header("🎯 장르/유형 감성으로 추천 받기")
    choice = st.selectbox("원하는 분위기/유형을 골라주세요", list(TYPES.keys()))
    k = st.slider("추천 개수", 3, 10, 5)
    if st.button("추천 보기"):
        recs = recommend_by_genre(choice, k=k)
        for b in recs:
            st.markdown(
                f"<div class='card'><div><b>{b['title']}</b> · {b['author']}<br><span class='small-note'>{b['reason']}</span></div></div>",
                unsafe_allow_html=True,
            )

# 내 리스트 기반
elif menu == "내 리스트 기반(간단)":
    st.header("📝 최근 읽은 책/키워드 기반 간단 추천")
    user_text = st.text_area(
        "최근 읽은 책/키워드 입력",
        placeholder="예) 달러구트 꿈 백화점\n예) 인간관계, 위로, 성장",
        height=150
    )
    k = st.slider("추천 개수", 3, 10, 5, key="mine_k")

    if st.button("추천 생성"):
        if not user_text.strip():
            st.warning("한 줄 이상 입력해 주세요.")
        else:
            tokens = [t.strip().lower() for t in user_text.splitlines() if t.strip()]

            key2type = {"위로": "힐링 독서형", "감동": "감성 몰입형", "철학": "철학 사색형",
                        "사회": "사회 참여형", "역사": "사회 참여형", "베스트": "트렌드 캐처형",
                        "유행": "트렌드 캐처형", "실용": "현실 적용형", "자기계발": "현실 적용형",
                        "정보": "지식 탐구형", "과학": "지식 탐구형", "재미": "가벼운 즐김형",
                        "소설": "스토리 몰입형", "시": "실험적 독서형"}

            votes = {t: 0 for t in TYPES}
            for tok in tokens:
                for kword, tname in key2type.items():
                    if kword in tok:
                        votes[tname] += 1

            top = sorted(votes.items(), key=lambda x: (-x[1], x[0]))
            if top[0][1] == 0:
                st.info("키워드에서 성향을 찾지 못했어요. 전체에서 랜덤 추천합니다.")
                picks = recommend_by_types(list(TYPES.keys()), k=k)
            else:
                chosen = top[0][0]
                st.caption(f"선택된 유형: **{chosen}**")
                picks = recommend_by_genre(chosen, k=k)

            st.subheader("추천 결과")
            for b in picks:
                st.markdown(
                    f"<div class='card'><div><b>{b['title']}</b> · {b['author']}<br><span class='small-note'>{b['reason']}</span></div></div>",
                    unsafe_allow_html=True,
                )

# 키워드 온라인 추천
elif menu == "키워드 온라인 추천":
    st.header("🌐 키워드 기반 온라인 추천 (Google Books)")
    keyword = st.text_input("키워드를 입력하세요", placeholder="예) 인공지능, 철학, 사랑")
    k = st.slider("추천 개수", 3, 10, 5, key="online_k")

    if st.button("온라인 추천 보기"):
        if not keyword.strip():
            st.warning("키워드를 입력해주세요.")
        else:
            recs = recommend_by_keyword_api(keyword, max_results=k)
            if not recs:
                st.info("관련 도서를 찾지 못했습니다.")
            else:
                for b in recs:
                    thumb_html = f"<img src='{b['thumbnail']}' width='80'>" if b['thumbnail'] else ""
                    st.markdown(
                        f"<div class='card'>{thumb_html}<div><b>{b['title']}</b><br>"
                        f"저자: {b['authors']}<br><span class='small-note'>{b['description']}</span></div></div>",
                        unsafe_allow_html=True,
                    )

# 푸터
st.write(" ")
st.caption("ⓒ 독서 성향 10유형 · Streamlit Demo · Google Books API 적용")
