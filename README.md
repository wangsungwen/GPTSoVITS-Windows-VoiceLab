# GPT-SoVITS Windows VoiceLab

Windows 10/11、NVIDIA GPU 的 GPT-SoVITS 部署、語音克隆與簡報配音工具。版本：1.8。

## v1.8 Conda 警告處理修正

官方 Invoke-Conda 同樣會在 PowerShell 5.1 的 stderr 擷取階段因一般警告而中止。v1.8 將 Conda 也交由記錄工具執行，合併輸出並依原始退出碼判定結果。Conda 日誌位於 logs/conda-時間-程序編號-console.log；pip 日誌規則不變。更新 scripts/install.ps1 與 scripts/pip_logged_runner.py 後，再執行 01_Install.cmd。這會沿用既有環境與模型，不會把真正的非零退出碼當成成功。Linux 已測試帶警告的成功與失敗情境；Windows 整合尚待實機回報。

## v1.7 相依套件安裝日誌修正

針對 Windows PowerShell 在官方 Invoke-Pip 的 stderr 擷取階段提前中止、只顯示 subprocess-exited-with-error 的情況，新增 scripts/pip_logged_runner.py。每次 pip 安裝均在 logs 留下 pip-時間-程序編號.log 與 pip-時間-程序編號-console.log，保留實際套件與建置錯誤及退出碼；不會忽略安裝失敗。

已安裝者只需更新 scripts/install.ps1 與 scripts/pip_logged_runner.py，再執行 01_Install.cmd。已有環境與模型目錄會沿用。這是錯誤輸出修正，不能保證解決尚未識別的依賴問題；若仍失敗，提供最新的 pip-*-console.log。成功／失敗及日誌保留已在 Linux 模擬 pip 驗證，Windows 整合仍待實機回報。Word／PDF 手冊維持 v1.6 基礎操作說明。

## 操作說明書下載

- [Word 操作說明書](docs/GPTSoVITS_Windows_VoiceLab_操作說明書_v1.6.docx)
- [PDF 操作說明書](docs/GPTSoVITS_Windows_VoiceLab_操作說明書_v1.6.pdf)

兩份均為 10 頁繁體中文手冊，涵蓋首次安裝、WebUI 語音克隆、參考錄音、14 頁批次配音、單頁重做、影片合成、微調備份與故障排除。已正常啟動介面者可從第 4 節開始。

## 快速開始

1. 使用 Code → Download ZIP，完整解壓後將專案放在 `D:\VoiceLab`。路徑使用英文且不含空白。
2. 首次部署執行 `01_Install.cmd`，預設 Python 3.10、PyTorch 2.7.1 + CUDA 12.8、v2Pro 模型。
3. 執行 `02_Check_GPU_Models.cmd`，確認 CUDA 與必要模型檔案。
4. 執行 `03_Start_WebUI.cmd`，依終端機網址開啟本機介面，通常為 http://127.0.0.1:9874 。
5. 在介面啟動 TTS 推理，準備本人或已獲授權的 3–10 秒參考錄音與精確逐字稿，先合成短句並試聽。

## 操作入口

| CMD | 功能 |
| --- | --- |
| 01_Install | 建立隔離環境、下載官方程式與模型、套用相容性修復及驗收 |
| 02_Check_GPU_Models | 檢查套件、實際 CUDA 運算與必要模型檔 |
| 03_Start_WebUI | 啟動官方操作介面 |
| 04_Start_API | 啟動本機 API，127.0.0.1:9880 |
| 05_Prepare_Reference | 擷取 7 秒單聲道 32 kHz 參考 WAV |
| 06_Batch_14_Slides | 依 slides.csv 產生逐頁旁白 |
| 07_Make_Presentation_Video | 依圖片與旁白合成 1080p MP4 |
| 08_Repair_WebUI | 固定網頁套件並驗證頁面與 schema 相容性 |

## 完整說明與程式碼

- [繁體中文完整操作說明](README_繁體中文.md)：安裝、資料夾、錄音、批次配音、影片、訓練與排錯。
- [scripts](scripts)：完整 PowerShell 與 Python 程式。
- [驗證紀錄](VALIDATION.json) 與 [入口檢查及 SHA-256](CMD_AUDIT.json)。
- [授權](LICENSE_KIT.txt)：本專案新增工具採 MIT；官方程式與模型依各自授權。

## 資料與目錄

包含 14 張 ES0003 4K PNG、14 頁講稿模板、參考逐字稿模板與資料夾骨架。Git 不追蹤空目錄，因此使用 `.gitkeep` 保留位置。模型及 Python 環境由安裝流程取得；個人錄音、既有模型、已安裝環境與生成成果沒有包含在原始碼庫內。講稿模板仍需替換為核定英文講稿。

已正常運作的電腦只更新 8 個 CMD、scripts 及說明；保留已安裝環境、模型、個人設定、講稿、錄音與輸出。

## 版本與驗證範圍

官方來源固定為 RVC-Boss/GPT-SoVITS 的 `b4570b876f5c086819ba84e3215472733c6a7b70`，安裝時下載；本庫不包含官方程式的複製品。

使用者於 2026-10-24 回報 Windows 安裝與 WebUI 修復檢查通過、介面可使用。v1.6 在 Linux 完成靜態檢查、封裝與圖片比對；未在此環境重新執行 Windows 安裝、真實模型推理、訓練或完整報告影片流程。

官方專案：https://github.com/RVC-Boss/GPT-SoVITS
