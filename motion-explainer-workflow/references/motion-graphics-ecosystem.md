# 開源 Motion Graphics 工具與工作流生態

本清單供動態圖文分鏡選型、研究與逐項安裝使用，並不表示所有專案已安裝到電腦。這 25 個 repo 包含獨立桌面程式、框架、程式庫與技能／範例，彼此不能當成同一種套件安裝。星數是 GitHub API 在 2026-11-03 擷取的快照，會變動；授權欄依 repo/API 當時可辨識的資訊標示，正式使用前仍要讀 repo 的 LICENSE 與第三方素材授權。

## 依分鏡挑工具

1. **本技能預設交付**：HyperFrames。已在 Windows 安裝流程中支援，適合 HTML／SVG／CSS／GSAP 的版面動畫與逐幀可尋畫面。
2. **資料驅動版型、React 元件重用**：Remotion。已納入 Windows 安裝流程；依公司／團隊使用情境先確認 Remotion 授權。
3. **科學與數學概念**：Manim Community；若動畫要進入教學片，可輸出透明背景或序列素材，再由主流程合成。
4. **自訂 2D／3D 畫面**：three.js 或 PixiJS 作為畫面引擎，由 HyperFrames／Remotion 負責影片時間與輸出。
5. **要編輯器、合成或傳統動畫軟體**：Graphite、EffectCraft、Friction、Natron、OpenToonz、Motionity、Astrofox 分別在專屬軟體內製作，再匯出素材交給主流程；先確認安裝包、格式支援及維護狀態。
6. **只需網頁小動畫或向量動畫播放**：Motion、Lottie Web、GSAP、mojs、Theatre.js 等是輔助程式庫／編輯器，不能取代影片輸出器。
7. **製作配方／Agent 工作流**：video-shotcraft、motion-skills、OpenFilm、OneTake、awesome-video-skills 提供流程、技能或參考。閱讀後只吸收可重用方法；不得將第三方 repo 的技能原文、提示詞、素材或程式碼直接複製進本技能。
8. **效能／Python 特殊用途**：fframes 與 Movis 可做候選渲染管線；先用本片實際字型、音訊、字幕、60fps 與中文輸出做小段驗證，再考慮替換既有渲染流程。

### 排序清單（星數由高至低）

| # | Repo | 星數 | 定位／工作流入口 | 授權／注意事項 |
|---:|---|---:|---|---|
| 1 | [three.js](https://github.com/mrdoob/three.js) | 117,448 | JavaScript 3D 圖形引擎；用於 3D 場景與動態主視覺 | MIT；npm `three` |
| 2 | [HyperFrames](https://github.com/heygen-com/hyperframes) | 77,770 | HTML/CSS 轉影片；本技能預設渲染路線 | Apache-2.0；既有安裝器已支援 |
| 3 | [Remotion](https://github.com/remotion-dev/remotion) | 70,123 | React 程式化影片；資料驅動卡片與元件重用 | repo 未辨識 SPDX；依 Remotion 官方授權條款核對；既有安裝器已支援 |
| 4 | [PixiJS](https://github.com/pixijs/pixijs) | 48,620 | 2D GPU 渲染引擎；粒子、動態插圖、互動畫面 | MIT；npm `pixi.js` |
| 5 | [Manim Community](https://github.com/ManimCommunity/manim) | 42,166 | Python 數學／科學動畫 | MIT；需 Python 與系統圖形相依套件 |
| 6 | [Motion](https://github.com/motiondivision/motion) | 34,819 | React／JavaScript UI 動畫 | MIT；npm `motion`，不是獨立影片輸出器 |
| 7 | [Lottie Web](https://github.com/airbnb/lottie-web) | 32,335 | 播放 AE 匯出的 Lottie 向量動畫 | MIT；npm `lottie-web` |
| 8 | [GSAP](https://github.com/greensock/GSAP) | 30,078 | 時間軸、文字及網頁物件動畫 | repo 未回報 SPDX；核對 GreenSock 當前授權；HyperFrames 可承載 GSAP 時間軸 |
| 9 | [Graphite](https://github.com/GraphiteEditor/Graphite) | 27,824 | 節點式 2D 設計與程序化圖形 | Apache-2.0；桌面／Web app，檢查官方安裝方式與功能成熟度 |
| 10 | [Motion Canvas](https://github.com/motion-canvas/motion-canvas) | 19,657 | TypeScript 動畫場景與即時預覽編輯器 | MIT；獨立場景／渲染管線，先試作再選用 |
| 11 | [mojs](https://github.com/mojs/mojs) | 18,874 | Web motion graphics 工具組 | MIT；npm `mo-js`；repo 使用狀態先核對 |
| 12 | [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 16,200 | 分鏡配方、預覽與 Remotion 製作技能 | Apache-2.0；以方法參考為主，勿直接複製其技能內容 |
| 13 | [Theatre.js](https://github.com/theatre-js/theatre) | 12,846 | Web 動態設計時間軸／編輯器 | Apache-2.0；確認目前維護與適用版本 |
| 14 | [EffectCraft](https://github.com/storytold/effectcraft) | 8,355 | Rust 動態圖形與合成桌面工具 | repo 標示 Apache-2.0；新興專案，先以非正式素材試用 |
| 15 | [OpenToonz](https://github.com/opentoonz/opentoonz) | 7,902 | 2D 動畫製作軟體 | repo 未辨識 SPDX；讀取 LICENSE 及第三方素材條款 |
| 16 | [Natron](https://github.com/NatronGitHub/Natron) | 5,628 | 節點式合成與視覺特效 | GPL-2.0；匯出中間素材再接主流程 |
| 17 | [OpenFilm](https://github.com/openfilm/openfilm) | 4,285 | AI 影片 agent 與可編輯成品工作流 | MIT；以外部流程參考為主，確認依賴與資料安全 |
| 18 | [Motionity](https://github.com/alyssaxuu/motionity) | 4,141 | 瀏覽器動態圖形編輯器 | MIT；專案曾長期少有更新，先確認可安裝性 |
| 19 | [OneTake](https://github.com/feitangyuan/onetake) | 3,650 | 連續鏡頭產品片的 agent 製作流程 | repo 未辨識 SPDX；只參考公開概念，勿直接再散布程式碼／素材 |
| 20 | [fframes](https://github.com/dmtrKovalenko/fframes) | 3,142 | Rust 程式化影片渲染框架 | MIT；需單獨評估中文字型與輸出支援 |
| 21 | [Astrofox](https://github.com/astrofox-io/astrofox) | 2,010 | 音訊反應式動態圖形桌面程式 | MIT；適用音樂視覺化，非一般旁白片主渲染器 |
| 22 | [Friction](https://github.com/friction2d/friction) | 1,871 | 2D 向量動態圖形與影片輸出桌面程式 | GPL-3.0；安裝／匯出後再合成 |
| 23 | [motion-skills](https://github.com/iart-ai/motion-skills) | 1,165 | AI agent 動態設計技能與工作流集合 | MIT；只作技能／範例參考，保留來源與授權告知 |
| 24 | [remotion-bits](https://github.com/av/remotion-bits) | 505 | Remotion 圖表、轉場與文字元件 | API 未回報 SPDX；使用前讀 repo LICENSE，抽查元件品質 |
| 25 | [Movis](https://github.com/rezoo/movis) | 487 | Python 影片與動態圖形程式庫 | MIT；repo 更新較少，先驗證相依版本與輸出 |

## 安裝與引入規則

- 既有 `setup_windows.bat`／`install_windows.ps1` 只安裝本流程實際支援的 Remotion、HyperFrames、Chromium、Node／FFmpeg 與必要字型；本版**不會在背景自動下載或安裝其他 23 個專案**。
- JavaScript 引擎／動畫程式庫須在某個影片專案內由使用者明確選擇後，用該專案的 package manager 安裝；不可把所有依賴塞進共用 production `package.json`。採用前逐一比對其授權、Node 相容性與 bundle 大小。
- 桌面程式由官方 Releases／官網安裝，不在本技能安裝器中靜默執行安裝包，也不 clone 整份 source 當作安裝。選定一個工具後，確認下載來源、作業系統、簽章／雜湊（官方有提供時）、授權與卸載方式。
- Manim／Movis／fframes 等其他 runtime 只有在分鏡需要且使用者選定時建立隔離環境；先做 5–10 秒、60fps 或目標幀率的中文試片，檢查音訊、透明背景、字型、色彩與可重現性。
- 若外部技能或模板含提示詞、字體、圖片、音樂、片段或品牌內容，需另外檢查每項素材授權；repo 的程式碼授權不自動涵蓋其素材。
- 第三方 repo 或服務升級時重新查官方文件；星數不代表品質、活躍度、授權相容性或可直接投入商業製作。

## 與本技能的整合界線

全片仍由主技能負責頻道設定、查證、腳本、配音、品牌資產、SRT、實證比例及上架驗收。本子技能從旁白定稿後選擇分鏡引擎；首段試作與靜幀審查通過後才擴片。不同引擎輸出統一交給 `video-editing-workflow`／主流程合成，不得自行重做核定片頭、片尾、角色、配樂或燒錄字幕。新增引擎需先加入 `tool-choice.md` 的實測紀錄，再調整預設工具。
