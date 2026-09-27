# 輸出規格與限制

版本 3.1.0｜2026-09-27

| 欄位 | 真實意義 | 不可推論 |
|---|---|---|
| fps | OpenCV 讀取值，缺失時原碼回退 30 | 不保證慢動作時間基準正確 |
| stroke_type | 手腕垂直位移閾值分類 full／putt | 不辨識木桿／鐵桿、切球或所有動作 |
| pose_detected_ratio | 取得骨架的影格比例 | 不是關鍵點正確率或事件準確率 |
| positions_s | 候選影格索引 / fps | 不保證真實擊球時間 |
| spine_tilt_deg | 正規化 2D 肩髖中點連線傾角 | 未校正長寬比；不是脊椎真實角度 |
| backstroke_s / forward_to_impact_s | 推桿候選事件間時間 | 不是球桿實測速度 |
| tempo_ratio_approx | 推桿候選時間比 | 不適用通用好壞門檻 |
| through_to_back_ratio | 推桿手腕水平投影擺幅比 | 不能直接診斷擊球減速 |
| metric_error | 計算中例外文字 | 有此欄位不能宣稱量測完整 |

JSON 外層依 basename 分組，例如 `{"putting": {"stroke_type": "putt"}}`（此為省略欄位的結構示意，不是實測）。

程式追蹤過程只保留 x、y、visibility，未使用 3D world landmarks；手腕軌跡是內部計算，未另存完整軌跡。拼圖主要是帶標籤影片截圖，不會像教學圖卡自動畫出彩色骨架。一般關節角度、完整全揮桿節奏表、壓力熱圖與總分均未實作。

原碼還有：空影片／無骨架保護不足、visibility 未作逐關節門檻、缺點插值可能掩蓋遮擋、同 basename 覆寫、Dense 最多 30 格、混合比例影片拼圖裁切、缺 CLI 參數驗證。請依使用指南採人工備援；待實拍測試後再修正。

AI Coach 益力康陳董 x CGM Coach 血糖教練 | 2026 AI to Agent
