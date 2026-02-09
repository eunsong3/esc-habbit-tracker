# app.py
import streamlit as st
import requests
import random
from datetime import datetime, timedelta
import pandas as pd
import openai

# =====================
# 기본 설정
# =====================
st.set_page_config(
    page_title="AI 습관 트래커",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI 습관 트래커")

# =====================
# 사이드바
# =====================
with st.sidebar:
    st.header("🔑 API 설정")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    weather_api_key = st.text_input("OpenWeatherMap API Key", type="password")

# =====================
# 세션 상태 초기화
# =====================
if "history" not in st.session_state:
    demo_dates = [datetime.now() - timedelta(days=i) for i in range(6, 0, -1)]
    st.session_state.history = [
        {
            "date": d.strftime("%m/%d"),
            "achieved": random.randint(2, 5)
        }
        for d in demo_dates
    ]

# =====================
# 습관 체크인 UI
# =====================
st.subheader("✅ 오늘의 습관 체크인")

habits = [
    ("🌅 기상 미션", "wake"),
    ("💧 물 마시기", "water"),
    ("📚 공부/독서", "study"),
    ("🏃 운동하기", "exercise"),
    ("😴 수면", "sleep"),
]

cols = st.columns(2)
checked = []

for i, (label, key) in enumerate(habits):
    with cols[i % 2]:
        checked.append(st.checkbox(label, key=key))

mood = st.slider("😊 오늘의 기분", 1, 10, 5)

city = st.selectbox(
    "🌍 도시 선택",
    ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon",
     "Gwangju", "Suwon", "Ulsan", "Jeju", "Changwon"]
)

coach_style = st.radio(
    "🎮 코치 스타일",
    ["스파르타 코치", "따뜻한 멘토", "게임 마스터"]
)

# =====================
# 달성률 계산
# =====================
achieved_count = sum(checked)
achievement_rate = int((achieved_count / len(habits)) * 100)

st.subheader("📈 오늘의 요약")
m1, m2, m3 = st.columns(3)
m1.metric("달성률", f"{achievement_rate}%")
m2.metric("달성 습관", f"{achieved_count}/5")
m3.metric("기분", f"{mood}/10")

# =====================
# 기록 저장 & 차트
# =====================
today_label = datetime.now().strftime("%m/%d")
if not any(h["date"] == today_label for h in st.session_state.history):
    st.session_state.history.append(
        {"date": today_label, "achieved": achieved_count}
    )

df = pd.DataFrame(st.session_state.history)

st.subheader("📊 최근 7일 습관 달성")
st.bar_chart(df.set_index("date"))

# =====================
# API 함수
# =====================
def get_weather(city, api_key):
    if not api_key:
        return None
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "kr"
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        return {
            "desc": data["weather"][0]["description"],
            "temp": data["main"]["temp"]
        }
    except Exception:
        return None


def get_dog_image():
    try:
        r = requests.get("https://dog.ceo/api/breeds/image/random", timeout=10)
        data = r.json()
        img_url = data["message"]
        breed = img_url.split("/breeds/")[1].split("/")[0].replace("-", " ")
        return img_url, breed
    except Exception:
        return None, None

# =====================
# AI 리포트 생성
# =====================
def generate_report(style, habits_done, mood, weather, breed):
    if not openai_api_key:
        return "❗ OpenAI API Key를 입력해주세요."

    openai.api_key = openai_api_key

    system_prompts = {
        "스파르타 코치": "너는 엄격하고 직설적인 스파르타 코치다.",
        "따뜻한 멘토": "너는 공감 능력이 뛰어난 따뜻한 멘토다.",
        "게임 마스터": "너는 RPG 세계관의 게임 마스터다."
    }

    user_prompt = f"""
오늘 습관 달성 개수: {habits_done}/5
오늘 기분: {mood}/10
날씨: {weather}
강아지 품종: {breed}

아래 형식으로 리포트를 작성해줘:
- 컨디션 등급 (S~D)
- 습관 분석
- 날씨 코멘트
- 내일 미션
- 오늘의 한마디
"""

    try:
        res = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_prompts[style]},
                {"role": "user", "content": user_prompt}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ 리포트 생성 실패: {e}"

# =====================
# 결과 표시
# =====================
st.subheader("🤖 AI 코치 리포트")

if st.button("컨디션 리포트 생성"):
    weather = get_weather(city, weather_api_key)
    dog_img, breed = get_dog_image()

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🌦 날씨")
        if weather:
            st.write(f"{weather['desc']} / {weather['temp']}°C")
        else:
            st.write("날씨 정보 없음")

    with c2:
        st.markdown("### 🐶 오늘의 강아지")
        if dog_img:
            st.image(dog_img, use_column_width=True)
            st.caption(f"품종: {breed}")
        else:
            st.write("강아지 이미지 없음")

    report = generate_report(
        coach_style,
        achieved_count,
        mood,
        weather,
        breed
    )

    st.markdown("### 📋 AI 리포트")
    st.write(report)

    st.markdown("### 📢 공유용 텍스트")
    st.code(report)

# =====================
# API 안내
# =====================
with st.expander("ℹ️ API 안내"):
    st.markdown("""
- **OpenAI API**: https://platform.openai.com/
- **OpenWeatherMap API**: https://openweathermap.org/api
- **Dog CEO API**: https://dog.ceo/dog-api/
    """)
