import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
import numpy as np
import glob
import os

# ファイルパスの指定
folder_path = "トレデータ/"
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

# 複数のCSVを読み込んで結合
df_list = [pd.read_csv(f) for f in csv_files]
data = pd.concat(df_list, ignore_index=True)
data["日付"] = pd.to_datetime(data["日付"], errors='coerce')
data["除脂肪体重"] = data["除脂肪体重"].replace(0, np.nan)

#data = pd.read_csv("トレ全体4.csv")
meibo = pd.read_csv("24trackman.csv")

meibo = meibo.query("PitcherTeam == 'TOK'")

st.title("フィジカルデータ")

page = st.sidebar.radio("表示モードを選択", ("個人表示", "全体表示"))

if page == "個人表示":
    st.header("個人別データ表示")
    names = list(meibo["フルネーム"].unique())
    selected_name = st.sidebar.selectbox("名前を選択", options=names)

    #if selected_name != "全員":
    filtered_data = data[data["名前"] == selected_name].copy()
    filtered_data["日付"] = pd.to_datetime(filtered_data["日付"], errors="coerce")
    filtered_data["体重"] = pd.to_numeric(filtered_data["体重"], errors="coerce")
    filtered_data = filtered_data.dropna(subset=["日付", "体重"])
    filtered_data = filtered_data.sort_values("日付")

    date = filtered_data["日付"]
    weight = filtered_data["体重"]

    fig, ax = plt.subplots()
    ax.plot(date, weight, label="体重", marker="o", linestyle="-")
    ax.plot(date, filtered_data["除脂肪体重"], label="除脂肪体重", marker="o", linestyle="-")
    ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
    #ax.set_xticklabels(date.dt.strftime("%Y-%m-%d"), rotation=45)
    ax.set_xlabel("日付")
    ax.set_ylabel("kg")

    st.pyplot(fig)
    #else:
        #filtered_data = data

    st.subheader(f"{selected_name}のデータ" if selected_name != "全員" else "全ユーザーのデータ")

    columns = ["日付", "名前", "体重", "体脂肪率", "除脂肪体重", "スクワットMAX(kg)", "ベンチプレスMAX(kg)", 
               "握力(左)", "握力(右)", "プルダウン", "Broad Jump(cm)", "Left Ice Skater Jump(cm)", 
               "Right Ice Skater Jump(cm)", "メディシン(バックスロー3kg)", "プライオ(三段跳び)", "チンニング", "ガチスタ"]
    looked_data = filtered_data[columns]
    st.dataframe(looked_data)

elif page == "全体表示":
    st.header("平均データ表示")
    df = data#.copy()
    df["日付"] = pd.to_datetime(df["日付"], errors="coerce")
    df["体重"] = pd.to_numeric(df["体重"], errors="coerce")
    df["除脂肪体重"] = pd.to_numeric(df["除脂肪体重"], errors="coerce")
    df_mean = df.groupby("日付")[["体重", "除脂肪体重"]].mean().reset_index()
    df_mean = df_mean.sort_values(by="日付")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df_mean["日付"], df_mean["体重"], marker="o", linestyle="-", label="体重")
    ax.plot(df_mean["日付"], df_mean["除脂肪体重"], marker="o", linestyle="-", label="除脂肪体重")
    #ax.set_xticklabels(df_mean["日付"].dt.strftime("%Y-%m-%d"), rotation=45)
    ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
    ax.set_xlabel("日付")
    ax.set_ylabel("kg")
    ax.set_title("平均値の推移")

    st.pyplot(fig)