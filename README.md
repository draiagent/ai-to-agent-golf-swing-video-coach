# AI to Agent · Golf Swing Video Coach

> 將高爾夫影片轉成候選關鍵影格，由 Agent 複核後提出一個改善重點、練習方式與四週追蹤計畫。

**技能名稱：** `ai-to-agent-golf-swing-video-coach`  
**版本：** 3.1.0｜2026-09-27｜實驗性技能／教材整合版  
**作者署名：** AI Coach 益力康陳董 x CGM Coach 血糖教練 | 2026 AI to Agent

![AI 影片高爾夫教練](assets/cards/01-overview.png)

## 為什麼建立這個專案

協助球友與教練把「感覺哪裡不對」轉成可檢視的影格，再用複拍觀察練習前後差異。適用單人、固定機位、單次完整揮桿或推桿的短片。

## 實際分工與限制

| 層級 | 本版提供 |
|---|---|
| Python 腳本 | MediaPipe 身體關鍵點追蹤、全揮桿／推桿啟發式分類、五個候選位置、拼圖與 JSON |
| Agent | 確認機位與桿型、看圖修正位置、區分證據與假設、撰寫練習報告 |
| 使用者／教練 | 提供球桿與結果、執行練習、結合現場觀察複核 |
| 教材 | 12 張獨立 PNG、逐頁文字說明、三個模擬案例、社群文章 |

腳本不直接輸出完整教練報告，也沒有 LLM API、自動影片搜尋、球追蹤、足底壓力或 3D 桿面分析。本版未以實拍影片完成端到端驗證。圖卡的關節與軌跡屬教學示意；腳本目前不輸出通用關節角度表或完整軌跡檔。

## 流程

影片 → 姿態追蹤 → 候選關鍵影格 → 人工／Agent 複核 → 一項改善重點 → 練習 → 相同條件複拍。

全揮桿標籤為 `Setup / Top / Transition / Impact / Finish`；圖卡「下桿」概括 `Transition` 候選位置，並非精準生物力學事件。推桿為 `Setup / Back / Impact / Through / Finish`。

## 快速開始

建議以 Python 3.11 的獨立虛擬環境建立相容性基線。本版保留原始 `mediapipe==0.10.14`，不是宣稱它是最新版本。依賴安裝尚未在本交付環境實測。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/swing_prep.py out/ --full face_on.mov
python scripts/swing_prep.py out/ --putt putting.mov
```

Windows PowerShell 啟用方式：`.venv\Scripts\Activate.ps1`。輸入檔名為示範，請改成自己的影片路徑。每次只使用 `--full` 或 `--putt` 其中一個；省略時自動分類。

輸出：`out/key_positions.jpg`、`out/dense_<name>.jpg`、`out/swing_metrics.json`。JSON 最外層以影片檔名為鍵，不是單一平面物件。不同影片請使用不同 basename。

在支援本地技能的 Agent 中，只安裝 `SKILL.md`、`scripts/`、`requirements.txt` 與 `LICENSE`，不要把整份教材當作技能上下文。平台安裝入口依所用工具而異；本專案不保證任意聊天視窗可直接執行。

觸發範例：

> 請使用 ai-to-agent-golf-swing-video-coach 分析這段七號鐵影片，先複核影格，再提出一項優先改善重點；無法確認的項目請標明。

詳細見 [使用指南](docs/usage.md)、[輸出規格與限制](docs/metrics-and-limitations.md)、[三個模擬案例](examples/club-cases.md)。

## 教材與文件

- [12 張圖卡索引與文字說明](docs/cards.md)
- [社群平台介紹](docs/social-post.md)
- [VAD/VAC 任務規格](docs/vad-vac.md)
- [教練報告範本](examples/report-template.md)
- [揮映活力 SwingFrame 風格](docs/visual-style.md)
- [驗證紀錄](docs/validation.md)
- [GitHub 上傳與 Release 指南](docs/publishing.md)

## 主要目錄

```text
SKILL.md                 Agent 執行規則
scripts/swing_prep.py     原始 v3 前處理程式（本版未改演算法）
requirements.txt         相容性基線，非完整鎖檔
VERSION / project.json   版本與中繼資料
assets/cards/            12 張新版 PNG
assets/manifest.json     頁碼、來源、SHA-256
assets/RIGHTS.md          圖片及 Logo 權利範圍
docs/                    使用、限制、教材、社群、發布與驗證
examples/                木桿／鐵桿／推桿案例與報告範本
LICENSE / COPYRIGHT.md   MIT 原文與版權範圍
CHANGELOG.md             真實變更
CONTRIBUTING.md           貢獻方式
RELEASE_NOTES.md          本版發布說明
```

## 後续計畫

先完成木桿、鐵桿、真實推桿影片校準與失敗案例測試，再評估升級 MediaPipe API。匹克球、健身、舞蹈等動作教學是後續方向，須另外設計事件、規則與驗收，尚未實作。

## 授權與版權

程式與文字文件沿用 [MIT License](LICENSE)，保留原始 `Copyright (c) 2026 AI Coach 益力康陳董 x CGM Coach 血糖教練`。圖片、人物與 Logo 不隨程式授予 MIT 權利，詳見 [圖片權利說明](assets/RIGHTS.md) 與 [第三方聲明](THIRD_PARTY_NOTICES.md)。品牌署名不等同法律權利人。

**AI Coach 益力康陳董 x CGM Coach 血糖教練 | 2026 AI to Agent**
