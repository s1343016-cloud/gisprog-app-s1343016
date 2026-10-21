"""臺北 YouBike 空站觀察：依 HW3 資料比較各行政區各時段空站比例。

執行方式：在終端機輸入 solara run app.py
"""

from pathlib import Path
from html import escape
from math import isfinite

import leafmap.leafmap as leafmap
from ipywidgets import Widget
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


分級顏色 = {"0 輛（空站）": "#440154", "1–3 輛": "#31688e", "4–9 輛": "#35b779", "10 輛以上": "#fde725"}


def 供應分級(數量):
    數量 = float(數量)
    if not isfinite(數量) or 數量 < 0 or not 數量.is_integer():
        raise ValueError("可借車數必須是非負整數")
    return list(分級顏色)[0 if 數量 == 0 else 1 if 數量 <= 3 else 2 if 數量 <= 9 else 3]


def 篩選站點(區, 期):
    資料 = df.loc[(df.sarea == 區) & (df.period == 期) & df.analysis_included].copy()
    資料["分級"] = 資料.available_rent_bikes.map(供應分級)
    return 資料


def 轉成GeoJSON(資料):
    特徵們 = []
    for 列 in 資料.itertuples():
        緯度, 經度 = float(列.latitude), float(列.longitude)
        if not (-90 <= 緯度 <= 90 and -180 <= 經度 <= 180):
            raise ValueError("站點座標超出有效範圍")
        分級 = 供應分級(列.available_rent_bikes)
        特徵們.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [經度, 緯度]},
            "properties": {"站名": escape(str(列.sna)), "可借車數": int(列.available_rent_bikes), "分級": 分級},
        })
    return {"type": "FeatureCollection", "features": 特徵們}


def 建立地圖(資料):
    地圖 = leafmap.Map(center=(25.04, 121.54), zoom=12, height="400px", width="100%",
                      toolbar_control=False, draw_control=False, fullscreen_control=False,
                      scale_control=False, scroll_wheel_zoom=False)
    # leafmap 0.63.1 即使關閉工具列仍會建立隱藏圖層管理器；此 App 不使用它。
    地圖.update_layer_manager = lambda: None
    if not 資料.empty:
        地圖.add_geojson(
            轉成GeoJSON(資料), layer_name="YouBike 站點", info_mode="on_click", zoom_to_layer=True,
            point_style={"radius": 6, "color": "#333333", "weight": 1, "fillOpacity": 0.9},
            style_callback=lambda feature: {"fillColor": 分級顏色[feature["properties"]["分級"]]},
        )
    地圖.add_legend(title="可借車數", legend_dict=分級顏色, position="topright")
    地圖.待關閉元件 = 地圖子元件(地圖)
    return 地圖


def 地圖子元件(地圖):
    """記住所有子元件，包含之後可能被使用者關閉的資訊框。"""
    待處理 = [地圖, 地圖._layer_manager_widget]
    元件們 = {}
    while 待處理:
        值 = 待處理.pop()
        if isinstance(值, Widget) and id(值) not in 元件們:
            元件們[id(值)] = 值
            待處理.extend(值.trait_values().values())
        elif isinstance(值, (list, tuple)):
            待處理.extend(值)
        elif isinstance(值, dict):
            待處理.extend(值.values())
    return list(元件們.values())


def 關閉地圖(地圖):
    """切換篩選時釋放舊的圖層、圖例與控制項。"""
    for 元件 in reversed(地圖.待關閉元件):
        元件.close()
    地圖.待關閉元件 = []


@solara.component
def Page():
    solara.Style("""
        .v-application, .v-application__wrap, .v-main, .v-main__wrap,
        .solara-content, .solara-autorouter-content { min-width: 0; max-width: 100%; }
        .v-application__wrap > div, .solara-content-main { width: 100%; min-width: 0; }
        .hw5-app { width: 100%; min-width: 0; max-width: 1100px; margin: auto; }
        .hw5-app > *, .hw5-app .widget-box, .hw5-app .v-sheet { min-width: 0; max-width: 100%; }
        .hw5-app .js-plotly-plot { width: 100%; min-width: 0; max-width: 100%; }
        .hw5-app .leaflet-widgets { margin: 0; }
        .hw5-app p, .hw5-app h1, .hw5-app h2 { overflow-wrap: anywhere; }
        .hw5-app table { width: 100%; table-layout: fixed; }
        .hw5-app th, .hw5-app td { white-space: normal !important; overflow-wrap: anywhere; padding: 6px !important; }
        .hw5-app .v-data-table-footer { flex-wrap: wrap; }
        @media (max-width: 600px) { .hw5-app h1 { font-size: 1.6rem; } }
    """)
    資料 = 篩選站點(行政區.value, 時段.value)
    地圖 = solara.use_memo(lambda: 建立地圖(資料), dependencies=[行政區.value, 時段.value])
    solara.use_effect(lambda: lambda: 關閉地圖(地圖), dependencies=[地圖])
    with solara.Column(classes=["hw5-app"]):
        主內容(資料, 地圖)


@solara.component
def 主內容(資料, 地圖):
    solara.Title("YouBike 空站觀察")
    solara.Markdown("# 臺北 YouBike 各行政區空站比例")
    solara.Select(label="選擇行政區", values=行政區們, value=行政區)
    solara.Select(label="選擇資料時段", values=時段們, value=時段)
    solara.Markdown(f"## {行政區.value}站點地圖")
    快照 = df.loc[df.period == 時段.value, "snapshot_time"].iloc[0]
    solara.Markdown(f"歷史快照：{快照}｜納入站點：**{len(資料)}**。點擊站點可查看站名、可借車數與分級。")
    solara.display(地圖)
    solara.Markdown("底圖：© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)。車況來源：臺北市 YouBike 開放資料，非即時車況。")
    if 資料.empty:
        solara.Markdown("這個行政區與時段沒有納入 HW3 分析的站點。")
    else:
        solara.Markdown("### 站點可借車數")
        solara.DataFrame(資料[["sna", "available_rent_bikes"]].rename(columns={"sna": "站名", "available_rent_bikes": "可借車數"}).reset_index(drop=True), items_per_page=10)
        solara.Markdown("### 同一批站點的供應分級")
        分級表 = 資料["分級"].value_counts().reindex(分級顏色, fill_value=0).rename_axis("分級").reset_index(name="站數")
        分級圖 = px.bar(分級表, x="站數", y="分級", orientation="h", color="分級", color_discrete_map=分級顏色, text="站數")
        分級圖.update_layout(autosize=True, width=None, height=300, margin=dict(l=10, r=20, t=20, b=30), showlegend=False)
        solara.FigurePlotly(分級圖)
    solara.Markdown("## 依行政區檢視 HW3 統計")
    solara.Markdown(
        "依 HW3 的納入站點與空站標記計算所有快照；此區使用固定的 HW3 定義，"
        "不受下方可調空站門檻影響。"
    )

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
            labels={"資料時段": "資料時段", "空站比例（%）": "空站比例（%）"},
        )
        圖.update_layout(
            autosize=True, width=None, margin=dict(l=10, r=20, t=20, b=30),
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
        "門檻只影響這份全區比較；上方時段選單同時更新站點地圖與這份全區比較，不會改變跨時段 HW3 統計。"
    )
    with solara.Column(style={"max-width": "480px"}):
        solara.SliderInt("空站門檻：可借車 ≤", value=門檻, min=0, max=5)

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
            labels={"sarea": "", "空站比例": "空站比例"},
        )
        全區圖.update_layout(
            autosize=True, width=None, margin=dict(l=10, r=20, t=20, b=30),
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
