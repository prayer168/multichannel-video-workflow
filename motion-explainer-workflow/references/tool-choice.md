# Remotion 與 HyperFrames 的選用時機（第 4 步實測，2026-10-22）

## 實測條件
- 影片：《地球離太陽最近，為什麼是冬天？》，紙張畫布＋虛擬攝影機風格，60 fps。
- 同一鏡：台北正午筷子影子模擬（7 秒，太陽高度 41.5° → 88.4°，影長依 20 ÷ tan(高度) 計算）。兩邊都用同一份畫面程式 `shadowSVG(w, h, t)`，只換外殼。
- 環境：雲端容器（2 核心、軟體繪圖），兩者都改用容器內預裝的 Chromium（HyperFrames：`HYPERFRAMES_BROWSER_PATH=<chrome>`；Remotion：`--browser-executable=<chrome-headless-shell>`，一般 chrome 會因「舊 headless 模式已移除」而啟動失敗）。

## 結果

| 項目 | HyperFrames 0.8.183 | Remotion 4.0.537 |
|---|---|---|
| 外殼寫法 | 一個 `index.html`：根節點 `data-composition-id`、`data-duration`；GSAP 暫停時間軸註冊到 `window.__timelines`，`onUpdate` 呼叫畫面函式 | React：`Composition`（fps、幀數）＋元件用 `useCurrentFrame()/fps` 換算秒數，再呼叫畫面函式 |
| 建置 | 不需要；`npx hyperframes render --fps 60` | 需 `npm install`（254 個套件）＋打包 |
| 7 秒 60 fps 渲染時間 | 41 秒（截圖模式，未用 BeginFrame） | 47 秒（concurrency 2） |
| 預設幀率 | 30（**要加 `--fps 60` 或根節點 `data-fps`**） | 由 `Composition fps` 決定 |
| 同時刻畫面差異 | 平均每像素差 1.0／255，0.27% 像素差超過 24：肉眼看不出 | — |

## 選用原則（取代 SKILL.md 的暫定原則）
1. **畫面程式先寫成「給時間 t 就畫出畫面」的純函式**（HTML／SVG 字串），不綁任何框架。這次整支主片就是這樣寫成 `comp.html` 的 `setT(t)`，用 Playwright 逐幀擷取（4 個並行，13,067 幀約 6 分鐘）；同一個函式包進 HyperFrames 或 Remotion 外殼，畫面幾乎一模一樣。
2. **預設用 HyperFrames**：不必建置、外殼一個 HTML 檔、與 `setT(t)` 寫法最接近；記得 `--fps 60`。
3. **改用 Remotion 的時機**：需要 React 元件重用（大量同型卡片、資料驅動的表格），或要用 Remotion 生態（字幕元件、Lambda 雲端渲染）時。授權：個人與 3 人以下團隊免費。
4. 在雲端容器渲染時，三種做法都要指定容器內的 Chromium；在使用者 Windows 上則用 `setup_windows.bat` 裝好的瀏覽器。
5. 不論哪個工具，品牌層（黑熊片頭、講課角色、片尾、配樂）仍由主技能的 `bear_presenter.py` 與 ffmpeg 接合，不在畫面程式裡重做。
