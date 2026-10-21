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

線上網址：https://gisprog-app-s1343016.onrender.com/

GitHub 更新後，請在 Render 確認新的部署成功，再檢查上述網址。

## HW5 地圖與手機版

- 選擇行政區及時段後，leafmap 地圖、站點表及供應分級圖使用同一份 HW3 納入站點資料。
- 可借車數分為 0、1–3、4–9、10 輛以上；點擊地圖站點可查看站名及可借車數。
- 使用歷史快照，並非即時車況。地圖標示快照時間，底圖採 OpenStreetMap。
- 手機使用單欄、可換行表格與自動寬度圖表；原有跨時段 HW3 統計與可調門檻的全區分析仍分別保留。

## Render 部署及驗證

Render Web Service 使用本 repo 的 Dockerfile；環境變數設定 `PORT=7860`。服務以非 root 使用者執行，監聽 `0.0.0.0:7860`。

安裝與測試：

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
solara run app.py
```

在 390×844、844×390 及桌面尺寸，檢查整頁沒有水平捲動、圖表刻度及文字完整、表格可讀、地圖能點擊。切換行政區與三個時段、重新整理、橫直向切換後重做檢查。可在瀏覽器開發者工具記錄 `document.documentElement.clientWidth` 與 `document.documentElement.scrollWidth`；兩者相等仍須確認沒有被裁切的內容。

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
