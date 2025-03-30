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

#data = pd.read_csv("トレ全体4.csv")
meibo = pd.read_csv("24trackman.csv")

meibo = meibo.query("PitcherTeam == 'TOK'")

st.title("トレ＆体重データ")

page = st.sidebar.radio("表示モードを選択", ("個人表示", "全体表示"))

if page == "個人表示":
    st.header("個人別データ表示")
    # ユーザー名の選択
    names = ["全員"] + list(meibo["フルネーム"].unique())
    selected_name = st.sidebar.selectbox("名前を選択", options=names)
    
    # フィルター処理
    if selected_name != "全員":
        filtered_data = data[data["名前"] == selected_name]
        date = filtered_data["日付"].tolist()
        weight = filtered_data["体重"].tolist()
        plt.plot(date, weight, label=selected_name)
        plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
        plt.xticks(rotation=45)
        plt.xlabel("日付")
        plt.ylabel("体重")
        st.pyplot()
    else:
        filtered_data = data
    
    st.subheader(f"{selected_name}のデータ" if selected_name != "全員" else "全ユーザーのデータ")
    st.dataframe(filtered_data)

elif page == "全体表示":
    st.header("平均データ表示")