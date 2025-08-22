import streamlit as st
import random

# ------------------------------
# 기본 페이지 설정
# ------------------------------
st.set_page_config(page_title="📔 감성 독서 성향 테스트", layout="wide")

# ------------------------------
# 🎨 감성 네이비 테마 + 둥근 폰트 + 음악
# ------------------------------
st.markdown("""
<style>
/* 전체 배경 & 기본 글자 */
.stApp {
    background-color: #26365c;
    color: #e5e7eb;
    font-family: 'Gowun Dodum', 'Noto Sans KR', sans-serif;
}

/* 헤더 */
h1, h2, h3, h4 {
    color: #f0f4ff;
    font-weight: 700;
}

/* 카드 스타일 */
.card {
    background: #2f406d;
    padding: 1.2rem;
    border-radius: 15px;
    border: 1px solid #3b4d7a;
    box-shadow: 2px 4px 10px rgba(0,0,0,0.4);
    margin-bottom: 1rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 4px 8px 16px rgba(0,0,0,0.6);
}

/* 작은 설명 텍스트 */
.small-note {
    font-size: 0.85rem;
    color: #ccc;
}

/* 버튼 스타일 */
div.stButton > button {
    background-color: #445d9e;
    color: white;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    transition: background-color 0.2s ease;
}
div.stButton > button:hover {
    background-color: #5c74b8;
    color: white;
}
</style>

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap" rel="stylesheet">

<!-- 감성 책 이모지 제목 -->
<h1 style='text-align: center; font-family: "Jua", sans-serif;'>
📔 감성 독서 성향 테스트
</h1>

<!-- 🎶 배경 음악 (베토벤 월광 소나타 1악장) -->
<div style="text-align: center; margin: 20px 0;">
    <iframe width="0" height="0" src="https://www.youtube.com/embed/4Tr0otuiQuU?autoplay=1&loop=1&playlist=4Tr0otuiQuU" frameborder="0" allow="autoplay"></iframe>
    <p style="color:#aaa; font-size:0.8rem;">🎵 Beethoven - Moonlight Sonata (1st Movement)</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# 데이터: 독서 성향 유형 + 질문
# ------------------------------
reading_types = {
    "감성적 몰입형": ["죽고 싶지만 떡볶이는 먹고 싶어", "언어의 온도", "나미야 잡화점의 기적"],
    "지식 탐구형": ["사피엔스", "총 균 쇠", "이기적 유전자"],
    "스토리 중심형": ["해리포터", "데미안", "연금술사"],
    "현실 도피형": ["반지의 제왕", "나니아 연대기", "셜록 홈즈 전집"],
    "철학 사색형": ["차라투스트라는 이렇게 말했다", "무엇이 옳은가", "논어"],
    "실용 행동형": ["원씽", "아침형 인간", "성공하는 사람들의 7가지 습관"],
    "힐링 감상형": ["여행의 이유", "작별인사", "오늘도 무사히"],
    "사회 참여형": ["정의란 무엇인가", "보통의 존재", "돈의 속성"],
    "창의 상상형": ["오만과 편견과 좀비", "은하수를 여행하는 히치하이커를 위한 안내서", "이상한 나라의 앨리스"],
    "균형 조화형": ["코스모스", "시간의 역사", "위대한 개츠비"]
}

questions = [
    ("책을 읽을 때 가장 중요하게 생각하는 것은?", 
     ["감정이입", "지식 습득", "스토리 전개", "현실 탈출"]),
    ("당신은 책을 통해 무엇을 얻고 싶나요?", 
     ["위로와 공감", "새로운 사실", "흥미진진함", "사색의 시간"]),
    ("하루 끝에 읽고 싶은 책은?", 
     ["에세이", "과학서", "소설", "철학서"]),
    ("친구에게 추천하는 책은 주로?", 
     ["감성적인 책", "실용적인 책", "재미있는 책", "깊이 있는 책"]),
    ("책을 다 읽고 난 뒤 당신의 모습은?", 
     ["눈물이 난다", "메모를 정리한다", "상상을 이어간다", "세상을 다시 본다"])
]

# ------------------------------
# 설문 진행
# ------------------------------
st.subheader("📖 나의 독서 성향 찾기")

answers = []
for i, (q, opts) in enumerate(questions):
    choice = st.radio(f"Q{i+1}. {q}", opts, key=i)
    answers.append(choice)

if st.button("✨ 결과 보기"):
    score_map = {k:0 for k in reading_types.keys()}
    for ans in answers:
        if ans in ["감정이입", "위로와 공감", "에세이", "감성적인 책", "눈물이 난다"]:
            score_map["감성적 몰입형"] += 1
        if ans in ["지식 습득", "새로운 사실", "과학서", "실용적인 책", "메모를 정리한다"]:
            score_map["지식 탐구형"] += 1
        if ans in ["스토리 전개", "흥미진진함", "소설", "재미있는 책", "상상을 이어간다"]:
            score_map["스토리 중심형"] += 1
        if ans in ["현실 탈출", "사색의 시간", "철학서", "깊이 있는 책", "세상을 다시 본다"]:
            score_map["철학 사색형"] += 1

    sorted_types = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    top_type = sorted_types[0][0]

    st.markdown(f"""
    <div class='card'>
        <h2>✨ 당신의 독서 성향은 <b>{top_type}</b> 입니다!</h2>
        <p class='small-note'>이 성향을 가진 분들께 추천하는 책:</p>
        <ul>
    """, unsafe_allow_html=True)

    for book in reading_types[top_type]:
        st.markdown(f"<li>{book}</li>", unsafe_allow_html=True)

    st.markdown("</ul></div>", unsafe_allow_html=True)
