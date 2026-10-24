# GPT-SoVITS Windows VoiceLab

Windows 10/11、NVIDIA GPU 的 GPT-SoVITS 部署、語音克隆與簡報配音工具。版本：1.11。

## v1.11 補齊參考錄音重採樣相依套件

若模型全部載入但合成時出現 ModuleNotFoundError: No module named resampy，原因是 TTS_infer_pack/TTS.py 的 GPU 重採樣路徑直接使用 resampy.filters.get_filter('kaiser_best')，原始相依清單未明確安裝該套件。

新增 scripts/runtime-requirements.txt，固定 resampy==0.4.3 並保留 numpy<2.0；安裝流程在驗收前安裝這份補充清單。doctor 同時檢查匯入及 kaiser_best 濾波器資料。已在 Linux 實測載入濾波器與 48 kHz 轉 16 kHz；Windows 真實語音仍待驗證。

已裝好環境者不必重裝模型，先關閉推理程序，再在 PowerShell 執行：

```powershell
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONPATH = ''
& 'D:\VoiceLab\.runtime\miniforge\Scripts\conda.exe' run --no-capture-output -p 'D:\VoiceLab\.runtime\gptsovits' python -m pip install 'resampy==0.4.3' 'numpy<2.0'
```

補裝成功後重新啟動 03_Start_WebUI.cmd，再用 3–10 秒參考錄音與精確逐字稿試合成。來源：https://pypi.org/project/resampy/0.4.3/ 。

## v1.10 OpenCC 官方 Windows wheel

安裝入口將 requirements.txt 中的 --no-binary=opencc 改成 --only-binary=opencc，並固定官方 opencc==1.4.2。官方已提供 CPython 3.10／Windows x86-64 wheel；沿用同一 OpenCC 套件，不更換為其他實作。requirements.txt 的原始內容先備份為 requirements.txt.before-opencc-wheel。保留既有 OpenJTalk Plus 修復與其他依賴，並在安裝驗收加入 s2tw／t2s 實際轉換檢查。

更新既有電腦時，只更新 scripts/install.ps1 與 scripts/opencc_windows.py，再執行 01_Install.cmd。已在 Linux 實測官方 1.4.2 wheel 匯入與繁簡轉換；Windows 安裝仍須實機驗證。

依賴清單中的 jieba_fast 0.53 仍含 C 擴充。若未安裝 Microsoft C++ 組建工具，請先安裝 Visual Studio Build Tools 的 Desktop development with C++／C++ build tools 工作負載，包含 MSVC x64/x86 與 Windows SDK。新安裝可使用：

```powershell
winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
```

若 Build Tools 已存在但缺少 C++ 元件，請在 Visual Studio Installer 選 Modify 加入工作負載；WinGet upgrade 不會自動新增元件。安裝要求重新啟動時先重開機。此步驟可能下載數 GB，視已安裝元件而異。不要以刪除 jieba_fast 或改用其他套件隱藏原生依賴。

來源：https://pypi.org/project/OpenCC/1.4.2/ 、https://github.com/deepcs233/jieba_fast/blob/master/setup.py 、https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio 。

## v1.9 選用 OpenJTalk 預編譯修復

若 Windows 安裝停在 pyopenjtalk 0.4.1 的 Getting requirements to build wheel，可執行 09_Repair_OpenJTalk.cmd，再執行 01_Install.cmd。這是選用修復，不變更預設 01 的套件方案。

09 會備份官方 requirements.txt 與 install.ps1，將 pyopenjtalk>=0.4.1 改為 pyopenjtalk-plus==0.4.1.post10 並指定 wheel；安裝 numpy 1.26.4，保留既有相容性 constraints；停用原版辭典覆蓋步驟，改用 fork 隨附辭典。最後檢查匯入、必要函式、辭典與文字前端。修復成功訊息不等於全套安裝完成，仍須執行 01。

pyopenjtalk-plus 是 tsukumijima 維護的衍生套件，保留 import pyopenjtalk 介面並提供 CPython 3.10 Windows x86-64 wheel，無需在本機編譯該套件。其日文辭典與部分讀音處理不同於原版；不宣稱日文結果完全相同。如果原版 pyopenjtalk 已安裝，09 會拒絕混裝；已能正常運作的電腦不需要執行 09。其他相依套件若仍需編譯，應依新日誌另行處理。

已驗證：固定官方來源上的備份、冪等修改與未知來源拒絕；Linux 真實套件的 API、辭典、g2p 與 frontend labels。Windows 執行與模型語音仍待實機驗證。

來源：https://pypi.org/project/pyopenjtalk-plus/0.4.1.post10/ 與 https://github.com/tsukumijima/pyopenjtalk-plus 。v1.6 Word／PDF 手冊保留原流程，本節為增補。

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
