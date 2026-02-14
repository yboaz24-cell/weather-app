import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

# 1. 페이지 설정
st.set_page_config(page_title="🌍 Global Weather App", layout="wide")

# API KEY 확인
if "WEATHER_API_KEY" not in st.secrets:
    st.error("⚠️ Streamlit Secrets에 'WEATHER_API_KEY'를 설정해주세요.")
    st.stop()

API_KEY = st.secrets["WEATHER_API_KEY"]

# ---------------------------
# 2. 위치 정보 감시 (최상단)
# ---------------------------
# 페이지 로드 시 항상 위치를 체크합니다.
loc_data = get_geolocation()

# ---------------------------
# 3. Session State 초기화
# ---------------------------
if "query" not in st.session_state:
    st.session_state.query = "Seoul"
if "mode" not in st.session_state:
    st.session_state.mode = "Search"

st.title("🌍 전 세계 실시간 날씨")

# ---------------------------
# 4. 입력 UI 레이아웃
# ---------------------------
col1, col2 = st.columns([3, 1])

with col1:
    # 도시 입력: 입력값이 바뀌면 즉시 검색 모드로 전환
    city_input = st.text_input("도시 이름 (영어)", value=st.session_state.query if st.session_state.mode == "Search" else "")
    
    if city_input and city_input != st.session_state.query:
        st.session_state.query = city_input
        st.session_state.mode = "Search"
        st.rerun()

with col2:
    st.write("<div style='height:28px'></div>", unsafe_allow_html=True)
    if st.button("📍 내 위치로 조회", use_container_width=True):
        if loc_data:
            lat = loc_data["coords"]["latitude"]
            lon = loc_data["coords"]["longitude"]
            st.session_state.query = f"{lat},{lon}"
            st.session_state.mode = "GPS"
            st.rerun()
        else:
            # 데이터가 아직 없으면 안내 메시지만 띄움 (에러 유발 X)
            st.info("🛰️ 브라우저가 위치를 계산 중입니다. 1~2초 후 다시 눌러주세요.")

# 최종 쿼리 결정 (비어있으면 기본값)
final_q = st.session_state.query if st.session_state.query else "Seoul"

# ---------------------------
# 5. API 호출 및 결과 출력
# ---------------------------
try:
    # 데이터 로딩 중임을 나타내는 스피너 (하단 경고창 대신 사용)
    with st.spinner('날씨 정보를 가져오는 중...'):
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={final_q}&aqi=no"
        response = requests.get(url)
        data = response.json()

    if "error" in data:
        st.error(f"❌ 지역을 찾을 수 없습니다.")
    else:
        loc = data["location"]
        cur = data["current"]

        # 📍 상단 정보 표시
        display_name = f"{loc['name']}, {loc['country']}"
        st.success(f"📍 {display_name} (모드: {st.session_state.mode})")

        # 메인 지표
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("온도", f"{cur['temp_c']}°C", f"체감 {cur['feelslike_c']}°C")
        with m2:
            st.metric("날씨", cur['condition']['text'])
            st.image(f"https:{cur['condition']['icon']}")
        with m3:
            st.metric("습도/UV", f"{cur['humidity']}%", f"UV {cur['uv']}")

        # 하단 안내 박스 (성공했을 때만 나타남)
        st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #dee2e6; color: #333;">
                현재 <b>{loc['name']}</b>의 날씨는 <b>{cur['condition']['text']}</b>입니다.
                <br><small style="color: #999;">업데이트: {loc['localtime']}</small>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    # 완전히 실패했을 경우에만 메시지 출력
    st.error("연결 상태를 확인해주세요.")