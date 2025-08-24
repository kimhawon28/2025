import streamlit as st
from typing import Dict, List, Tuple
import random

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
/* 기본 배경과 본문 텍스트 (흰색) */
.stApp {
    background-color: #26365c;
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
}

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

/* ===== 메인 영역 위젯 텍스트: 흰색 ===== */
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

/* select 드롭다운 옵션(팝오버) 검정 */
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

/* 사이드바의 라디오 선택지 강조 */
section[data-testid="stSidebar"] [data-baseweb="radio"] label {
    font-weight: 600 !important;
}
</style>

<!-- 배경 음악: 베토벤 월광 소나타 1악장 (자동재생/반복) -->
<audio autoplay loop style="display:none">
  <source src="https://upload.wikimedia.org/wikipedia/commons/0/0e/Beethoven_Moonlight_1st_movement.ogg" type="audio/ogg">
</audio>
""", unsafe_allow_html=True)

# ==============================
# 데이터 정의 (10유형 + 책 데이터)
# ==============================
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

BOOKS: Dict[str, List[Dict]] = {
    "감성 몰입형": [
        {"title": "아몬드", "author": "손원평", "reason": "섬세한 감정선과 성장."},
        {"title": "연의 편지", "author": "조현아", "reason": "잔잔한 위로와 울림."},
        {"title": "작별인사", "author": "김영하", "reason": "따뜻함과 상실의 여운."},
        {"title": "달러구트 꿈 백화점", "author": "이미예", "reason": "아늑하고 몽환적인 위로."},
        {"title": "우리가 빛의 속도로 갈 수 없다면", "author": "김초엽", "reason": "다정한 SF의 위로."},
    ],
    "지식 탐구형": [
        {"title": "이기적 유전자", "author": "리처드 도킨스", "reason": "진화론의 시각 확대."},
        {"title": "코스모스", "author": "칼 세이건", "reason": "우주와 인간에 대한 경이."},
        {"title": "사피엔스", "author": "유발 하라리", "reason": "인류의 거대한 서사."},
        {"title": "총, 균, 쇠", "author": "재레드 다이아몬드", "reason": "문명의 격차를 해부."},
        {"title": "생각에 관한 생각", "author": "대니얼 카너먼", "reason": "사고 체계의 이해."},
    ],
    "현실 적용형": [
        {"title": "원씽", "author": "게리 켈러", "reason": "핵심에 집중하는 법."},
        {"title": "아주 작은 습관의 힘", "author": "제임스 클리어", "reason": "작은 변화의 누적."},
        {"title": "린 스타트업", "author": "에릭 리스", "reason": "사업/프로젝트 실행."},
        {"title": "초집중", "author": "니르 에얄", "reason": "주의관리와 실천."},
        {"title": "하버드 상위 1%의 비밀", "author": "정주영", "reason": "실전 생산성 팁."},
    ],
    "스토리 몰입형": [
        {"title": "해리 포터", "author": "J.K. 롤링", "reason": "성장과 우정, 모험."},
        {"title": "나미야 잡화점의 기적", "author": "히가시노 게이고", "reason": "따뜻한 연결의 서사."},
        {"title": "미드나잇 라이브러리", "author": "매트 헤이그", "reason": "다중 가능성의 이야기."},
        {"title": "종의 기원", "author": "정유정", "reason": "몰입감 있는 전개."},
        {"title": "바람의 이름", "author": "패트릭 로스퍼스", "reason": "장대한 판타지 서사."},
    ],
    "철학 사색형": [
        {"title": "무엇이 옳은가", "author": "마이클 샌델", "reason": "정의와 윤리의 질문."},
        {"title": "니체의 말", "author": "니시모토 켄", "reason": "사유의 자극."},
        {"title": "존재의 세 가지 거짓말", "author": "김영민", "reason": "일상 속 사유 확장."},
        {"title": "철학 카페에서 문학 읽기", "author": "탁석산", "reason": "문학을 통한 성찰."},
        {"title": "소크라테스 익스프레스", "author": "에릭 와이너", "reason": "여행하는 철학."},
    ],
    "트렌드 캐처형": [
        {"title": "불편한 편의점", "author": "김호연", "reason": "대중적 인기와 울림."},
        {"title": "하얼빈", "author": "김훈", "reason": "화제성 높은 서사."},
        {"title": "파친코", "author": "이민진", "reason": "드라마틱한 화제작."},
        {"title": "역행자", "author": "자청", "reason": "실전 자기계발 화제."},
        {"title": "아주 희미한 빛으로", "author": "정세랑", "reason": "요즘 감성의 문장."},
    ],
    "힐링 독서형": [
        {"title": "여행의 이유", "author": "김영하", "reason": "여정 속 위로."},
        {"title": "보건교사 안은영", "author": "정세랑", "reason": "경쾌하고 상냥한 세계."},
        {"title": "언어의 온도", "author": "이기주", "reason": "따뜻한 문장들."},
        {"title": "우리가 빛의 속도로 갈 수 없다면", "author": "김초엽", "reason": "다정한 SF의 위로."},
        {"title": "죽고 싶지만 떡볶이는 먹고 싶어", "author": "백세희", "reason": "진솔한 공감."},
    ],
    "실험적 독서형": [
        {"title": "1Q84", "author": "무라카미 하루키", "reason": "형식과 세계의 변주."},
        {"title": "기나긴 하루", "author": "가즈오 이시구로", "reason": "문체 실험과 여백."},
        {"title": "보트", "author": "남수연", "reason": "낯선 시선의 서사."},
        {"title": "말들의 풍경", "author": "이문재", "reason": "시적 이미지의 실험."},
        {"title": "설국", "author": "가와바타 야스나리", "reason": "정제된 미학."},
    ],
    "사회 참여형": [
        {"title": "팩트풀니스", "author": "한스 로슬링", "reason": "데이터로 보는 세상."},
        {"title": "난장이가 쏘아올린 작은 공", "author": "조세희", "reason": "불평등의 기록."},
        {"title": "우리는 왜 분노하는가", "author": "마사 누스바움", "reason": "감정과 정의."},
        {"title": "정의란 무엇인가", "author": "마이클 샌델", "reason": "공정과 정의의 기준."},
        {"title": "그 많던 싱아는 누가 다 먹었을까", "author": "박완서", "reason": "시대와 생활의 증언."},
    ],
    "가벼운 즐김형": [
        {"title": "달러구트 꿈 백화점 2", "author": "이미예", "reason": "편하게 이어 읽기."},
        {"title": "미움받을 용기 (만화판)", "author": "기시미 이치로", "reason": "쉽고 빠른 몰입."},
        {"title": "어느 날 공주가 되어버렸다", "author": "플루토", "reason": "라이트한 판타지."},
        {"title": "최애의 아이 (코믹스)", "author": "아카사카 아카", "reason": "팝하고 가벼움."},
        {"title": "김비서가 왜 그럴까(소설)", "author": "정경윤", "reason": "드라마틱 로맨스."},
    ],
}

# ==============================
# 질문(5문항) 및 매핑
# ==============================
QUESTIONS: List[Dict] = [
    {
        "text": "책을 읽을 때 가장 기대하는 건 무엇인가요?",
        "options": {
            "감동": ["감성 몰입형", "힐링 독서형"],
            "지식": ["지식 탐구형"],
            "실용성": ["현실 적용형"],
            "재미": ["가벼운 즐김형", "스토리 몰입형"],
        },
    },
    {
        "text": "다 읽고 난 뒤 어떤 기분을 원하나요?",
        "options": {
            "위로": ["힐링 독서형", "감성 몰입형"],
            "뿌듯함": ["현실 적용형"],
            "깨달음": ["지식 탐구형", "철학 사색형"],
            "여운": ["스토리 몰입형", "철학 사색형"],
        },
    },
    {
        "text": "어떻게 책을 고르나요?",
        "options": {
            "유행/베스트셀러": ["트렌드 캐처형"],
            "필요에 따라": ["현실 적용형"],
            "감정 상태에 따라": ["감성 몰입형", "힐링 독서형"],
            "그냥 끌려서": ["가벼운 즐김형", "실험적 독서형"],
        },
    },
    {
        "text": "선호하는 글 스타일은?",
        "options": {
            "서정적 문장": ["감성 몰입형", "힐링 독서형"],
            "간결한 정보": ["지식 탐구형", "현실 적용형"],
            "강렬한 서사": ["스토리 몰입형", "트렌드 캐처형"],
            "낯선 실험": ["실험적 독서형"],
        },
    },
    {
        "text": "요즘 더 끌리는 주제는?",
        "options": {
            "삶의 의미": ["철학 사색형"],
            "사회/역사": ["사회 참여형"],
            "성장/자기관리": ["현실 적용형"],
            "순수한 재미": ["가벼운 즐김형", "스토리 몰입형"],
        },
    },
]

# ==============================
# 유틸 & 로직
# ==============================

def score_types(answers: List[str]) -> Dict[str, int]:
    score: Dict[str, int] = {t: 0 for t in TYPES}
    for a, q in zip(answers, QUESTIONS):
        for t in q["options"].get(a, []):
            score[t] += 1
    return score


def best_types(score: Dict[str, int], topk: int = 2) -> List[Tuple[str, int]]:
    ranked = sorted(score.items(), key=lambda x: (-x[1], x[0]))
    return ranked[:topk]


def recommend_by_types(top_types: List[str], k: int = 6) -> List[Dict]:
    picks: List[Dict] = []
    pool: List[Dict] = []
    for t in top_types:
        pool.extend(BOOKS.get(t, []))
    random.shuffle(pool)
    seen = set()
    for b in pool:
        key = (b["title"], b["author"])
        if key in seen:
            continue
        picks.append(b)
        seen.add(key)
        if len(picks) >= k:
            break
    # 부족하면 전체에서 보충
    if len(picks) < k:
        others = sum(BOOKS.values(), [])
        random.shuffle(others)
        for b in others:
            key = (b["title"], b["author"])
            if key in seen:
                continue
            picks.append(b)
            seen.add(key)
            if len(picks) >= k:
                break
    return picks


def recommend_by_genre(genre_type: str, k: int = 5) -> List[Dict]:
    pool = BOOKS.get(genre_type, [])
    return random.sample(pool, k=min(k, len(pool))) if pool else []

# ==============================
# UI
# ==============================
with st.sidebar:
    st.title("📚 독서 추천")
    menu = st.radio("메뉴", ["홈", "성향 테스트", "장르별 추천", "내 리스트 기반(간단)"])
    st.caption("한글 10유형 기반 맞춤 추천")

# 추가 카드/보조 스타일 (보정)
st.markdown(
    """
<style>
.small-note {font-size: 0.9rem; color: #dddddd;}
.card {padding: 1rem; border: 1px solid rgba(255,255,255,0.12); border-radius: 1rem;}
</style>
""",
    unsafe_allow_html=True,
)

st.title("📖✨ 독서 성향 기반 책 추천 웹앱")

# 홈
if menu == "홈":
    st.header("앱 소개")
    st.write("간단한 설문으로 독서 성향을 파악하고, 유형별로 맞춤 도서를 추천해 드려요.")

    cols = st.columns(3)
    with cols[0]:
        st.subheader("① 성향 테스트")
        st.write("5문항 설문 → 상위 2개 유형 도출 → 맞춤 추천")
    with cols[1]:
        st.subheader("② 장르별 추천")
        st.write("원하는 유형(분위기)에 맞는 추천 리스트")
    with cols[2]:
        st.subheader("③ 내 리스트 기반")
        st.write("최근 읽은 책 키워드로 간단 추천")

# 성향 테스트
elif menu == "성향 테스트":
    st.header("🧭 독서 성향 테스트")
    answers: List[str] = []
    for i, q in enumerate(QUESTIONS, 1):
        ans = st.radio(
            f"Q{i}. {q['text']}",
            list(q["options"].keys()),
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
            cols = st.columns(len(top2))
            for col, (t, v) in zip(cols, top2):
                with col:
                    st.subheader(f"{t}")
                    st.caption(TYPES[t])
                    st.markdown(f"**점수**: {v}")

            st.divider()
            st.subheader("맞춤 추천")
            recs = recommend_by_types(top_names, k=6)
            for b in recs:
                st.markdown(
                    f"<div class='card'><b>{b['title']}</b> · {b['author']}<br><span class='small-note'>추천 이유: {b['reason']}</span></div>",
                    unsafe_allow_html=True,
                )

# 장르별(유형 감성) 추천
elif menu == "장르별 추천":
    st.header("🎯 장르/유형 감성으로 추천 받기")
    choice = st.selectbox("원하는 분위기/유형을 골라주세요", list(TYPES.keys()))
    k = st.slider("추천 개수", 3, 10, 5)
    if st.button("추천 보기"):
        recs = recommend_by_genre(choice, k=k)
        if not recs:
            st.info("해당 유형 데이터가 아직 없어요. 다른 유형을 선택해 주세요.")
        for b in recs:
            st.markdown(
                f"<div class='card'><b>{b['title']}</b> · {b['author']}<br><span class='small-note'>추천 이유: {b['reason']}</span></div>",
                unsafe_allow_html=True,
            )

# 간단: 내 리스트 기반 추천(키워드 매칭)
elif menu == "내 리스트 기반(간단)":
    st.header("📝 최근 읽은 책/키워드 기반 간단 추천")
    text = st.text_area(
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

            # 매우 단순한 키워드 → 유형 매핑 규칙 (원하면 확장 가능)
            key2type = {
                "위로": "힐링 독서형",
                "감동": "감성 몰입형",
                "철학": "철학 사색형",
                "사회": "사회 참여형",
                "역사": "사회 참여형",
                "베스트": "트렌드 캐처형",
                "유행": "트렌드 캐처형",
                "실용": "현실 적용형",
                "자기계발": "현실 적용형",
                "정보": "지식 탐구형",
                "과학": "지식 탐구형",
                "재미": "가벼운 즐김형",
                "소설": "스토리 몰입형",
                "시": "실험적 독서형",
            }

            votes = {t: 0 for t in TYPES}
            matched = []
            for tok in tokens:
                for kword, tname in key2type.items():
                    if kword in tok:
                        votes[tname] += 1
                        matched.append((tok, tname))

            # 최다 득표 유형 선정(동점 시 임의 선택)
            top = sorted(votes.items(), key=lambda x: (-x[1], x[0]))
            if top[0][1] == 0:
                st.info("키워드에서 뚜렷한 성향을 찾지 못했어요. 전체에서 골라 드릴게요.")
                picks = recommend_by_types(list(TYPES.keys()), k=k)
            else:
                max_vote = top[0][1]
                candidates = [t for t, v in top if v == max_vote]
                chosen = random.choice(candidates)
                st.caption(f"키워드 매칭으로 선택된 유형: **{chosen}** (득표 {max_vote})")
                if matched:
                    with st.expander("키워드 매칭 로그 보기"):
                        for m in matched:
                            st.write("-", m[0], "→", m[1])
                picks = recommend_by_genre(chosen, k=k)

            st.subheader("추천 결과")
            for b in picks:
                st.markdown(
                    f"<div class='card'><b>{b['title']}</b> · {b['author']}<br><span class='small-note'>추천 이유: {b['reason']}</span></div>",
                    unsafe_allow_html=True,
                )

# 푸터
st.write(" ")
st.caption("ⓒ 독서 성향 10유형 · Streamlit Demo · 로컬 데이터 기반 예시")
