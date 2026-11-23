# BlackBear Science Video Skill V1.3 — 封版與回歸測試報告

**日期：2026-11-23**  
**版本：1.3.0；封版範圍：前製 A–C3 + 本機技術占位渲染。**

## 1. 測試範圍與結果

| 項目 | 結果 | 說明 |
|---|---|---|
| V1.3 單元、負向與交接驗證 | PASS 13/13 | 權利自動放行、原稿遭竄改、階段跳關、檢查點損毀、恢復、ZIP 驗證等 |
| V1.2 相容性回歸 | PASS 6/6 | 《尼莫點》舊格式仍可用 |
| 《尼莫點》原稿保護 | PASS 5/5 | 五份 original/ 位元組相同；未改旁白腳本 |
| 《尼莫點》108 鏡提示詞 | PASS 108/108 | 16 保留 + 92 填補（V1.2 既有成果） |
| 新題材 A→C3 | PASS | 3 鏡、20 秒、2 個官方科普來源，階段檔案與檢查點生成 |
| FFmpeg 畫面技術煙霧測試 | PASS | 新題材 20 秒、600 影格；《尼莫點》既有 27 秒、810 影格 |
| 兩題材 Handoff Gate | PASS_WITH_WARNINGS | 結構通過，但科學逐鏡人工審查與權利待補 |
| 兩題材 Production / Release Gate | BLOCKED | 預期行為，不能自動放行 |
| Claude Code／Codex 真正執行 | NOT TESTED | 當前執行環境沒有這兩個 CLI |
| Remotion npm 安裝與渲染 | NOT PASSED | npm registry DNS `EAI_AGAIN`，無法取得依賴 |

## 2. 封版決定

V1.3.0 **封版為「ChatGPT 前製 A–C3 + 本機可攜式交接」穩定技術版本**。不得宣稱它已完成 Claude Code／Codex 正式接手、Remotion render、科學內容逐句簽核、正式影片授權及發布驗收。

### 3. 仍需在使用者的 Claude Code／Codex 環境驗收

1. 解壓 C3 ZIP 並執行 `python scripts/audit_v13.py . --gate handoff`，回報 stdout/JSON。
2. 執行 `npm install` 並成功運行《尼莫點》CH01 Remotion 預覽；保存 package-lock 和實際版本。
3. 提供 ffprobe 影片影格、聲音/字幕 QA 以及素材來源；如仍無正式權利與科學簽核，保持正式 production/release blocked。
4. 提供含 CLI 版本、執行日誌、影片 SHA-256 的真人可核對執行紀錄，之後才能另標註 `external_agent_e2e_verified`。

**所有原始腳本仍以 V1.2 為主，並未重寫。**
