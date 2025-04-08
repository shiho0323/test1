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

folder_path2 = "BLAST/"
csv_files2 = glob.glob(os.path.join(folder_path2, "*.csv"))
df_list2 = [pd.read_csv(f) for f in csv_files]
BLAST = pd.concat(df_list, ignore_index=True)

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

st.title("フィジカル＆練習データ")

page = st.sidebar.radio("表示モードを選択", ("個人表示", "全体表示"), index = 1)

if page == "個人表示":
    st.header("個人別データ表示")
    # 学年ごとの並び順を指定（4年→3年→2年→1年→R7卒）
    grade_order = [2022, 2023, 2024, 2025, 2021]

    # 学年ごとに処理して、投手→野手の順に並べる
    sorted_meibo = pd.DataFrame()
    for year in grade_order:
        year_group = meibo[meibo["入学年"] == year]
        pitchers = year_group[year_group["位置"] == "投手"].sort_values("フルネーム")
        batters = year_group[year_group["位置"] != "投手"].sort_values("フルネーム")
        sorted_meibo = pd.concat([sorted_meibo, pitchers, batters], ignore_index=True)

    names = sorted_meibo["フルネーム"].tolist()
    selected_name = st.sidebar.selectbox("名前を選択", options=names)

    page = st.sidebar.radio("表示モードを選択", ("測定会データ", "BLAST推移"), index = 1)

    if page == "測定会データ":
        st.subheader(f"{selected_name}の測定会データ")
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
            title=f"{selected_name}の測定会データ",
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
    
    elif page == "BLAST推移":
        BLAST['Date'] = pd.to_datetime(BLAST['Date'])
        BLAST = BLAST.query('mode == "ドラ直"')

        player_data = BLAST[BLAST["name"] == selected_name].copy()

        if player_data.empty:
            st.write("データがありません。")  # データが1件もなかったらスキップ

        player_data['Month'] = player_data['Date'].dt.to_period('M')
        monthly_avg = player_data.groupby('Month')[["バットスピード (km/h)", "スイング時間 (秒)"]].mean().reset_index()
        monthly_avg['Month'] = monthly_avg['Month'].dt.to_timestamp()  # plotly用にdatetime型に戻す

        #if monthly_avg.empty:
            #continue  # 月別平均が空（データがまとまらなかった）ときもスキップ

        # Plotlyで描画
        fig = go.Figure()

        # バットスピード：左軸
        fig.add_trace(go.Scatter(
            x=monthly_avg["Month"],
            y=monthly_avg["バットスピード (km/h)"],
            mode='lines+markers',
            name="バットスピード (km/h)",
            yaxis="y1"
        ))

        # スイング時間：右軸
        fig.add_trace(go.Scatter(
            x=monthly_avg["Month"],
            y=monthly_avg["スイング時間 (秒)"],
            mode='lines+markers',
            name="スイング時間 (秒)",
            yaxis="y2"
        ))
        # レイアウト：2軸設定
        fig.update_layout(
            title=f"{p} の月別平均（バットスピード＆スイング時間）",
            xaxis=dict(title="月"),
            yaxis=dict(title="バットスピード (km/h)", side="left"),
             yaxis2=dict(
                title="スイング時間 (秒)",
                overlaying="y",
                side="right",
                showgrid=False
               ),
            legend=dict(x=0.01, y=0.99),
            width=800,
            height=400
        )


        fig.update_layout(
        xaxis=dict(
            tickformat="%Y-%m",
            tickvals=monthly_avg["Month"]  # 月ごとのdatetimeのリストを渡す
        )
        )

        fig.update_layout(
        legend=dict(
            x=1.2,  # x=1より右に出る（1がグラフの右端）
            y=1,     # y=1は上端（1がグラフの上）
            xanchor="left",
            yanchor="top",
            bordercolor="lightgray",
            borderwidth=1
        )
        )

        st.plotly_chart(fig, use_container_width=True)


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

