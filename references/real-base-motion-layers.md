# 真實底圖＋程式動態層分工

2026-11-25 使用者指定：影片裡的地圖、地景、天體、生物與實物，一律使用**真實地圖或可商用的圖片**當底圖；**Claude Code 只負責畫動態元件**。本規則適用兩個頻道，黑熊老師的自然教室必須遵守。它補充 [image-led-motion-graphics.md](image-led-motion-graphics.md) 的第 2、7 點，兩者衝突時以本檔為準。

## 1. 分工

| 圖層 | 內容 | 由誰提供 |
|---|---|---|
| 靜態底圖 | 地圖、衛星影像、海岸／地形、地球／月球／太陽、動植物、實物、地景照片 | 真實地圖或可商用圖片。找不到合用的真實素材，或是概念無法拍攝（例如「月亮消失後的海岸」）時，才用 ImageGen 等 AI 生成底圖，並在畫面標「示意」。 |
| 動態元件 | 隨旁白出現、移動或變化的元素：箭頭、定位點、路徑描繪、岸線高亮、長條／數值、引線與標籤、遮罩、可淡出的獨立圖層（例如月亮）、水面反光等微動效、運鏡（推、拉、平移）、轉場、標題、字幕、頻道角標 | Claude Code 以程式繪製，並對齊旁白時間。 |

- 程式**不從零畫**地圖、海岸線、行星、動物或地景來當主畫面。程式畫的卡通螃蟹、多邊形大陸、手畫港灣都屬於這一類，應改成真實素材。
- 純概念圖表本身就是動態元件，可以由程式繪製，例如從零起算的長條圖、座標軸、力的方向示意。圖上的數值仍須有來源。
- 需要從底圖抽出的獨立圖層（例如要淡出的月亮）也用真實或可商用影像，例如 NASA 月球照片去背，由程式控制透明度與位置。

## 2. 可商用來源清單

每次使用前都要開啟該素材的授權頁核對。清單只是起點，不代表每張圖都可用。

| 來源 | 適合用途 | 授權重點 | 署名範例 |
|---|---|---|---|
| Copernicus Sentinel-2（ESA）原始影像，可由 AWS Earth Search 或 Copernicus Browser 取得 | 10 m 衛星真彩影像：海岸、潟湖、河口、港灣 | 免費、可商用、可改作，須註明 | Contains modified Copernicus Sentinel data 2025 |
| USGS／NASA Landsat | 30 m 衛星影像、長期變化 | 美國政府作品，公有領域 | Landsat imagery courtesy of NASA／USGS |
| NASA 影像（Blue Marble、EPIC、LRO 月球、SDO 太陽、Visible Earth） | 地球、月球、太陽、太空視角 | 一般不受美國著作權保護。不可使用 NASA 標誌，不可暗示 NASA 背書；少數由第三方提供的圖片例外。 | Image: NASA |
| Natural Earth | 國界、海岸線、河流向量 | 公有領域 | Made with Natural Earth |
| GEBCO Grid | 全球水深地形 | 公有領域，須依其使用條款註明 | GEBCO Compilation Group (年份) GEBCO Grid |
| OpenStreetMap 資料（自行繪製，或使用允許的圖磚服務） | 街道、港口、地名 | ODbL，須標示，資料改作有相同方式分享的義務 | © OpenStreetMap contributors |
| 內政部國土測繪中心（NLSC）圖層、政府資料開放平臺 | 臺灣地圖、正射影像、地形 | 只用標明「政府資料開放授權條款第 1 版」的圖層，可商用並須標示。逐圖層核對，不是每個圖層都適用。 | 內政部國土測繪中心（政府資料開放授權條款第 1 版） |
| Wikimedia Commons | 物種、地景、實物照片 | 只用 CC0、公有領域、CC BY、CC BY-SA。CC BY-SA 的改作須以相同授權釋出，需要時先告知使用者。 | 作者／Wikimedia Commons／CC BY 4.0 |
| iNaturalist、Flickr | 物種照片 | 逐張確認，只用 CC0 或 CC BY。iNaturalist 預設是 CC BY-NC，不能商用。 | 作者／iNaturalist／CC BY 4.0 |
| ImageGen／Images 2.6 生成圖 | 無法拍攝的情境底圖 | 本頻道自產。畫面標「示意」，不冒充實景。 | （不需外部署名，標「示意」） |

**不使用（或需購買授權）**：Google Maps 與 Google Earth 截圖、Esri World Imagery、Mapbox／Bing 衛星圖、EOX Sentinel-2 cloudless 2017 年以後版本（非商用授權）、CC BY-NC 或 CC BY-ND 授權、一般圖片搜尋結果、只標「免費下載」的圖庫縮圖。

## 3. 製作流程

1. **列靜態底圖清單**：分鏡時逐鏡寫出要用的底圖，含地點、座標範圍或物種、建議來源與授權。
2. **下載前先取得同意**：向使用者列出檔名、來源網址、預估大小，取得同意後才下載。
3. **歸檔**：素材存到專案的 `assets/licensed/`。同時寫 `assets/licensed/sources.json` 與 `CREDITS.md`，每筆記錄來源頁網址、作者、授權名稱與版本、取得日期、原檔 SHA-256，以及本片的修改方式（裁切、調色、去背、合成）。
4. **處理底圖**：裁切、調色、去背都由程式重現，原檔不覆蓋。衛星影像要保留正確的方向與比例；需要放大時，要能看出是同一處的放大。
5. **動態層**：Claude Code 讀入處理後的底圖，只在上面畫動態元件，例如依旁白時間描出岸線、出現定位點、淡出月亮、推近港口。
6. **署名**：在畫面的不遮擋處標小字來源（例如左下「衛星影像：Contains modified Copernicus Sentinel data 2025」），並在片尾或說明欄列出完整 `CREDITS.md`。合成或 AI 生成的畫面另標「示意」或「示意合成」。
7. **驗收**：見第 4 節。

## 4. 驗收清單

- [ ] 每個地圖、地景、天體、生物畫面都來自真實或可商用素材，或是有標「示意」的 AI 生成圖。
- [ ] 程式畫的部分只有動態元件與概念圖表，沒有程式從零畫的地圖、地景或生物當主畫面。
- [ ] `sources.json` 和 `CREDITS.md` 涵蓋片中每一張外部素材，雜湊值和檔案相符。
- [ ] 每張素材的授權都允許商用與改作；CC BY-SA 素材已處理相同方式分享的義務。
- [ ] 畫面上的來源小字清楚可讀，不和字幕、熊掌角標重疊；說明欄附完整來源。
- [ ] 地名、方位、比例正確；示意範圍有標示。

## 5. 交接給 Claude Code 的場景格式

場景規格把底圖和動態層分開寫，Claude Code 只實作 `layers`：

```json
{
  "id": "geography",
  "base": [
    {"path": "assets/licensed/qigu-lagoon-s2.png", "credit": "Contains modified Copernicus Sentinel data 2025", "label": "七股潟湖"},
    {"path": "assets/licensed/tainan-open-coast-s2.png", "credit": "Contains modified Copernicus Sentinel data 2025", "label": "臺南開闊海岸"}
  ],
  "layers": [
    {"type": "trace_shoreline", "at": 50.25},
    {"type": "callout", "text": "潟湖口狹窄", "at": 51.521}
  ]
}
```

找不到合用的真實素材時，先停下來告訴使用者缺哪一鏡、試過哪些來源，再提出 AI 示意底圖的替代方案，不要自行改用程式畫的地景。
