import streamlit as st
import requests

st.set_page_config(page_title="책과 친해지기", layout="centered")
st.title("📚 책과 친해지기")

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
                  ["스토리 몰입", "실용적/자기계발"])
    q6 = st.radio("6. 책을 고를 때 가장 먼저 보는 것은?", 
                  ["제목/표지", "추천/후기"])
    q7 = st.radio("7. 책을 읽을 때 나는 주로", 
                  ["처음부터 끝까지 차근차근 읽는다", "흥미 있는 부분만 골라서 읽는다"])

    # --- 결과 버튼 ---
    if st.button("결과 보기"):
        # 점수 계산
        score = 0
        if q1 == "감정을 크게 느끼는 편이다": score += 1
        else: score += 3
        if q2 == "실용적이고 현실적인 편": score += 1
        else: score += 2
        if q3 == "베스트셀러/트렌드를 본다": score += 1
        else: score += 3
        if q4 == "지식과 정보 습득": score += 1
        else: score += 2
        if q5 == "실용적/자기계발": score += 1
        else: score += 2
        if q6 == "추천/후기": score += 1
        else: score += 2
        if q7 == "흥미 있는 부분만 골라서 읽는다": score += 1
        else: score += 2

        # 성향 매핑
        if score <= 7:
            personality = "사회 참여형"
        elif score == 8:
            personality = "철학 사색형"
        elif score == 9:
            personality = "트렌드 캐처형"
        elif score == 10:
            personality = "현실 적용형"
        elif score == 11:
            personality = "가벼운 즐김형"
        elif score == 12:
            personality = "지식 탐구형"
        elif score == 13:
            personality = "감성 몰입형"
        elif score == 14:
            personality = "힐링 독서형"
        elif score == 15:
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

        st.subheader(f"🔹 당신의 독서 성향  : {personality}")
        st.write(descriptions.get(personality, "당신의 독서 스타일을 찾는 중이에요."))

        book_recommendations = {
            "힐링 독서형": ["언어의 온도 (말과 글에는 나름의 따뜻함과 차가움이 있다) - 이기주", "우리의 낙원에서 만나자 (이 계절을 함께 건너는 당신에게) - 하태완", "여름을 한 입 베어 물었더니 - 이꽃님"],
            "감성 몰입형": ["노르웨이의 숲 - 무라카미 하루키", "안녕이라 그랬어 - 김애란", "천 개의 파랑 - 천선란"],
            "철학 사색형": ["참을 수 없는 존재의 가벼움 - 밀란 쿤데라", "쇼펜하우어의 인생 수업 (살아갈 힘을 주는 쇼펜하우어 아포리즘) - 쇼펜하우어", "데미안 - 헤르만헤세"],
            "사회 참여형": ["빅터 프랭클의 죽음의 수용소에서 - 빅터 프랭클", "하얼빈 - 김훈", "법과 사회와 인권 - 안경환"],
            "트렌드 캐처형": ["모순 - 양귀자", "첫 여름 완주 - 김금희", "혼모노 - 성해나"],
            "현실 적용형": ["원씽(The One Thing) (복잡한 세상을 이기는 단순함의 힘) - 게리 켈러, 제이 파파산", "말 그릇 (비울수록 사람을 더 채우는) - 김윤나", "퓨처 셀프 (현재와 미래가 달라지는 놀라운 혁명) - 벤저민 하디"],
            "지식 탐구형": ["넛지 (복잡한 세상에서 똑똑한 선택을 이끄는 힘) - 리처드 탈러, 캐스 선스타인", "총 균 쇠 - 재레드 다이아몬드", "코스모스 - 칼 세이건"],
            "가벼운 즐김형": ["길모퉁이에서 만난 사람 - 양귀자", "사서함 110호의 우편물 - 이동우", "외계인이 인류를 멸망시킨대 - 박대겸"],
            "스토리 몰입형": ["파과 - 구병모", "나는 소망한다 내게 금지된 것을 - 양귀자", "광인 - 이혁진"],
            "실험적 독서형": ["구의 증명  - 최진영", "삼미 슈퍼스타즈의 마지막 팬클럽 - 박민규", "일인용 책 - 신해욱"]
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
