import streamlit as st
import requests

st.set_page_config(page_title="독서 성향 테스트 & 도서 검색", layout="centered")
st.title("📚 독서 성향 테스트 & 도서 검색 앱")

# --- 탭 생성 ---
tab1, tab2 = st.tabs(["독서 성향 테스트", "도서 검색"])

# --- 탭 1: 독서 성향 테스트 ---
with tab1:
    st.header("📋 독서 성향 테스트")
    st.write("각 질문에서 자신에게 가까운 선택지를 골라주세요.")

    q1 = st.radio("1. 책을 읽을 때 나는?", 
                  ["감정을 크게 느끼는 편이다", "지식을 얻는 것이 더 좋다"])
    q2 = st.radio("2. 나는?", 
                  ["철학적이고 사색적인 편", "실용적이고 현실적인 편"])
    q3 = st.radio("3. 책을 고를 때?", 
                  ["베스트셀러/트렌드를 본다", "내 취향대로 고른다"])
    q4 = st.radio("4. 독서 목적은?", 
                  ["마음을 위로받고 치유", "지식과 정보 습득"])
    q5 = st.radio("5. 선호하는 책 스타일은?", 
                  ["스토리 몰입, 소설", "실용적/자기계발"])

    # --- 결과 버튼 ---
    if st.button("결과 보기"):
        # 점수 계산
        score = 0
        if q1 == "감정을 크게 느끼는 편이다": score += 1
        else: score += 2
        if q2 == "철학적이고 사색적인 편": score += 1
        else: score += 2
        if q3 == "베스트셀러/트렌드를 본다": score += 1
        else: score += 2
        if q4 == "마음을 위로받고 치유": score += 1
        else: score += 2
        if q5 == "스토리 몰입, 소설": score += 1
        else: score += 2

        # 성향 매핑
        if score <= 5:
            personality = "힐링 독서형"
        elif score == 6:
            personality = "감성 몰입형"
        elif score == 7:
            personality = "철학 사색형"
        elif score == 8:
            personality = "사회 참여형"
        elif score == 9:
            personality = "트렌드 캐처형"
        elif score == 10:
            personality = "현실 적용형"
        elif score == 11:
            personality = "지식 탐구형"
        elif score == 12:
            personality = "가벼운 즐김형"
        elif score == 13:
            personality = "스토리 몰입형"
        else:
            personality = "실험적 독서형"

        descriptions = {
            "힐링 독서형": "마음을 위로받고 치유받는 독서를 선호해요.",
            "감성 몰입형": "감정을 자극하는 문학 작품을 즐겨요.",
            "철학 사색형": "깊은 사유와 철학적 텍스트를 탐구해요.",
            "사회 참여형": "사회 문제와 역사에 관심이 많아요.",
            "트렌드 캐처형": "베스트셀러와 최신 화제작을 따라가요.",
            "현실 적용형": "실용적이고 자기계발에 도움 되는 책을 좋아해요.",
            "지식 탐구형": "정보, 과학, 지식을 탐구하는 독서가 즐거워요.",
            "가벼운 즐김형": "재미와 오락을 위한 가벼운 책을 즐겨요.",
            "스토리 몰입형": "몰입감 있는 소설을 선호해요.",
            "실험적 독서형": "실험적인 텍스트에 매력을 느껴요."
        }

        st.subheader(f"🔹 당신의 독서 성향: {personality}")
        st.write(descriptions.get(personality, "당신의 독서 스타일을 찾는 중이에요."))

        book_recommendations = {
            "힐링 독서형": ["책1", "책2", "책3"],
            "감성 몰입형": ["책4", "책5", "책6"],
            "철학 사색형": ["책7", "책8", "책9"],
            "사회 참여형": ["책10", "책11", "책12"],
            "트렌드 캐처형": ["책13", "책14", "책15"],
            "현실 적용형": ["책16", "책17", "책18"],
            "지식 탐구형": ["책19", "책20", "책21"],
            "가벼운 즐김형": ["책22", "책23", "책24"],
            "스토리 몰입형": ["책25", "책26", "책27"],
            "실험적 독서형": ["책28", "책29", "책30"]
        }

        st.subheader("📖 추천 도서")
        for b in book_recommendations[personality]:
            st.write(f"- {b}")

# --- 탭 2: 도서 검색 ---
with tab2:
    st.header("🔎 도서 검색")
    keyword = st.text_input("검색 키워드를 입력하세요 (예: 소설, 자기계발, 경제)")
    
if keyword:
    url = "https://openapi.naver.com/v1/search/book.json"
    headers = {
        "X-Naver-Client-Id": "ZpjV3RrEyIOBNZ0CkqPM",        # 🔑 발급받은 Client ID
        "X-Naver-Client-Secret": "Yv857utsaI" # 🔑 발급받은 Client Secret
    }
    params = {"query": keyword, "display": 10}  # 최대 10권 추천

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        books = response.json()["items"]

        if len(books) > 0:
            for book in books:
                st.image(book["image"], width=120)  # 책 표지
                # <b>태그 제거
                title = book["title"].replace("<b>", "").replace("</b>", "")
                st.subheader(title)
                st.write(f"저자: {book['author']}")
                st.write(f"출판사: {book['publisher']}")
                st.write(f"출판일: {book['pubdate']}")
                st.write(f"[상세보기]({book['link']})")
                st.markdown("---")
        else:
            st.write("😥 관련 도서를 찾을 수 없습니다.")
    else:
        st.error("API 요청 실패. Client ID/Secret을 확인하세요.")
