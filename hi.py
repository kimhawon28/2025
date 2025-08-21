# app.py
# -------------------------------------------------------------
# 감정 기반 책 추천 + 한줄 교훈 + MBTI 캐릭터 + 음악 매칭 + 독서 여정 지도
# 단일 파일 Flask 데모 (템플릿 내장)
# -------------------------------------------------------------
from flask import Flask, request, redirect, url_for, session, render_template_string
import random

app = Flask(__name__)
app.secret_key = "super-secret-key-change-me"

EMOTIONS = ["행복", "우울", "설렘", "답답", "분노", "평온"]
MBTIS = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

# 샘플 데이터 (원하면 자유롭게 추가/수정)
BOOKS = [
    {
        "id": 1,
        "title": "데미안",
        "author": "헤르만 헤세",
        "emotions": ["우울", "설렘", "답답"],
        "lesson": "새는 알을 깨고 나온다. 스스로를 찾는 자의 투쟁.",
        "characters": [
            {"name": "싱클레어", "mbti": "INFP"},
            {"name": "데미안", "mbti": "INTJ"}
        ],
        "location": {"name": "독일", "lat": 52.52, "lng": 13.405},
        "music": [
            "https://www.youtube.com/watch?v=2g5xkLqIElU",
            "https://www.youtube.com/watch?v=Q4gJVOM-bGk"
        ]
    },
    {
        "id": 2,
        "title": "노인과 바다",
        "author": "어니스트 헤밍웨이",
        "emotions": ["평온", "우울"],
        "lesson": "인간은 패배하도록 만들어지지 않았다. 파괴될 수는 있어도 패배하지는 않는다.",
        "characters": [
            {"name": "산티아고", "mbti": "ISTJ"},
            {"name": "마놀린", "mbti": "ENFP"}
        ],
        "location": {"name": "쿠바 아바나 근해", "lat": 23.1136, "lng": -82.3666},
        "music": [
            "https://www.youtube.com/watch?v=3aYy1B9Wn38"
        ]
    },
    {
        "id": 3,
        "title": "어린 왕자",
        "author": "앙투안 드 생텍쥐페리",
        "emotions": ["행복", "설렘", "평온"],
        "lesson": "중요한 것은 눈에 보이지 않아.",
        "characters": [
            {"name": "어린 왕자", "mbti": "INFJ"},
            {"name": "여우", "mbti": "ENFP"}
        ],
        "location": {"name": "사하라 사막(가상여행)", "lat": 23.4162, "lng": 25.6628},
        "music": [
            "https://www.youtube.com/watch?v=mWRsgZuwf_8"
        ]
    },
    {
        "id": 4,
        "title": "보건교사 안은영",
        "author": "정세랑",
        "emotions": ["설렘", "행복"],
        "lesson": "서로의 언어를 배우려는 시도가 세상을 구한다.",
        "characters": [
            {"name": "안은영", "mbti": "ENFP"},
            {"name": "홍인표", "mbti": "ISTJ"}
        ],
        "location": {"name": "대한민국 서울(가상학교)", "lat": 37.5665, "lng": 126.9780},
        "music": [
            "https://www.youtube.com/watch?v=QH2-TGUlwu4"
        ]
    },
    {
        "id": 5,
        "title": "해리 포터와 마법사의 돌",
        "author": "J.K. 롤링",
        "emotions": ["설렘", "행복"],
        "lesson": "용기는 두려움이 없어서가 아니라, 두려움을 이겨내는 것.",
        "characters": [
            {"name": "해리", "mbti": "ISFP"},
            {"name": "헤르미온느", "mbti": "ESTJ"},
            {"name": "스네이프", "mbti": "INTJ"}
        ],
        "location": {"name": "영국(호그와트)", "lat": 55.3781, "lng": -3.4360},
        "music": [
            "https://www.youtube.com/watch?v=Htaj3o3JD8I"
        ]
    },
    {
        "id": 6,
        "title": "1984",
        "author": "조지 오웰",
        "emotions": ["답답", "분노"],
        "lesson": "자유란 2 더하기 2가 4라는 것을 말할 자유다.",
        "characters": [
            {"name": "윈스턴", "mbti": "INTP"},
            {"name": "줄리아", "mbti": "ESTP"}
        ],
        "location": {"name": "런던(오세아니아)", "lat": 51.5072, "lng": -0.1276},
        "music": [
            "https://www.youtube.com/watch?v=J---aiyznGQ"
        ]
    }
]

# MBTI 기질 그룹 (유사 성향 추천용)
MBTI_GROUPS = {
    "NT": {"INTJ","INTP","ENTJ","ENTP"},
    "NF": {"INFJ","INFP","ENFJ","ENFP"},
    "SJ": {"ISTJ","ISFJ","ESTJ","ESFJ"},
    "SP": {"ISTP","ISFP","ESTP","ESFP"},
}

def mbti_group(m):
    for g, s in MBTI_GROUPS.items():
        if m in s:
            return g
    return None

# ----------------------------- 템플릿 ------------------------------
BASE_CSS = """
<style>
body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, Arial; margin: 0; background:#0b1020; color:#e6e9f0; }
.container { max-width: 980px; margin: 0 auto; padding: 24px; }
.card { background: #121833; border: 1px solid #263055; border-radius: 16px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.24); }
.h1 { font-size: 28px; font-weight: 800; margin: 0 0 12px; }
.sub { opacity:.8; margin-bottom: 16px; }
.row { display:flex; gap:16px; flex-wrap: wrap; }
.col { flex:1; min-width: 240px; }
label { font-weight: 600; margin-bottom: 8px; display:block; }
select, button { width:100%; padding:12px 14px; border-radius: 12px; border:1px solid #334170; background:#0f1530; color:#e6e9f0; }
button { cursor: pointer; font-weight:700; letter-spacing:.2px; }
.button-primary { background: linear-gradient(135deg,#5b8cff,#7a5cff); border:none; }
.kbd { background:#0f1530; border:1px solid #334170; padding:2px 6px; border-radius:8px; }
.badge { display:inline-block; background:#1a2347; border:1px solid #334170; padding:6px 10px; border-radius:9999px; margin-right:6px; }
.hr { border:0; height:1px; background: linear-gradient(90deg,transparent,#2a3566,transparent); margin:18px 0; }
.footer { opacity:.7; font-size: 13px; margin-top: 16px; }
.list { line-height:1.7; }
.music iframe { width:100%; height:260px; border:0; border-radius: 12px; }
.map { height: 520px; border-radius: 16px; overflow: hidden; border:1px solid #263055; }
</style>
"""

INDEX_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>감정 기반 책 추천기</title>
{{ base_css|safe }}
</head>
<body>
<div class="container">
  <div class="card">
    <div class="h1">📚 감정 기반 책 추천기</div>
    <div class="sub">감정을 고르면 책을 추천하고, <span class="kbd">한 줄 교훈</span>, <span class="kbd">MBTI 유사 캐릭터</span>, <span class="kbd">책-음악 매칭</span>까지 제공합니다. 읽기 완료하면 <b>독서 여정 지도</b>에 자동 기록돼요!</div>
    <form method="post" action="{{ url_for('recommend') }}">
      <div class="row">
        <div class="col">
          <label>오늘의 감정</label>
          <select name="emotion" required>
            <option value="" disabled selected>감정을 선택하세요</option>
            {% for e in emotions %}
            <option value="{{e}}">{{e}}</option>
            {% endfor %}
          </select>
        </div>
        <div class="col">
          <label>내 MBTI</label>
          <select name="mbti" required>
            <option value="" disabled selected>MBTI를 선택하세요</option>
            {% for m in mbtis %}
            <option value="{{m}}">{{m}}</option>
            {% endfor %}
          </select>
        </div>
      </div>
      <div style="margin-top:16px;" class="row">
        <div class="col">
          <button class="button-primary" type="submit">추천 받기</button>
        </div>
        <div class="col">
          <a href="{{ url_for('reading_map') }}"><button type="button">내 독서 여정 지도 보기</button></a>
        </div>
      </div>
    </form>
  </div>
  <div class="footer">Tip: <span class="kbd">R</span> 키로 새로고침하면 다른 조합을 쉽게 시도할 수 있어요.</div>
</div>
<script>
  // 편의 단축키: R = 새로고침
  document.addEventListener('keydown', (e)=>{ if(e.key==='r' || e.key==='R'){ location.reload(); }});
</script>
</body>
</html>
"""

RECOMMEND_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>추천 결과</title>
{{ base_css|safe }}
</head>
<body>
<div class="container">
  <div class="card">
    <div class="h1">✨ 추천 결과</div>
    <div class="sub">감정: <span class="badge">{{ emotion }}</span>  ·  MBTI: <span class="badge">{{ mbti }}</span></div>

    <div class="row">
      <div class="col">
        <h3 style="margin:0 0 6px;">📖 {{ book.title }}</h3>
        <div class="sub">{{ book.author }}</div>
        <div class="list">
          <div><b>한 줄 교훈:</b> {{ book.lesson }}</div>
          <div style="margin-top:8px;">
            <b>MBTI 매칭 캐릭터:</b>
            {% if matched_chars %}
              {% for c in matched_chars %}
                <span class="badge">{{ c.name }} ({{ c.mbti }})</span>
              {% endfor %}
            {% else %}
              <span class="badge">직접 일치 없음 → 유사 기질 {{ similar_group }} 추천</span>
              {% for c in similar_chars %}
                <span class="badge">{{ c.name }} ({{ c.mbti }})</span>
              {% endfor %}
            {% endif %}
          </div>
        </div>
        <div class="hr"></div>
        <form method="post" action="{{ url_for('complete') }}">
          <input type="hidden" name="book_id" value="{{ book.id }}">
          <button class="button-primary" type="submit">이 책 읽기 완료! → 지도에 기록</button>
        </form>
        <div style="margin-top:10px;">
          <a href="{{ url_for('index') }}"><button type="button">다시 선택하기</button></a>
          <a href="{{ url_for('reading_map') }}"><button type="button">내 독서 여정 지도</button></a>
        </div>
      </div>
      <div class="col music">
        <h3 style="margin:0 0 6px;">🎵 책-음악 매칭</h3>
        {% if music_embed %}
          {{ music_embed|safe }}
        {% else %}
          <div class="sub">등록된 음악 매칭이 없어요. 다른 책을 시도해 보세요.</div>
        {% endif %}
      </div>
    </div>
  </div>
</div>
</body>
</html>
"""

MAP_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>독서 여정 지도</title>
{{ base_css|safe }}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
</head>
<body>
<div class="container">
  <div class="card">
    <div class="h1">🗺️ 내 독서 여정 지도</div>
    <div class="sub">읽기 완료한 책이 지도에 기록됩니다. 총 <b>{{ count }}</b>권</div>
    <div id="map" class="map"></div>
    <div style="margin-top:12px;">
      <a href="{{ url_for('index') }}"><button type="button">홈으로</button></a>
    </div>
  </div>
</div>
<script>
  const map = L.map('map').setView([20, 0], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap'
  }).addTo(map);

  const records = {{ records|tojson }};
  records.forEach(r => {
    const marker = L.marker([r.location.lat, r.location.lng]).addTo(map);
    const html = `<b>${r.title}</b><br/>${r.author}<br/><small>${r.location.name}</small>`;
    marker.bindPopup(html);
  });

  if(records.length > 0){
    const group = new L.featureGroup(records.map(r => L.marker([r.location.lat, r.location.lng])));
    map.fitBounds(group.getBounds().pad(0.2));
  }
</script>
</body>
</html>
"""

# ----------------------------- 유틸 ------------------------------

def find_books_by_emotion(emotion):
    return [b for b in BOOKS if emotion in b["emotions"]]

def get_book(book_id):
    for b in BOOKS:
        if b["id"] == book_id:
            return b
    return None

def yt_embed(url):
    # 간단한 YouTube 링크를 iframe으로 변환
    if "youtube.com/watch?v=" in url:
        vid = url.split("v=")[-1].split("&")[0]
        return f"<iframe src='https://www.youtube.com/embed/{vid}' allowfullscreen></iframe>"
    if "youtu.be/" in url:
        vid = url.split("youtu.be/")[-1].split("?")[0]
        return f"<iframe src='https://www.youtube.com/embed/{vid}' allowfullscreen></iframe>"
    return None

# ----------------------------- 라우트 ------------------------------
@app.route("/")
def index():
    return render_template_string(INDEX_HTML, base_css=BASE_CSS, emotions=EMOTIONS, mbtis=MBTIS)

@app.route("/recommend", methods=["POST"]) 
def recommend():
    emotion = request.form.get("emotion")
    mbti = request.form.get("mbti")

    candidates = find_books_by_emotion(emotion)
    if not candidates:
        # 해당 감정 데이터가 없으면 임의 전체에서 추천
        candidates = BOOKS[:]
    book = random.choice(candidates)

    # MBTI 일치/유사 캐릭터 찾기
    matched = [c for c in book["characters"] if c["mbti"] == mbti]
    similar_chars = []
    similar_group = None
    if not matched:
        g = mbti_group(mbti)
        similar_group = g
        if g:
            group_set = MBTI_GROUPS[g]
            similar_chars = [c for c in book["characters"] if c["mbti"] in group_set]

    # 음악 임베드
    music_embed = None
    if book["music"]:
        m = random.choice(book["music"])
        music_embed = yt_embed(m)

    session.setdefault("completed", [])

    return render_template_string(
        RECOMMEND_HTML,
        base_css=BASE_CSS,
        emotion=emotion,
        mbti=mbti,
        book=book,
        matched_chars=matched,
        similar_chars=similar_chars,
        similar_group=similar_group,
        music_embed=music_embed
    )

@app.route("/complete", methods=["POST"]) 
def complete():
    book_id = int(request.form.get("book_id"))
    session.setdefault("completed", [])
    if book_id not in session["completed"]:
        session["completed"].append(book_id)
        session.modified = True
    return redirect(url_for('reading_map'))

@app.route("/map") 
def reading_map():
    completed_ids = session.get("completed", [])
    records = [get_book(bid) for bid in completed_ids if get_book(bid)]
    return render_template_string(MAP_HTML, base_css=BASE_CSS, records=records, count=len(records))

# ----------------------------- 실행 ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
