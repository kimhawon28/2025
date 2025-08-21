import streamlit as st

# MBTI별 추천 직업 데이터
mbti_jobs = {
    "ISTJ": ["회계사", "공무원", "데이터 분석가"],
    "ISFJ": ["교사", "간호사", "사회복지사"],
    "INFJ": ["심리상담사", "작가", "교수"],
    "INTJ": ["엔지니어", "과학자", "전략 컨설턴트"],
    "ISTP": ["파일럿", "수사관", "메카닉"],
    "ISFP": ["디자이너", "작곡가", "사진작가"],
    "INFP": ["작가", "상담사", "예술가"],
    "INTP": ["연구원", "개발자", "철학자"],
    "ESTP": ["기업가", "영업직", "스포츠 선수"],
    "ESFP": ["배우", "방송인", "이벤트 플래너"],
    "ENFP": ["광고 기획자", "작가", "강연가"],
    "ENTP": ["벤처기업가", "변호사", "정치가"],
    "ESTJ": ["경영자", "군인", "프로젝트 매니저"],
    "ESFJ": ["간호사", "HR 담당자", "교사"],
    "ENFJ": ["리더십 코치", "교사", "홍보 담당자"],
    "ENTJ": ["CEO", "변호사", "정치가"]
}

# Streamlit UI
st.title("MBTI 기반 직업 추천 웹앱")
st.write("자신의 MBTI 유형을 선택하면 적합한 직업을 추천해드립니다!")

# MBTI 선택
mbti = st.selectbox("당신의 MBTI를 선택하세요:", list(mbti_jobs.keys()))

# 결과 출력
if mbti:
    st.subheader(f"✨ {mbti} 유형에게 추천하는 직업")
    for job in mbti_jobs[mbti]:
        st.write(f"- {job}")
