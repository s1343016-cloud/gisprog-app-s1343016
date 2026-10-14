---
title: YouBike 空站觀察
emoji: 🚲
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 臺北 YouBike 空站觀察

> 上面 `---` 之間的設定是給 HuggingFace Spaces 讀的（W5 部署時使用），請保留。

這個 App 使用 HW3 整理的 YouBike 快照資料，觀察臺北各行政區在不同時段的空站情形。選擇行政區後，可比較各時段的站點總數、空站數與空站比例；原有的全區分析也保留時段選擇與空站門檻，可比較不同行政區的空站比例。

## App 用途

App 可用來回答：不同行政區的 YouBike 空站比例如何隨資料快照時段變化？選取單一行政區時，表格與長條圖會同步呈現該區各時段的 HW3 統計；全區分析則可選擇單一時段及空站門檻，查看各區的比較結果。

## 資料

| 項目 | 內容 |
|---|---|
| 來源 | 臺北市資料大平臺「YouBike2.0 臺北市公共自行車即時資訊」 |
| 網址 | `https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json` |
| 授權 | 政府資料開放授權條款－第 1 版（使用時須註明來源） |
| 資料檔案 | `data/youbike_hw3_cleaned_long.csv` |
| 資料日期與快照時間 | 2026-09-30（星期三）00:31:52；2026-10-01（星期四）10:02:52；2026-10-07（星期三）15:40:52 |

快照時間依 HW3 CSV 的 `snapshot_time` 欄位記錄；日期與星期依 `infoDate` 欄位確認。HW3 行政區分析沿用 CSV 的 `analysis_included` 與 `empty` 欄位進行計算。

App 使用的資料欄位包括：`sno`、`sarea`、`period`、`snapshot_time`、`infoDate`、`analysis_included`、`empty`、`act_raw` 與 `available_rent_bikes`。

## 在 Codespaces 執行

1. 在 repo 頁面按 **Code → Codespaces → Create codespace on main**。
2. 等環境建好（第一次約 2–3 分鐘，會自動安裝 `requirements.txt` 的套件）。
3. 在終端機輸入：

   ```bash
   solara run app.py
   ```

4. 右下角出現提示時，按 **Open in Browser**；或到「連接埠」分頁，開啟 8765 埠。

## 修改之後

```bash
git status          # 哪些檔案被改了？
git diff            # 改了哪幾行？
   git add README.md   # 只加入本次確認過的檔案
git commit -m "說明你改了什麼"
git push
```

**agent 改完之後，一定先看 `git diff` 再 commit。**

## 授權

- **程式碼**（`app.py`、`Dockerfile` 等）：MIT License，見 [`LICENSE`](LICENSE)。可以自由使用、修改、公開，請保留 `LICENSE` 檔。
- **資料**（`data/youbike_hw3_cleaned_long.csv`）：來源為臺北市資料大平臺的 YouBike 2.0 開放資料，依政府資料開放授權條款－第 1 版使用，不適用 MIT；使用資料時請註明來源。
