import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

# 1. 페이지 설정
st.set_page_config(page_title="🌍 Global Weather App", layout="wide")

# API KEY 확인
if "WEATHER_API_KEY" not in st.secrets:
    st.error("Secrets에 'WEATHER_API_KEY'를 설정해주세요.")
    st.stop()

API_KEY = st.secrets["WEATHER_API_KEY"]

# 2. 위치 정보 실시간 감시 (최상단 배치)
# 버튼 클릭과 상관없이 브라우저가 제공하는 현재 좌표를 항상 가져옵니다.
curr_loc = get_geolocation()

# 3. session_state 초기화
if "search_query" not in st.session_state:
    st.session_state.search_query = "Seoul"
if "use_gps" not in st.session_state:
    st.session_state.use_gps = False

st.title("🌍 전 세계 실시간 날씨")

# 4. 입력 UI
col1, col2 = st.columns([3, 1])

with col1:
    # 도시 입력 시 즉시 GPS 모드 해제 및 쿼리 업데이트
    city_input = st.text_input("도시 이름을 입력하세요 (영어)", value=st.session_state.search_query)
    if city_input != st.session_state.search_query:
        st.session_state.search_query = city_input
        st.session_state.use_gps = False  # 타이핑하면 GPS 모드 꺼짐
        st.rerun()

with col2:
    st.write("---") # 간격 맞춤
    if st.button("📍 내 위치로 조회", use_container_width=True):
        st.session_state.use_gps = True
        st.rerun()

# 5. 최종 쿼리 결정 로직
if st.session_state.use_gps:
    if curr_loc:
        lat = curr_loc["coords"]["latitude"]
        lon = curr_loc["coords"]["longitude"]
        final_query = f"{lat},{lon}"
    else:
        st.info("🛰️ GPS 신호를 기다리는 중입니다... (권한을 허용해주세요)")
        final_query = st.session_state.search_query # 데이터 올 때까지 기존 값 유지
else:
    # 검색창이 비어있으면 에러 방지를 위해 기본값 설정
    final_query = st.session_state.search_query if st.session_state.search_query else "Seoul"

# 6. Weather API 호출 및 출력
try:
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={final_query}&aqi=no"
    response = requests.get(url)
    data = response.json()

    if "error" in data:
        st.error(f"❌ 지역을 찾을 수 없습니다. (입력값: {final_query})")
    else:
        # 데이터 정리
        loc = data["location"]
        cur = data["current"]

        # 상단 지역 표시
        st.subheader(f"📍 {loc['name']}, {loc['country']} (모드: {'GPS' if st.session_state.use_gps else '검색'})")

        # 날씨 카드 레이아웃
        m1, m2, m3 = st.columns([1, 1, 1])
        
        with m1:
            st.metric("현재 기온", f"{cur['temp_c']}°C", f"체감 {cur['feelslike_c']}°C")
        with m2:
            st.metric("날씨 상태", cur['condition']['text'])
            st.image(f"https:{cur['condition']['icon']}")
        with m3:
            st.metric("습도 및 UV", f"{cur['humidity']}%", f"UV {cur['uv']}")

        # 디자인 요소 (HTML 카드)
        st.markdown(f"""
            <div style="background-color: #f0f8ff; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #d1e9ff;">
                <h4 style="color: #333;">현재 {loc['name']}의 하늘은 <b>{cur['condition']['text']}</b> 입니다.</h4>
            </div>
        """, unsafe_allow_allow_html=True)

except Exception as e:
    st.warning("데이터를 불러오는 중입니다...")