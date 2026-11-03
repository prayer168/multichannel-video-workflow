# Awesome AI Motion 雙 repo 整合指引

本工作流安裝並整合兩個同名 repo；兩者用途不同，使用時先按任務選庫。資料來源以官方 GitHub repo 為準。repo 星數會變動，不作為品質或授權依據。

## 已安裝位置

預設安裝到 `%USERPROFILE%\AI-Video-Tools\motion-explainer\ecosystem\awesome-ai-motion\`：

| 目錄 | 上游 repo | 用途 | 授權與素材界線 |
|---|---|---|---|
| `guanmo-ai\` | [guanmo-ai/awesome-ai-motion](https://github.com/guanmo-ai/awesome-ai-motion) | 作品畫廊與搜尋索引；按知識講解、產品宣傳、角色、交互、敘事、音樂等形式找視覺參考 | 自編程式／文件為 MIT；第三方作品、音軌、封面、提示詞和品牌素材不由 MIT 授權。必須保留作者來源；公開不等於可重製或商用 |
| `gongnyang\` | [gongnyang/awesome-ai-motion](https://github.com/gongnyang/awesome-ai-motion) | 637 項效果卡、已渲染參考、動效配方與設計路線；含可供 Codex 參考的上游 `SKILL.md`，可用於挑選與短片試作 | repo 原始程式／文件為 MIT；`lib/` 第三方檔案保留各自授權，見其 `ATTRIBUTIONS.md`；參考素材亦須依條目來源核對 |

數量、卡片與授權內容以上游當前版本為準；安裝時採淺層 clone，保留各 repo 自帶的 LICENSE、ATTRIBUTIONS 與來源連結。使用者可在本機瀏覽 GitHub Pages；本技能不把 repo 的原始案例、提示詞、預覽影片、封面或字體匯入技能 repo，也不將它們當作本頻道可發布素材。

## 路由與使用步驟

1. 腳本定稿後先依 `studio-style-production.md` 定義這一鏡的溝通目的、觀眾應看見／理解的事物和實證需求。
2. 到 `guanmo-ai` 畫廊找相近媒介或敘事方式；讀案例的作者、來源與權利資訊。只把參考轉成抽象設計意圖，例如「由整體推近細節」或「用一個形狀串接資訊」，不可照搬片段、原提示詞或品牌識別。
3. 若需要具體動作，再到 `gongnyang` 的決定表選 2–3 張效果卡，讀效果目的、預設參數、限制和來源；需要組合時再讀 recipe／route。優先從 repo 已標記 rendered/done 的案例選，確認 HTML template 存在後再複製。
4. 把範例複製到單集專案的 `製作中/動態參考試作/`，在複本中替換文字、圖表與素材。輸出一段 5–10 秒短片至 `製作中/動態參考試作/輸出/`，不要向上游範例資料夾輸出，以免覆蓋原檔。
5. 經人工審查可讀性、旁白同步、繁體中文字型、幀率、字幕安全區、品牌、實證比例及素材授權；通過後才把設計意圖改寫為本技能的風格卡／分鏡並用 HyperFrames 或 Remotion 重製。上游範例 renderer 只負責短片預覽，不自動取代正式主片渲染管線。
6. 不需 Codex 以外的額外全域 skill 安裝：主技能會在上述需求時指向已安裝的 repo 與其特定檔案。只有使用者要求獨立叫用上游 `SKILL.md` 時才另行註冊成 Codex skill，避免重複路由或上游規則覆蓋本技能設定。

## 安裝、更新與檢查

- Windows 預設安裝：執行 `scripts/install_motion_reference_repos.ps1`。只會把兩個 repo clone 到上述 ecosystem 資料夾；已有 checkout 會保留並略過，不清除資料、不覆寫現存非 Git 資料夾。要更新時先進入相應資料夾，確認工作樹乾淨後手動 `git pull --ff-only`。
- 上游安裝說明：Guanmo 畫廊本機預覽用 Node.js 22+ 執行 `node scripts/serve.mjs`，不需 npm 相依安裝。Gongnyang 瀏覽／讀卡／使用 Skill 不需安裝相依；只在做本機渲染時檢查 Node.js 20+、FFmpeg、Playwright 與 Chromium，缺少時依 repo README 指示安裝。
- 本機 checkout 只是查閱來源；使用其中任一程式碼、素材、提示詞、音訊、圖片或字體前，依該檔案及上游授權／署名文件重新核對，不把 GitHub 星數視為授權。
- 新版引入效果需記錄來源 repo、路徑／slug、檢查日期、授權判定、中文 5–10 秒樣片與人工審片結論；未做實測不得宣稱效果在主流程中已驗證。
