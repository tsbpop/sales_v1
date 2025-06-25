import streamlit as st
import pandas as pd

st.title("📦 상품 구성 확인")

# 1. 엑셀 업로드
uploaded_file = st.file_uploader("📁 '상품' 시트와 '판매' 시트가 있는 Excel 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    try:
        # 2. 시트 불러오기
        상품_df = pd.read_excel(uploaded_file, sheet_name='상품')
        판매_df = pd.read_excel(uploaded_file, sheet_name='판매')

        # 3. 병합 셀 대응
        상품_df['상품'] = 상품_df['상품'].fillna(method='ffill')
        판매_df['일'] = 판매_df['일'].fillna(method='ffill')
        판매_df['상품명'] = 판매_df['상품명'].fillna(method='ffill')

        # 4. 날짜 처리
        판매_df['일'] = pd.to_datetime(판매_df['일'])

        # 5. 구성품 검색
        구성품_검색어 = st.text_input("🔍 구성품을 입력하세요 (예: 초콜릿)")

        # 6. 날짜 범위
        st.write("🗓️ 조회 기간을 선택하세요:")
        시작일 = st.date_input("시작일", value=판매_df['일'].min().date())
        종료일 = st.date_input("종료일", value=판매_df['일'].max().date())

        if 구성품_검색어:
            # 7. 관련 상품명 필터
            상품명_리스트 = 상품_df[상품_df['구성품'].str.contains(구성품_검색어, na=False)]['상품'].dropna().tolist()
            상품명_리스트 = [x for x in 상품명_리스트 if str(x).strip() != ""]
            st.write("📦 해당 구성품이 포함된 상품:", 상품명_리스트)

            # 8. 판매 필터
            판매_필터 = 판매_df[
                (판매_df['상품명'].isin(상품명_리스트)) &
                (판매_df['일'].dt.date >= 시작일) &
                (판매_df['일'].dt.date <= 종료일)
            ]

            # 9. 상품+일자별 집계
            집계 = 판매_필터.groupby(['일', '상품명'], as_index=False)[['거래건수', '거래금액']].sum()

            # 10. 비중 계산
            전체_금액 = 판매_df.groupby('일')['거래금액'].sum()
            집계['비중(%)'] = 집계.apply(lambda row: round(row['거래금액'] / 전체_금액[row['일']] * 100, 2), axis=1)

            # 11. 숫자 포맷
            집계['거래금액'] = 집계['거래금액'].apply(lambda x: f"{x:,.0f}")
            집계['비중(%)'] = 집계['비중(%)'].apply(lambda x: f"{x:.2f}%")

            # 12. 결과 표시
            st.write("📊 분석 결과:")
            st.dataframe(집계[['일', '상품명', '거래건수', '거래금액', '비중(%)']])

            # 13. 상품 구성 보기
            선택상품 = st.selectbox("🔍 구성품을 보고 싶은 상품을 선택하세요", sorted(set(집계['상품명'])))
            구성정보 = 상품_df[상품_df['상품'] == 선택상품][['구성품', '개수']].drop_duplicates()
            st.write(f"📋 **{선택상품}**의 구성 (중복 제외):")
            st.dataframe(구성정보.reset_index(drop=True))


    except Exception as e:
        st.error(f"❌ 엑셀 파일을 불러오는데 문제가 발생했습니다: {e}")
