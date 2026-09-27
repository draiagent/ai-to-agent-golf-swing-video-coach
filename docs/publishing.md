# GitHub 上傳指南

建議 repository 名稱：`ai-to-agent-golf-swing-video-coach`

Description：高爾夫影片前處理與 Agent 教練判讀技能，附 12 張知識圖卡、三類球桿案例及四週追蹤規格。

Topics：`ai-to-agent`, `agent-skill`, `golf`, `mediapipe`, `pose-estimation`, `sports-coaching`, `traditional-chinese`。

Website 留空：本專案尚無已驗證的公開示範網址。visibility 由建立遠端時決定；本包未更改任何遠端。

## 上傳

1. 解壓縮交付 ZIP，進入 ai-to-agent-golf-swing-video-coach 目錄。
2. 建立同名 GitHub repo，選擇預期可見性；若已有同名 repo，先比較內容再合併。
3. 上傳此目錄內檔案，勿只上傳 ZIP。圖片建議使用 Git 用戶端推送。
4. 先執行 `python scripts/validate_release.py`，閱讀驗證與已知限制。
5. 若要建立 Release，確認目標 commit 後使用新 tag `v3.1.0`，說明採 RELEASE_NOTES.md；不要移動既有 tag。

教材 PNG 是可閱讀示意，非動作標註資料；不要把 GitHub 公開瀏覽解讀成圖片已採 MIT 授權。
