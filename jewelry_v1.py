import streamlit as st
import pandas as pd
import random
from collections import Counter, defaultdict

st.title("🔨 장신구 강화 시뮬레이터")

uploaded_file = st.file_uploader("강화 확률 엑셀 파일 업로드", type=[".xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df = df.rename(columns=lambda x: x.strip())

    st.subheader("📊 강화 확률 테이블")
    st.dataframe(df)

    prob_table = {
        int(row['강화 단계']): {
            'success': float(row['확률']),
            'destroy': float(row['파괴확률'])
        } for _, row in df.iterrows()
    }

    initial_count = st.number_input("초기 장신구 수", min_value=4, value=100, step=1)
    min_remaining = st.number_input("최소 남길 장신구 수", min_value=1, max_value=initial_count-1, value=3, step=1)
    item_price = st.number_input("장신구 개당 가격 (원)", min_value=0, value=3000, step=100)
    repeat_count = st.number_input("반복 시뮬레이션 횟수", min_value=1, value=1, step=1)

    if st.button("🧪 시뮬레이션 시작"):
        with st.spinner("시뮬레이션 실행 중... 잠시만 기다려주세요"):
            total_attempts = 0
            total_destroyed = 0
            total_results = defaultdict(int)
            full_log = []

            for repeat in range(repeat_count):
                accessories = [0] * initial_count
                attempts = 0
                destroyed = 0
                attempt_log = []

                while len(accessories) > min_remaining:
                    accessories.sort()
                    target = accessories[0]
                    prob = prob_table.get(target + 1, {'success': 0.0, 'destroy': 1.0})
                    roll = random.random()

                    if roll < prob['success']:
                        accessories[0] += 1
                        result = f"강화 성공 → +{accessories[0]}"
                    elif roll < prob['success'] + prob['destroy']:
                        accessories.pop(0)
                        destroyed += 1
                        result = "장신구 파괴"
                    else:
                        result = f"강화 실패 → +{target} 유지"

                    attempts += 1
                    if repeat_count == 1:
                        attempt_log.append(f"[{attempts}] +{target} 시도 → {result} (남은 {len(accessories)}개)")

                result_counter = Counter(accessories)
                for k, v in result_counter.items():
                    total_results[k] += v
                total_attempts += attempts
                total_destroyed += destroyed
                if repeat_count == 1:
                    full_log = attempt_log

            avg_attempts = total_attempts / repeat_count
            avg_destroyed = total_destroyed / repeat_count
            avg_results = {k: v / repeat_count for k, v in sorted(total_results.items())}
            total_cost = initial_count * item_price

            st.subheader("📈 반복 시뮬레이션 결과 요약")
            st.write(f"🔁 반복 횟수: {repeat_count}회")
            st.write(f"📊 평균 시도 횟수: {avg_attempts:.1f}회")
            st.write(f"💥 평균 파괴 수: {avg_destroyed:.1f}개")
            st.write("📦 평균 강화 결과:")
            st.write(avg_results)
            st.write(f"💰 평균 비용: {total_cost:,}원")

            if repeat_count == 1:
                with st.expander("📜 로그 보기"):
                    st.text("\n".join(full_log))
else:
    st.info("엑셀 파일을 업로드해주세요. 컬럼은 '강화 단계', '확률', '파괴확률'이어야 합니다.")
