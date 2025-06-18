import streamlit as st
import pyrebase
import time
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------
# Firebase 설정
# ---------------------
firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.firebasestorage.app",
    "messagingSenderId": "812186368395",
    "appId": "1:812186368395:web:be2f7291ce54396209d78e"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
firestore = firebase.database()
storage = firebase.storage()

# ---------------------
# 세션 상태 초기화
# ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.id_token = ""
    st.session_state.user_name = ""
    st.session_state.user_gender = "선택 안함"
    st.session_state.user_phone = ""
    st.session_state.profile_image_url = ""

# ---------------------
# 홈 페이지 클래스
# ---------------------
class Home:
    def __init__(self, login_page, register_page, findpw_page):
        st.title("🏠 Home")
        if st.session_state.get("logged_in"):
            st.success(f"{st.session_state.get('user_email')}님 환영합니다.")

        # Kaggle 데이터셋 출처 및 소개
        st.markdown("""
                ---
                **Bike Sharing Demand 데이터셋**  
                - 제공처: [Kaggle Bike Sharing Demand Competition](https://www.kaggle.com/c/bike-sharing-demand)  
                - 설명: 2011–2012년 캘리포니아 주의 수도인 미국 워싱턴 D.C. 인근 도시에서 시간별 자전거 대여량을 기록한 데이터  
                - 주요 변수:  
                  - `datetime`: 날짜 및 시간  
                  - `season`: 계절  
                  - `holiday`: 공휴일 여부  
                  - `workingday`: 근무일 여부  
                  - `weather`: 날씨 상태  
                  - `temp`, `atemp`: 기온 및 체감온도  
                  - `humidity`, `windspeed`: 습도 및 풍속  
                  - `casual`, `registered`, `count`: 비등록·등록·전체 대여 횟수  
                """)

        # 인구 분석 소개 추가
        st.markdown("""
                ---
                **Population Trends Analysis**  
                - 데이터: population_trends.csv  
                - 설명: 대한민국 지역별 인구, 출생아수, 사망자수 데이터를 분석하여 연도별·지역별 추이를 파악합니다.  
                - 주요 변수:  
                  - `연도`: 연도  
                  - `지역`: 지역명  
                  - `인구`: 인구 수  
                  - `출생아수(명)`: 출생아 수  
                  - `사망자수(명)`: 사망자 수  
                """)

# ---------------------
# 로그인 페이지 클래스
# ---------------------
class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token = user['idToken']

                user_info = firestore.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.user_name = user_info.get("name", "")
                    st.session_state.user_gender = user_info.get("gender", "선택 안함")
                    st.session_state.user_phone = user_info.get("phone", "")
                    st.session_state.profile_image_url = user_info.get("profile_image_url", "")

                st.success("로그인 성공!")
                time.sleep(1)
                st.rerun()
            except Exception:
                st.error("로그인 실패")

# ---------------------
# 회원가입 페이지 클래스
# ---------------------
class Register:
    def __init__(self, login_page_url):
        st.title("📝 회원가입")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        name = st.text_input("성명")
        gender = st.selectbox("성별", ["선택 안함", "남성", "여성"])
        phone = st.text_input("휴대전화번호")

        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                firestore.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "name": name,
                    "gender": gender,
                    "phone": phone,
                    "role": "user",
                    "profile_image_url": ""
                })
                st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.switch_page(login_page_url)
            except Exception:
                st.error("회원가입 실패")

# ---------------------
# 비밀번호 찾기 페이지 클래스
# ---------------------
class FindPassword:
    def __init__(self):
        st.title("🔎 비밀번호 찾기")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 메일 전송"):
            try:
                auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일을 전송했습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("이메일 전송 실패")

# ---------------------
# 사용자 정보 수정 페이지 클래스
# ---------------------
class UserInfo:
    def __init__(self):
        st.title("👤 사용자 정보")

        email = st.session_state.get("user_email", "")
        new_email = st.text_input("이메일", value=email)
        name = st.text_input("성명", value=st.session_state.get("user_name", ""))
        gender = st.selectbox(
            "성별",
            ["선택 안함", "남성", "여성"],
            index=["선택 안함", "남성", "여성"].index(st.session_state.get("user_gender", "선택 안함"))
        )
        phone = st.text_input("휴대전화번호", value=st.session_state.get("user_phone", ""))

        uploaded_file = st.file_uploader("프로필 이미지 업로드", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_path = f"profiles/{email.replace('.', '_')}.jpg"
            storage.child(file_path).put(uploaded_file, st.session_state.id_token)
            image_url = storage.child(file_path).get_url(st.session_state.id_token)
            st.session_state.profile_image_url = image_url
            st.image(image_url, width=150)
        elif st.session_state.get("profile_image_url"):
            st.image(st.session_state.profile_image_url, width=150)

        if st.button("수정"):
            st.session_state.user_email = new_email
            st.session_state.user_name = name
            st.session_state.user_gender = gender
            st.session_state.user_phone = phone

            firestore.child("users").child(new_email.replace(".", "_")).update({
                "email": new_email,
                "name": name,
                "gender": gender,
                "phone": phone,
                "profile_image_url": st.session_state.get("profile_image_url", "")
            })

            st.success("사용자 정보가 저장되었습니다.")
            time.sleep(1)
            st.rerun()

# ---------------------
# 로그아웃 페이지 클래스
# ---------------------
class Logout:
    def __init__(self):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.id_token = ""
        st.session_state.user_name = ""
        st.session_state.user_gender = "선택 안함"
        st.session_state.user_phone = ""
        st.session_state.profile_image_url = ""
        st.success("로그아웃 되었습니다.")
        time.sleep(1)
        st.rerun()

# ---------------------
# EDA 페이지 클래스 (수정: 지역별 인구 분석)
# ---------------------
class EDA:
    def __init__(self):
        st.title("📊 Population Trends EDA")
        uploaded = st.file_uploader("Upload population_trends.csv", type="csv", key="pop_file")
        if not uploaded:
            st.info("Please upload population_trends.csv file.")
            return

        # 데이터 로드 및 전처리
        df = pd.read_csv(uploaded, encoding='utf-8')
        df.replace("-", 0, inplace=True)  # '세종'의 '-'를 0으로 치환
        for col in ['인구', '출생아수(명)', '사망자수(명)']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 탭 생성
        tabs = st.tabs([
            "Basic Statistics",
            "Yearly Trends",
            "Regional Analysis",
            "Change Analysis",
            "Visualization"
        ])

        # 1. 기초 통계
        with tabs[0]:
            st.header("🔍 Basic Statistics")
            st.subheader("Missing Values")
            st.bar_chart(df.isnull().sum())
            st.subheader("Duplicate Rows")
            st.write(f"- Number of duplicate rows: {df.duplicated().sum()}")
            st.subheader("Data Structure (df.info())")
            buffer = io.StringIO()
            df.info(buf=buffer)
            st.text(buffer.getvalue())
            st.subheader("Summary Statistics (df.describe())")
            st.dataframe(df.describe())

        # 2. 연도별 추이
        with tabs[1]:
            st.header("📈 Yearly Trends")
            # 전국 데이터 필터링
            df_nation = df[df['지역'] == '전국'].copy()
            df_nation_yearly = df_nation.groupby('연도')['인구'].mean().reset_index()

            # 최근 3년(2021-2023) 데이터로 인구 변화율 계산
            df_recent = df_nation[df_nation['연도'].isin([2021, 2022, 2023])]
            avg_births = df_recent['출생아수(명)'].mean()
            avg_deaths = df_recent['사망자수(명)'].mean()
            avg_change = avg_births - avg_deaths

            # 2023년 인구
            pop_2023 = df_nation[df_nation['연도'] == 2023]['인구'].iloc[0] if not df_nation.empty and 2023 in df_nation['연도'].values else 0

            # 2035년 예측
            years_to_2035 = 2035 - 2023
            pop_2035 = pop_2023 + avg_change * years_to_2035 if pop_2023 > 0 else 0

            # 그래프
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(x='연도', y='인구', data=df_nation_yearly, marker='o', ax=ax)
            ax.scatter([2035], [pop_2035], color='red', s=100, label='2035 Prediction')
            ax.set_title("Nationwide Population Trend and 2035 Prediction")
            ax.set_xlabel("Year")
            ax.set_ylabel("Population")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

        # 3. 지역별 분석
        with tabs[2]:
            st.header("🌐 Regional Analysis")
            # 최근 5년 데이터
            recent_years = df['연도'].max() - 4
            df_recent = df[df['연도'] >= recent_years].copy()

            # 인구 변화량 계산
            df_change = df_recent.groupby('지역')['인구'].diff().groupby(df_recent['지역']).mean().reset_index()
            df_change = df_change[df_change['지역'] != '전국'].sort_values('인구', ascending=False)

            # 변화량 그래프
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            sns.barplot(x='인구', y='지역', data=df_change, ax=ax1)
            ax1.set_xlabel("Population Change (thousands)")
            ax1.set_ylabel("Region")
            for i, v in enumerate(df_change['인구']):
                ax1.text(v, i, f'{v/1000:.1f}k', va='center')
            st.pyplot(fig1)

            # 변화율 그래프
            df_rate = (df_recent.groupby('지역')['인구'].pct_change().groupby(df_recent['지역']).mean() * 100).reset_index()
            df_rate = df_rate[df_rate['지역'] != '전국'].sort_values('인구', ascending=False)
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            sns.barplot(x='인구', y='지역', data=df_rate, ax=ax2)
            ax2.set_xlabel("Change Rate (%)")
            ax2.set_ylabel("Region")
            for i, v in enumerate(df_rate['인구']):
                ax2.text(v, i, f'{v:.1f}%', va='center')
            st.pyplot(fig2)

        # 4. 변화량 분석
        with tabs[3]:
            st.header("📊 Change Analysis")
            # 연도별 인구 증감 계산
            df['인구_증감'] = df.groupby('지역')['인구'].diff()
            top_changes = df[df['지역'] != '전국'].nlargest(100, '인구_증감')[['연도', '지역', '인구_증감']]

            # 색상 처리 (증가: 파랑, 감소: 빨강)
            def color_val(val):
                color = 'blue' if val > 0 else 'red'
                return f'color: {color}'

            st.dataframe(top_changes.style.applymap(color_val, subset=['인구_증감']).format({'인구_증감': '{:,.0f}'}))

        # 5. 시각화 (누적 영역 그래프)
        with tabs[4]:
            st.header("🎨 Visualization")
            pivot_df = df.pivot_table(values='인구', index='연도', columns='지역', aggfunc='mean')
            fig, ax = plt.subplots(figsize=(10, 6))
            pivot_df.plot(kind='area', ax=ax, alpha=0.5)
            ax.set_title("Population Trends by Region")
            ax.set_xlabel("Year")
            ax.set_ylabel("Population")
            ax.legend(title="Region")
            st.pyplot(fig)

# ---------------------
# 페이지 객체 생성
# ---------------------
Page_Login    = st.Page(Login,    title="Login",    icon="🔐", url_path="login")
Page_Register = st.Page(lambda: Register(Page_Login.url_path), title="Register", icon="📝", url_path="register")
Page_FindPW   = st.Page(FindPassword, title="Find PW", icon="🔎", url_path="find-password")
Page_Home     = st.Page(lambda: Home(Page_Login, Page_Register, Page_FindPW), title="Home", icon="🏠", url_path="home", default=True)
Page_User     = st.Page(UserInfo, title="My Info", icon="👤", url_path="user-info")
Page_Logout   = st.Page(Logout,   title="Logout",  icon="🔓", url_path="logout")
Page_EDA      = st.Page(EDA,      title="EDA",     icon="📊", url_path="eda")

# ---------------------
# 네비게이션 실행
# ---------------------
if st.session_state.logged_in:
    pages = [Page_Home, Page_User, Page_Logout, Page_EDA]
else:
    pages = [Page_Home, Page_Login, Page_Register, Page_FindPW]

selected_page = st.navigation(pages)
selected_page.run()
