"""臺北 YouBike 空站觀察：依 HW3 資料比較各行政區各時段空站比例。

執行方式：在終端機輸入 solara run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import solara

DATA_PATH = Path(__file__).parent / "data" / "youbike_hw3_cleaned_long.csv"

# 在元件外讀取一次，保留 HW3 已整理的納入與空站判定欄位。
df = pd.read_csv(DATA_PATH, dtype={"sno": str, "act": str})
行政區們 = sorted(df["sarea"].dropna().unique().tolist())
時段們 = (
    df[["period", "snapshot_time"]]
    .drop_duplicates()
    .sort_values("snapshot_time")["period"]
    .tolist()
)
快照資訊 = (
    df[["infoDate", "snapshot_time"]]
    .drop_duplicates()
    .sort_values("snapshot_time")
)

行政區 = solara.reactive("大安區" if "大安區" in 行政區們 else 行政區們[0])
門檻 = solara.reactive(0)
時段 = solara.reactive(時段們[0])


def 各時段空站統計(資料):
    """依 HW3 標記計算各時段納入站點的數量與空站比例。"""
    表 = (
        資料.groupby("period", sort=False)
        .agg(站點總數=("sno", "size"), 空站數=("empty", "sum"))
        .reindex(時段們)
    )
    表[["站點總數", "空站數"]] = 表[["站點總數", "空站數"]].fillna(0).astype(int)
    分母 = 表["站點總數"].where(表["站點總數"] != 0)
    表["空站比例（%）"] = (表["空站數"] / 分母 * 100).round(1)
    return 表.rename_axis("資料時段").reset_index()


def 各區空站比例(資料, 門檻值):
    """沿用原功能，以可借車數門檻計算各區空站比例。"""
    資料 = 資料.assign(空站=資料["available_rent_bikes"] <= 門檻值)
    表 = 資料.groupby("sarea").agg(站數=("sno", "size"), 空站數=("空站", "sum"))
    表["空站比例"] = (表["空站數"] / 表["站數"]).round(3)
    return 表.sort_values("空站比例", ascending=False).reset_index()


@solara.component
def Page():
    solara.Title("YouBike 空站觀察")
    solara.Markdown("# 臺北 YouBike 各行政區空站比例")
    solara.Markdown("## 依行政區檢視 HW3 統計")
    solara.Markdown(
        "依 HW3 的納入站點與空站標記計算所有快照；此區使用固定的 HW3 定義，"
        "不受下方可調空站門檻影響。"
    )
    solara.Select(label="選擇行政區", values=行政區們, value=行政區)

    行政區資料 = df.loc[
        (df["sarea"] == 行政區.value) & df["analysis_included"]
    ]
    表 = 各時段空站統計(行政區資料)
    if 表["站點總數"].sum() == 0:
        solara.Markdown(
            f"{行政區.value}沒有納入 HW3 統計的站點，因此沒有可繪製的空站比例。"
        )
    else:
        圖 = px.bar(
            表,
            x="資料時段",
            y="空站比例（%）",
            title=f"{行政區.value}各時段空站比例",
            labels={"資料時段": "資料時段", "空站比例（%）": "空站比例（%）"},
        )
        圖.update_layout(
            xaxis_title="資料時段",
            yaxis={"title": "空站比例（%）", "ticksuffix": "%", "rangemode": "tozero"},
            showlegend=False,
        )
        solara.FigurePlotly(圖)

    顯示表 = 表.copy()
    顯示表["空站比例（%）"] = 顯示表["空站比例（%）"].map(
        lambda 比例: f"{比例:.1f}%" if pd.notna(比例) else "無法計算"
    )
    solara.DataFrame(顯示表)

    solara.Markdown("## 原有全區空站觀察")
    solara.Markdown(
        "此區只計營運中的站，並以可借車數小於或等於門檻判定空站；"
        "門檻與時段控制只影響這份全區比較，不會改變上方 HW3 統計。"
    )
    with solara.Column(style={"max-width": "480px"}):
        solara.SliderInt("空站門檻：可借車 ≤", value=門檻, min=0, max=5)
    solara.ToggleButtonsSingle(value=時段, values=時段們)

    營運站點 = df.loc[df["act_raw"] == 1]
    當時資料 = 營運站點.loc[營運站點["period"] == 時段.value]
    全區表 = 各區空站比例(當時資料, 門檻.value)
    if 全區表.empty:
        solara.Markdown("這個時段沒有符合條件的營運站資料，無法呈現全區比較。")
    else:
        全區圖 = px.bar(
            全區表,
            x="空站比例",
            y="sarea",
            orientation="h",
            title=f"{時段.value}，可借車 ≤ {門檻.value} 算空站（只算營運中的站）",
            labels={"sarea": "", "空站比例": "空站比例"},
        )
        全區圖.update_layout(
            yaxis={"categoryorder": "total ascending"},
            xaxis_tickformat=".0%",
            height=150 + 30 * len(全區表),
        )
        solara.FigurePlotly(全區圖)
        solara.DataFrame(全區表)

    星期名稱 = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    快照文字 = "；".join(
        f"{pd.Timestamp(日期).strftime('%Y-%m-%d')}（"
        f"{星期名稱[pd.Timestamp(日期).dayofweek]}）"
        f"{pd.Timestamp(時間).strftime('%H:%M:%S')}"
        for 日期, 時間 in 快照資訊.itertuples(index=False, name=None)
    )
    solara.Markdown(
        "資料來源：[臺北市 YouBike 開放資料（臺北市資料大平臺）]"
        "(https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json)。\n\n"
        f"資料日期、星期與快照時間：{快照文字}。\n\n"
        "資料授權：政府資料開放授權條款－第 1 版。"
    )
