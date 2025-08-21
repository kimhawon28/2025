import streamlit as st
from PIL import Image
import requests
from streamlit_lottie import st_lottie

# --- 직업 데이터 + 이미지 URL ---
mbti_jobs = {
    "ISTJ": [("회계사", "https://cdn-icons-png.flaticon.com/512/3135/3135673.png"),
             ("공무원", "https://cdn-icons-png.flaticon.com/512/1903/1903226.png"),
             ("데이터 분석가", "https://cdn-icons-png.flaticon.com/512/4359/4359963.png")],
    "ENFP": [("광고 기획자", "https://cdn-icons-png.flaticon.com/512/1995/1995574.png"),
             ("작가", "https://cdn-icons-png.flaticon.com/512/1995/1995531.png"),
             ("강연가", "https://cdn-icons-png.flaticon.com/512/1087/1087840.png")],
    "INTP": [("연구원", "https://cdn-icons-png.flaticon.com/512/3063/3063815.png"),
             ("개발자", "https://cdn-icons-png.flaticon.com/512/3296/3296464.png"),
             ("철학자", "https://cdn-icons-png.flaticon.com/512/3845/3845825.png")]
}

# --- Lottie 애니메이션 불러오기 ---
def load_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://assets4.lottiefiles.com/packages/lf20_t24tpvcu.json"
lottie_animation = load_lottie(lottie_url)

# --- UI 시작 ---
st.set_page_config(page_title="MBTI Career Recommender", page_icon="✨", layout="wide")

st.title("🌟 MBTI 기반 직업 추천 웹앱 🌟")
st.write("자신의 **MBTI**를 선택하면, 멋진 직업들이 기다리고 있어요!")

# MBTI 선택
mbti = st.selectbox("👉 당신의 MBTI는?", list(mbti_jobs.keys()))

# Lottie 애니메이션
st_lottie(lottie_animation, height=200, key="career")

# 결과 출력
if mbti:
    st.subheader(f"✨ {mbti} 유형에게 어울리는 직업들 ✨")

    cols = st.columns(3)  # 3개씩 카드처럼 나열
    for idx, (job, img_url) in enumerate(mbti_jobs[mbti]):
        with cols[idx % 3]:
            st.image(img_url, width=100)
            st.markdown(f"### {job}")
            st.write("💡 이 직업은 당신의 강점을 살릴 수 있어요!")
            st.markdown("---")
