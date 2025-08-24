import streamlit as st
import requests

st.title("📚 도서 추천 앱")

# 사용자 입력
keyword = st.text_input("관심 있는 키워드를 입력하세요 (예: 행정학, 심리학, 소설, 에세이)")

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
