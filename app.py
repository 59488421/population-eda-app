import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="인구 분석 앱", layout="wide")
st.title("📈 지역별 인구 분석 웹앱")

uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())
else:
    st.info("population_trends.csv 파일을 업로드해주세요.")
