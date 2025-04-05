import streamlit as st
import pandas as pd
import numpy as np
import glob
import os
import plotly.graph_objects as go

# ファイルパスの指定
folder_path = "data/"
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

# 複数のcsvを結合
df_list = [pd.read_csv(f) for f in csv_files]
data = pd.concat(df_list, ignore_index=True)
data["日付"] = pd.to_datetime(data["日付"], errors='coerce')
data["除脂肪体重"] = pd.to_numeric(data["除脂肪体重"], errors="coerce")
data["除脂肪体重"] = data["除脂肪体重"].replace(0, np.nan)

meibo = pd.read_csv("24trackman.csv")
meibo = meibo.query("PitcherTeam == 'TOK'")

# 分類
m1 = meibo.query("入学年 == 2021")
senior = meibo.query("入学年 == 2022")
junior = meibo.query("入学年 == 2023")
sophomore = meibo.query("入学年 == 2024")
freshman = meibo.query("入学年 == 2025")
pitcher = meibo.query("位置 == '投手'")
batter = meibo.query("位置 != '投手'")

st.title("フィジカルデータ")

page = st.sidebar.radio("表示モードを選択", ("個人表示", "全体表示"))

if page == "個人表示":
    st.header("個人別データ表示")
    names = list(meibo["フルネーム"].unique())
    selected_name = st.sidebar.selectbox("名前を選択", options=names)

    filtered_data = data[data["名前"] == selected_name].copy()
    filtered_data["日付"] = pd.to_datetime(filtered_data["日付"], errors="coerce")
    filtered_data["体重"] = pd.to_numeric(filtered_data["体重"], errors="coerce")
    filtered_data["除脂肪体重"] = pd.to_numeric(filtered_data["除脂肪体重"], errors="coerce")
    filtered_data = filtered_data.dropna(subset=["日付", "体重"])
    filtered_data = filtered_data.sort_values("日付")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_data["日付"], y=filtered_data["体重"], mode='lines+markers', name="体重"))
    fig.add_trace(go.Scatter(x=filtered_data["日付"], y=filtered_data["除脂肪体重"], mode='lines+markers', name="除脂肪体重"))

    fig.update_layout(
        title=f"{selected_name}の体重推移",
        xaxis_title="日付",
        yaxis_title="kg",
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"{selected_name}のデータ")
    columns = ["日付", "名前", "体重", "体脂肪率", "除脂肪体重", "スクワットMAX(kg)", "ベンチプレスMAX(kg)", 
               "握力(左)", "握力(右)", "プルダウン", "Broad Jump(cm)", "Left Ice Skater Jump(cm)", 
               "Right Ice Skater Jump(cm)", "メディシン(バックスロー3kg)", "プライオ(三段跳び)", "チンニング", "ガチスタ"]
    st.dataframe(filtered_data[columns])

elif page == "全体表示":
    st.header("平均データ表示")
    option = st.sidebar.selectbox("データを選択", options=["全体", "1年生", "2年生", "3年生", "4年生", "R7卒生", "投手", "野手"])

    label_dict = {
        "全体": meibo,
        "1年生": freshman,
        "2年生": sophomore,
        "3年生": junior,
        "4年生": senior,
        "R7卒生": m1,
        "投手": pitcher,
        "野手": batter
    }

    selected_group = label_dict[option]
    df = data[data["名前"].isin(selected_group["フルネーム"])]
    df["日付"] = pd.to_datetime(df["日付"], errors="coerce")
    df["体重"] = pd.to_numeric(df["体重"], errors="coerce")
    df["除脂肪体重"] = pd.to_numeric(df["除脂肪体重"], errors="coerce")
    df_mean = df.groupby("日付")[["体重", "除脂肪体重"]].mean().reset_index()
    df_mean = df_mean.sort_values("日付")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_mean["日付"], y=df_mean["体重"], mode='lines+markers', name="体重"))
    fig.add_trace(go.Scatter(x=df_mean["日付"], y=df_mean["除脂肪体重"], mode='lines+markers', name="除脂肪体重"))

    fig.update_layout(
        title=f"{option}の平均値の推移",
        xaxis_title="日付",
        yaxis_title="kg",
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    if option in ["1年生", "2年生", "3年生", "4年生", "R7卒生"]:
        pos_pitcher = selected_group[selected_group["位置"] == "投手"]
        pos_batter = selected_group[selected_group["位置"] != "投手"]

        for df_sub, pos_label in zip(
            [data[data["名前"].isin(pos_pitcher["フルネーム"])],
             data[data["名前"].isin(pos_batter["フルネーム"])]],
            ["投手", "野手"]
        ):
            df_sub["日付"] = pd.to_datetime(df_sub["日付"], errors="coerce")
            df_sub["体重"] = pd.to_numeric(df_sub["体重"], errors="coerce")
            df_sub["除脂肪体重"] = pd.to_numeric(df_sub["除脂肪体重"], errors="coerce")

            # 人数・測定回数を表示
            num_players = df_sub["名前"].nunique()
            num_records = len(df_sub)
            st.markdown(f"**{option}（{pos_label}）**：{num_players}人、{num_records}件の測定データ")

            df_mean_sub = df_sub.groupby("日付")[["体重", "除脂肪体重"]].mean().reset_index()
            df_mean_sub = df_mean_sub.sort_values("日付")

            fig_sub = go.Figure()
            fig_sub.add_trace(go.Scatter(x=df_mean_sub["日付"], y=df_mean_sub["体重"], mode='lines+markers', name="体重"))
            fig_sub.add_trace(go.Scatter(x=df_mean_sub["日付"], y=df_mean_sub["除脂肪体重"], mode='lines+markers', name="除脂肪体重"))

            fig_sub.update_layout(
                title=f"{option}（{pos_label}）の平均値の推移",
                xaxis_title="日付",
                yaxis_title="kg",
                hovermode='x unified'
            )

            st.plotly_chart(fig_sub, use_container_width=True)

