# GPT-SoVITS Windows NVIDIA 語音克隆操作包

這是「在您的 Windows 電腦執行」的部署包。2026-10-24 使用者回報安裝檢查、WebUI 修復檢查通過，並確認介面可以使用；實際語音品質與微調效果仍須試聽驗證。它會自動取得官方程式、建立隔離環境並下載模型；壓縮檔本身不含大型預訓練模型。請使用本人或已獲授權的錄音。

## v1.12 整合與實機合成成功

使用者已在 RTX 2080 Ti 11 GB 回報 v2Pro 真實英文語音合成成功。新版 01 已整合 Conda／pip 日誌、OpenCC 官方 wheel、resampy 補充相依套件與濾波器檢查；新環境自動使用 pyopenjtalk-plus，已有原版 pyopenjtalk 則保留。Plus 的日文辭典與部分讀音行為不同於原版。jieba_fast 仍需要 Microsoft C++ Build Tools。

已正常運作的電腦直接使用 03，不必重裝。新安裝、更新及驗證範圍以 docs/版本更新說明_v1.12.md 為準；下列舊版章節保留供追查修復歷程。

## v1.6 完整資料夾版（2026-10-24）

ZIP 明確收錄空目錄，解壓後保留完整存放位置：

| 資料 | 路徑 | 包內內容 |
| --- | --- | --- |
| 環境 | .runtime/miniforge、.runtime/gptsovits | 空目錄，安裝時建立環境 |
| 官方程式與模型 | GPT-SoVITS/GPT_SoVITS/pretrained_models | 預建目錄，安裝時取得官方程式與模型 |
| 訓練資料及權重 | GPT-SoVITS/dataset/raw、dataset/wavs、GPT_weights_v2Pro、SoVITS_weights_v2Pro | 空目錄 |
| 講稿 | texts、slides.csv | 保留原先 14 頁講稿模板與配對；需填入核定講稿 |
| 錄音 | reference | 保留逐字稿模板；未含私人錄音 |
| 圖片 | slides | 已放入 ES0003 的 14 張 3840×2160 PNG，含更新後第 11 頁 |
| 語音輸出 | output_audio | 空目錄，批次生成後存放 WAV |
| 影片輸出 | 部署包根目錄 | 生成後為 ES0003_Presentation.mp4 |
| 日誌與下載 | logs、downloads、GPT-SoVITS/logs | 空目錄 |

此包提供完整目錄與本對話已取得的素材，並非您 D:\VoiceLab 的整機備份。您電腦上的既有模型、已安裝環境、編修講稿、私人錄音及已生成結果未傳回本工作區，因此沒有假裝收錄。更新已正常運作的電腦時，只更新 CMD、scripts 與說明；保留原有資料。新電腦才解壓完整包並執行 01。

安裝流程使用 install.ps1 檔案判斷官方程式是否已取得，避免預建空目錄造成跳過下載。沒有預建 pretrained_models/sv 或 G2PWModel，避免官方腳本誤判模型已下載。

## v1.5 最終入口檢查（2026-10-24）

8 個 CMD 均統一 UTF-8 主控台、切換部署包根目錄、檢查目標腳本存在、保留錯誤代碼與失敗提示。所有入口均透過 common.ps1 使用隔離環境，停用使用者套件並清空繼承的 PYTHONPATH。01 安裝新增 WebUI 相容性測試，通過後才顯示 INSTALL CHECKS PASSED。

已正常運作的使用者不必重新安裝或再次修復。更新入口時，只複製本包根目錄的 8 個 CMD、整個 scripts 資料夾，以及這份說明至 D:\VoiceLab。不要用模板的 texts、reference、slides、slides.csv 覆蓋自己的資料；保留 .runtime、GPT-SoVITS、tts_local.yaml 與輸出檔。日常直接使用 03；08 僅供需要時修復。各入口與檔案 SHA-256 見 CMD_AUDIT.json。

## v1.4 修復 WebUI 的 TemplateResponse 錯誤與使用者套件混入

若 9874 已啟動但出現 `TypeError: unhashable type: dict`，且堆疊由 Gradio `templates.TemplateResponse` 進入 Starlette／Jinja2，使用此修復。新版 Starlette 移除了 Gradio 4.x 仍使用的舊模板呼叫簽名。本包固定 Gradio 4.44.1、FastAPI 0.115.6、Starlette 0.41.3、Pydantic 2.10.6、Jinja2 3.1.6、huggingface-hub 0.36.0。這是沿用 Gradio 4 的相容性處理，不宣稱這些都是最新版。

`common.ps1` 對這個程序及其子程序設定 `PYTHONNOUSERSITE=1`，並清空繼承的 `PYTHONPATH`，避免再載入 AppData/Roaming/Python 的使用者套件。這不更動 Windows 全域環境變數，也不刪除其他專案的 Python 套件。

已安裝者：將新版包的 `scripts` 資料夾及 `08_Repair_WebUI.cmd` 複製到 D:\VoiceLab 覆蓋對應檔案；保留 texts、reference、slides、模型與 output_audio。關閉舊 WebUI 後，雙擊 `08_Repair_WebUI.cmd`。修復入口會在隔離狀態下補齊 requirements 相依套件並固定網頁套件版本，可能下載原先只存在使用者目錄的套件；不下載模型，也不執行模型訓練。

看到 `WEBUI REPAIR CHECKS PASSED`，再開 `03_Start_WebUI.cmd`。若修復失敗，請提供 `logs/webui-repair-時間.log`。

驗證：已在獨立 Linux Python 環境安裝相同網頁套件組合，以含音訊、文字與按鈕的 Gradio 測試介面驗證 HTML、config 與 info 端點。這只驗證網頁相容性，不替代 Windows GPT-SoVITS 實際介面與語音模型測試。

來源：https://www.starlette.io/release-notes/ （移除舊版 TemplateResponse 簽名）

## v1.3 安裝修正：torchcodec 找不到 Windows 套件

若安裝停在 `Could not find a version that satisfies the requirement torchcodec`，v1.3 將官方腳本中的三處 `Invoke-Pip torch torchcodec --index-url ...` 改為相容配對 `torch==2.7.1` 與 `torchaudio==2.7.1`。原腳本備份為 `GPT-SoVITS/install.ps1.before-kit-v1.3`，修改可重複執行。本包核對的專案使用 `torchaudio.load`，沒有直接匯入 `torchcodec`；此 TorchAudio 配對使用既有音訊後端，不需要新版 TorchCodec 路線。

部署包建立 `pip-constraints.txt`，在安裝期間固定 torch／torchaudio／torchvision 版本，防止後續 requirements 解依賴時跳升。這仍不是全部相依套件的完整鎖檔。RTX 5090 使用 `CU128`。已核對官方提供 Windows、Python 3.10 的 torch 2.7.1+cu128 與 torchaudio 2.7.1+cu128 wheel，尚未在您的 Windows GPU 上驗證完整模型推論。

更新時只需將此包的 `scripts/install.ps1` 覆蓋到 `D:\VoiceLab\scripts\install.ps1`，再執行 `01_Install.cmd`。已有的 Miniforge、環境與完整模型目錄會沿用；先前不完整的模型仍可能需要獨立修復。請使用新版 `01_Install.cmd` 入口，而不是從備份或手動呼叫尚未修補的官方腳本。

官方版本來源：https://pytorch.org/get-started/previous-versions/#v271
TorchAudio 2.7 後端：https://docs.pytorch.org/audio/2.7.0/generated/torchaudio.load.html

## v1.2 安裝修正：Conda Windows 啟動器紀錄

如果 Miniforge 已安裝，但 `conda create` 出現 `Could not find share/conda-launchers/cli-64.exe`，v1.2 會先驗證隔離 base 環境的 launcher 檔案、`paths_data` 紀錄與 SHA-256；不合格時啟用 `CONDA_SAFETY_CHECKS=warn` 並 force-reinstall `conda-launchers`。修復後再次驗證，通過才建立 Python 環境。這依據官方 issue https://github.com/conda/conda-launchers/issues/35 的 workaround；錯誤本身不能證明是缺檔或缺紀錄，檢查會區分有效／需修復狀態。

若先前建立目標環境未完成且沒有 Conda history，會更名備份為 `.runtime/gptsovits.incomplete-時間-程序編號`，保留內容後重新建立；已有 history 則使用 conda install 補齊。無需刪除整個 `.runtime` 或重裝顯示卡驅動。

舊版升級只需覆蓋 ZIP 中的 `scripts/install.ps1` 到 `D:\VoiceLab\scripts\install.ps1`，再執行 `01_Install.cmd`。

## v1.1 安裝修正：Miniforge SHA-256 下載 404

舊版將沒有版本號的 EXE 別名直接加上 `.sha256`，但官方僅提供含版本號的校驗檔，因此在建立 Python 環境前中止。v1.1 固定 Miniforge 26.9.4-0，使用官方校驗檔及 release API 交叉核對的 SHA-256，不再請求錯誤網址。已下載的 EXE 若校驗相符會沿用，否則下載到 `.partial`，驗證成功才取代快取。

已使用舊版的修復方式：關閉失敗的安裝視窗，將新 ZIP 解壓至另一個暫存資料夾，只複製其中 `scripts/install.ps1` 覆蓋 `D:\VoiceLab\scripts\install.ps1`，再執行原位置的 `01_Install.cmd`。不必刪除 `.runtime`、`downloads` 或原有模型與講稿，也不要用整包模板覆蓋已編輯的內容。

## 一、快速開始

1. 完整解壓到 `D:\VoiceLab` 或 `C:\VoiceLab`，路徑使用英文、不含空白。請勿在 ZIP 預覽內執行。建議避開 OneDrive 同步資料夾。
2. 安裝 NVIDIA 顯示卡驅動並重新啟動；一般不需另裝完整 CUDA Toolkit。這個包預設使用官方 CU128 安裝選項，驅動與顯卡相容性最後由實際 CUDA 運算檢查。
3. 雙擊 `01_Install.cmd`。下載包含 Miniforge、Python 3.10、PyTorch、FFmpeg、GPT-SoVITS 相依套件與官方模型，所需時間取決於網路。建議預留 50 GB 可用空間，這是操作餘裕，並非官方最低需求。
4. 看到 `INSTALL CHECKS PASSED` 後，雙擊 `02_Check_GPU_Models.cmd`，確認 `cuda_available: true` 且 `errors: []`。
5. 雙擊 `03_Start_WebUI.cmd`，使用瀏覽器開啟 http://127.0.0.1:9874 。第一次載入可能較久；啟動視窗須保持開啟。
6. 在主介面開啟 TTS 推論 WebUI，通常位於 http://127.0.0.1:9872 。本包採官方程式預設 v2Pro 系列；選擇對應底模，先做免訓練推論。
7. 上傳約 5–8 秒乾淨參考錄音，填入「錄音實際說出的逐字文字」及語言，再輸入要生成的文字與目標語言，合成並試聽。

本包在安裝後將 Gradio 明確的 `server_name="0.0.0.0"` 設定改為 `127.0.0.1`；API 也綁定本機。未開啟公開分享，不需要設定路由器轉發。停止時在啟動視窗按 Ctrl+C。勿在 API 和 WebUI 同時載入模型時誤以為顯示記憶體占用不會增加。

## 二、完整架構與資料位置

| 層次 | 元件 | 功能／位置 |
| --- | --- | --- |
| 操作入口 | `.cmd`、PowerShell | 安裝、檢查、啟動與批次工具 |
| 隔離環境 | `.runtime/miniforge`、`.runtime/gptsovits` | Python、CUDA 版 PyTorch、音訊工具；不取代系統 Python |
| 官方應用 | `GPT-SoVITS/` | 官方 WebUI、語料工具、GPT／SoVITS 訓練與 API |
| 預訓練模型 | `GPT-SoVITS/GPT_SoVITS/pretrained_models/` | 語意、聲學、HuBERT、BERT、speaker embedding |
| 參考聲音 | `reference/reference.wav`、`reference.txt` | 同一段聲音與精確逐字稿 |
| 訓練資料 | `GPT-SoVITS/dataset/`（自行建立） | 錄音、切片、標註 `.list` |
| 訓練成果 | `GPT-SoVITS/logs/`、`GPT_weights_v2Pro/`、`SoVITS_weights_v2Pro/` | 特徵、中間檔與 GPT／SoVITS 權重；權重目錄位於官方程式根目錄 |
| 長篇旁白 | `texts/*.txt`、`slides.csv` | 每頁一份講稿，避免把 12 分鐘文字當作單一工作 |
| 輸出 | `output_audio/` | 每頁 WAV 與生成時間報表 |
| 影片 | `slides/*.png` → `ES0003_Presentation.mp4` | 逐頁圖片配對旁白，依實際聲音長度切頁 |
| 安裝診斷 | `logs/` | 安裝紀錄、套件清單、GPU 與模型檢查結果 |

聲音生成關係：參考聲音與逐字稿提供說話者／語境條件；目標文字轉換為語音特徵，再由 GPT 語意模型與 SoVITS 聲學模型生成波形。微調會另外更新模型權重；免訓練模式不會替您訓練一組專屬權重。

## 三、錄音準備與第一次操作

建議先走免訓練路線，再判斷是否值得微調。官方介紹有 5 秒參考音訊的 zero-shot 功能；本次核對的實作檢查參考音訊為 3–10 秒。本包採 7 秒轉檔預設，但選段必須是一個自然完整句子，不能任意截斷尾音。

- 使用同一位說話者、安靜房間、固定麥克風距離，避免背景音樂、迴音、多人交談及削波失真。
- 中文錄音可以跨語言生成英文，但不能保證口音、音色、術語與語調完全正確。英文報告建議另外錄製清楚的英文參考句，逐段試聽。
- 準備長錄音後雙擊 `05_Prepare_Reference.cmd`，輸入來源路徑與起始秒數；會抽出 7 秒、單聲道、32 kHz PCM WAV。可直接自行準備符合條件的 WAV，不強制使用此工具。
- 試聽 `reference/reference.wav`，將同一段實際內容填入 `reference/reference.txt`。參考逐字稿不是「要合成的新講稿」。
- 在 WebUI 以一兩句英文測試，再逐步增加長度。先試 `Good afternoon. Today I will present our collaborative orchard monitoring architecture.`
- 技術詞可在旁白稿改為實際讀法，例如 `U A V`、`LoRa W A N`，但每次需試聽；模型可能對縮寫有不同讀法。

## 四、14 頁報告批次語音

`texts/slide_01.txt` 至 `slide_14.txt` 目前是明確的待填欄位，並非您已核定的完整口說稿。將既有英文講稿逐頁貼入對應檔案，以 UTF-8 儲存。`slides.csv` 已建立 14 頁配對。

1. 將英文參考聲音與其逐字稿放到 `reference/`。
2. 填妥 14 頁講稿，不保留 `[REPLACE ...]`。
3. 停止 WebUI／推論子視窗以釋放 VRAM；雙擊 `04_Start_API.cmd`，等模型載入並看到伺服器啟動訊息。API 位址 http://127.0.0.1:9880 ，互動文件 http://127.0.0.1:9880/docs 。
4. 另開視窗雙擊 `06_Batch_14_Slides.cmd`，輸出 `output_audio/slide_01.wav` 至 `slide_14.wav`。每頁完成後更新 `generation_report.json`，內含實際音長與生成耗時。
5. 逐頁試聽、修正人名與術語；總音長以實際生成結果為準，不保證剛好 12 分鐘。不要為達時限盲目加速。

批次工具預設參考語言是英文。中文參考音訊請以命令列設定 `--prompt-lang zh`；目標語言由 `slides.csv` 的 `text_lang` 決定，英文用 `en`、中英混合用 `zh`。使用遠端 API 時，`ref_audio_path` 必須是伺服器看得到的路徑；此包預設同一部電腦運作。

手動執行範例（PowerShell，位於解壓根目錄）：

```powershell
& .\.runtime\miniforge\Scripts\conda.exe run --no-capture-output -p .\.runtime\gptsovits python .\scripts\batch_tts.py --manifest .\slides.csv --reference .\reference\reference.wav --prompt .\reference\reference.txt --prompt-lang en --out .\output_audio --dry-run
```

移除 `--dry-run` 才會生成。已有同名輸出時會停止，避免蓋掉已核定的旁白。修改一頁時，可複製 CSV、只保留該頁，再明確加 `--overwrite` 重新生成。若中途失敗，只把未完成頁面放入新 CSV 後續跑。

## 五、圖片＋旁白產生報告影片

將先前 4K PNG ZIP 解壓後的 14 張圖片放入 `slides/`，檔名須為 `ES0003_Slide_01.png` 至 `ES0003_Slide_14.png`。音訊核對完成後雙擊 `07_Make_Presentation_Video.cmd`。

會輸出 1920×1080、30 FPS、H.264／AAC MP4，每頁音訊後補 0.5 秒停頓。來源 4K 圖片會縮為 1080p，適合寄送或上傳。這個步驟只合成影片，不會寄信，也不會自動上傳。會議是否需要真人出鏡，仍依大會要求。

## 六、少量資料微調訓練

免訓練結果若不足，再進行微調。官方示範可使用約 1 分鐘訓練資料；為了較穩定的語音品質，實務上可先準備數分鐘至十餘分鐘乾淨且多樣的本人錄音，實際效果依資料而異。

1. 備份原始錄音，將素材放入 `GPT-SoVITS/dataset/raw/`。有伴奏時才考慮 UVR5；已乾淨的人聲可直接使用，避免額外處理損傷音質。
2. 使用官方主 WebUI 的音訊切分工具，得到自然句子的切片。檢查片頭片尾，不切掉子音，去除長靜音與非語音噪音。
3. 使用辨識／標註工具產生 `.list`，逐段人工核對 ASR 錯字、人名及語言標籤。格式 `音檔路徑|說話者名稱|語言|逐字稿`，例如 `D:/VoiceLab/GPT-SoVITS/dataset/wavs/001.wav|speaker01|EN|Good afternoon, everyone.`。自動 ASR 模型可能會在第一次使用時另行下載。
4. 到 GPT-SoVITS 訓練分頁，建立實驗名稱 `speaker01_v2pro`；版本與預訓練 GPT、SoVITS G／D 必須一致，切勿混用 v2、v2Pro、v3、v4 權重。
5. 執行文字處理、HuBERT／SSL 特徵、語意 token 等官方「資料準備」步驟，再執行 SoVITS 與 GPT 訓練。實際按鈕文字以這次固定版本介面為準。
6. 您的顯卡為 RTX 5090，約 32 GB VRAM；仍不固定承諾 batch size 或訓練時間。先用介面建議的小 batch；OOM 時降低 batch、關閉其他模型程序，必要時使用介面提供的梯度檢查點。不要未看驗證結果就增加 epochs。
7. 選取同一實驗對應的 GPT `.ckpt` 與 SoVITS `.pth`，在推論介面測試未出現在訓練資料的句子。比較咬字、自然度、音色與重複／漏字。
8. API 改用個人權重時，編輯 `tts_local.yaml` 的 `t2s_weights_path`、`vits_weights_path`，並保持 `version` 正確；停止 API 再重啟。微調後仍需參考錄音。

可選下載 UVR5 的安裝命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Device CU128 -Source HF -DownloadUVR5
```

## 七、驗收標準與問題排查

| 關卡 | 成功條件 | 常見處理 |
| --- | --- | --- |
| 驅動 | `nvidia-smi` 能列出 GPU | 安裝驅動、重新啟動 |
| 相依套件 | doctor 匯入檢查無錯 | 看 `logs/install-*.log` 第一個失敗；若需編譯 opencc／pyopenjtalk，可安裝 Microsoft C++ Build Tools 再重跑 |
| CUDA | 陣列運算成功 | 檢查驅動、PyTorch wheel、GPU 架構；不要只看 nvidia-smi 的 CUDA Version |
| 模型 | 必要路徑存在且非空 | 官方下載中斷會留下部分資料；先備份並更名不完整模型資料夾，再重跑安裝。勿刪除個人訓練成果 |
| WebUI／API | 模型載入後可開啟頁面 | 第一次載入較久；端口被占用時先關閉舊程序 |
| 真實推論 | 一句話產出可播放 WAV | 確認 3–10 秒參考、正確逐字稿與語言，查看啟動視窗錯誤 |
| 訓練 | 個人權重產生且新句可讀 | 檢查標註、版本一致性、VRAM 與過擬合 |
| 報告影片 | 圖片順序、聲音、總時長正確 | 試看完整 MP4，再自行提交會議 |

若 CU128 不適合您的驅動，可更新驅動，或依 GPU 相容性選擇官方另一選項：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Device CU126 -Source HF
```

這不是所有顯卡均適用的保證。發生錯誤請提供顯卡型號、VRAM、`logs/doctor.json`、安裝或啟動視窗最後約 30 行訊息。無需提供您的私人錄音或密碼。

## 八、版本、驗證範圍與來源

官方程式快照固定為 `b4570b876f5c086819ba84e3215472733c6a7b70`；安裝包不會自動切換 main。官方模型壓縮包與 Python 依賴仍是下載當下版本，不能宣稱完全鎖版；成功安裝後會記錄 `logs/installed-packages.txt` 方便追蹤。來源快照保存於本機 downloads，後續請備份實驗設定與權重。

本次驗證包括 Python 編譯、模擬 API 批次輸出／錯誤檢查、參考音檔轉檔與圖片配音的實際 FFmpeg 編碼。模擬 API 使用測試波形，不是語音克隆品質驗證。本地檢查環境為 Linux、無 NVIDIA GPU；使用者已在 Windows 回報安裝檢查與 WebUI 修復通過、介面可使用。這不等同於完整語音合成、14 頁批次、影片及微調均已實機驗證。

- GPT-SoVITS 官方：https://github.com/RVC-Boss/GPT-SoVITS
- 固定快照：https://github.com/RVC-Boss/GPT-SoVITS/tree/b4570b876f5c086819ba84e3215472733c6a7b70
- 官方 Windows 安裝：https://github.com/RVC-Boss/GPT-SoVITS/blob/b4570b876f5c086819ba84e3215472733c6a7b70/install.ps1
- API 定義：https://github.com/RVC-Boss/GPT-SoVITS/blob/b4570b876f5c086819ba84e3215472733c6a7b70/api_v2.py
- Miniforge：https://github.com/conda-forge/miniforge

此包新增的啟動器與工具使用 MIT License，見 `LICENSE_KIT.txt`；官方程式、模型及第三方依賴依各自授權。
