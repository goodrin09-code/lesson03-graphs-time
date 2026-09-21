import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------
# 기본 설정
# -----------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("1년간 일별 박스오피스 데이터를 이용해 영화의 시간에 따른 변화를 살펴봅니다.")


# -----------------------------------------
# 데이터 불러오기
# -----------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 실제 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    # 숫자형 열 변환
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()


# -----------------------------------------
# 데이터 기본 정보
# -----------------------------------------
st.caption(
    f"데이터 기간: {df['날짜'].min().strftime('%Y-%m-%d')} ~ "
    f"{df['날짜'].max().strftime('%Y-%m-%d')}"
)


# =================================================
# 그래프 1. 영화별 일관객 변화
# =================================================
st.header("1. 영화별 일관객 변화")

st.write(
    "영화를 선택하면 해당 영화의 날짜별 일관객 변화를 확인할 수 있습니다."
)

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요",
    movie_list
)

movie_df = df[df["영화명"] == selected_movie].copy()
movie_df = movie_df.sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

fig1.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}"
        "<br>일관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig1.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")

st.text_input(
    "그래프에서 발견한 내용을 한 문장으로 적어 보세요.",
    placeholder="예: 이 영화는 개봉 초기에 관객 수가 가장 많고 이후 점차 감소하는 모습을 보인다.",
    key="graph1_note"
)


# =================================================
# 그래프 2. 일관객 합계가 가장 큰 영화 TOP 5
# =================================================
st.header("2. 일관객 합계가 가장 큰 영화 TOP 5")

st.write(
    "전체 기간 동안 일관객의 합계가 가장 큰 5편의 날짜별 일관객 변화를 비교합니다."
)

top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)["영화명"]
    .tolist()
)

top5_df = df[df["영화명"].isin(top5_movies)].copy()
top5_df = top5_df.sort_values(["날짜", "영화명"])

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    title="일관객 합계 TOP 5 영화의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=(
        "영화: %{fullData.name}"
        "<br>날짜: %{x|%Y-%m-%d}"
        "<br>일관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    legend_title="영화"
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")

st.text_input(
    "그래프에서 발견한 내용을 한 문장으로 적어 보세요.",
    placeholder="예: 기간 전체에서 일관객이 많은 영화들의 관객 수 변화를 비교할 수 있다.",
    key="graph2_note"
)


# =================================================
# 그래프 3. 날짜별 TOP 10 일관객 합계
# =================================================
st.header("3. 날짜별 TOP 10 일관객 합계")

st.write(
    "각 날짜의 박스오피스 10위권 영화의 일관객을 모두 합산하여 날짜별 전체 관객 규모의 변화를 보여 줍니다."
)

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("날짜")
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 TOP 10 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계"
    }
)

fig3.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}"
        "<br>10위권 일관객 합계: %{y:,}명"
        "<extra></extra>"
    )
)

fig3.add_trace(
    go.Scatter(
        x=top3_days["날짜"],
        y=top3_days["일관객"],
        mode="markers+text",
        text=[
            date.strftime("%Y-%m-%d")
            for date in top3_days["날짜"]
        ],
        textposition="top center",
        marker=dict(size=9),
        name="일관객 합계 TOP 3",
        hovertemplate=(
            "날짜: %{x|%Y-%m-%d}"
            "<br>10위권 일관객 합계: %{y:,}명"
            "<extra></extra>"
        )
    )
)

fig3.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계(명)",
    showlegend=False
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")

st.text_input(
    "그래프에서 발견한 내용을 한 문장으로 적어 보세요.",
    placeholder="예: 영화관을 찾는 관객은 특정 시기에 집중되는 경향이 나타난다.",
    key="graph3_note"
)


# =================================================
# 그래프 4. 영화별 기간 일관객 TOP 10
# =================================================
st.header("4. 영화별 기간 일관객 TOP 10")

st.write(
    "전체 기간 동안 영화별 일관객을 모두 더해 관객 수가 많은 영화 TOP 10을 비교합니다."
)

# 영화별 일관객 합계 + 10위권에 기록된 날수 계산
movie_summary = (
    df.groupby("영화명")
    .agg(
        기간_일관객=("일관객", "sum"),
        기록_일수=("날짜", "nunique")
    )
    .reset_index()
)

# 기간 일관객이 많은 TOP 10
top10_movies = (
    movie_summary
    .sort_values("기간_일관객", ascending=False)
    .head(10)
    .copy()
)

# 가로 막대그래프에서 위쪽에 가장 많은 영화가 오도록
top10_movies = top10_movies.sort_values(
    "기간_일관객",
    ascending=True
)

fig4 = px.bar(
    top10_movies,
    x="기간_일관객",
    y="영화명",
    orientation="h",
    title="영화별 기간 일관객 TOP 10",
    labels={
        "기간_일관객": "기간 일관객 합계",
        "영화명": "영화"
    },
    hover_data={
        "기간_일관객": ":,",
        "기록_일수": True
    }
)

fig4.update_traces(
    hovertemplate=(
        "영화: %{y}"
        "<br>기간 일관객 합계: %{x:,}명"
        "<br>10위권 기록 일수: %{customdata[0]}일"
        "<extra></extra>"
    ),
    customdata=top10_movies[["기록_일수"]].values
)

fig4.update_layout(
    xaxis_title="기간 일관객 합계(명)",
    yaxis_title="영화",
    yaxis=dict(
        categoryorder="total ascending"
    )
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")

st.text_input(
    "그래프에서 발견한 내용을 한 문장으로 적어 보세요.",
    placeholder="예: 전체 기간 동안 누적된 일관객 수가 많은 영화들을 비교할 수 있다.",
    key="graph4_note"
)


# =================================================
# 그래프 5. 앞으로 추가할 그래프
# =================================================
st.header("5. 추가 그래프")

st.info(
    "앞으로 새로운 시간 관련 영화 데이터 그래프를 이 구역에 추가할 수 있습니다."
)
