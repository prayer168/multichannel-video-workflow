# Studio 操作與復原

## 頻道與初次使用

1. 使用可用瀏覽器進入 `https://studio.youtube.com/`。依工具實際快照定位控制項，不硬編座標或沿用失效的選取器。登入、雙重驗證、驗證碼交由使用者完成；不要要求密碼出現在聊天中。
2. 檢查頭像選單與頻道頁／Studio URL，記錄實際頻道名稱、handle（可取得時）及 `UC…` ID。名稱相近或有多個品牌帳戶時，以 ID 對照。首次目標不明先詢問；已核定對照存到專案或使用者指定的設定位置。
3. 不編造兩個品牌的實際 ID；現有製作流程中的 `blackbear-science`／`ai-watch` 只是內部代號。未核實前不得發布。
4. 檢查專案 state 與頻道內容清單，確認先前是否已上傳／發布。第一次建立連線不代表已有待發布專案。

## 每支上傳

- 點建立／上傳影片，用工具支援的檔案選取介面選本支正式檔。取得 ID／影片連結後立即存 state。
- 填各自標題、說明欄、Tags，對照原始文案；不可將 Hashtag 全當成 Tags。依交付補影片語言、字幕、自訂縮圖、明確指定的播放清單，以及有依據的兒童／合成揭露設定。
- 中文與英文字幕各用自己的字幕檔；字幕不可憑檔案存在就聲稱已發佈。檢查字幕軌是否實際儲存。流程必須在上傳後才可補時，先記待補，再完成字幕頁。
- 等待上傳完成及可播放處理狀態、檢查頁結果。明確封鎖、失敗或需決策的著作權聲明只阻擋該支；不要擅自提出爭議或接受會改變權利／營利的選項。其他可獨立處理的影片仍可準備；主片未取得可用網址時不要發布帶未解占位符的 Shorts。
- 公開模式選「公開」並發布；不要建立首播或排程。使用者改為排程時保留其指定時間，採 `Asia/Taipei` 顯示並核對平台時區，設定完成記 `scheduled`，不記成已公開。
- 點發布前寫 `publish_pending`。點後查看成功對話、內容清單或詳情，核對 ID、標題、可見度；可用時再打開觀看頁確認可播放。只看到進度 100% 不算公開。
- Shorts 發布後到內容詳情設定「相關影片」，選同頻道已公開主片並儲存；無功能就記 `unavailable` 及原因。Shorts 超過一分鐘且有有效 Content ID 聲明時，依官方說明可能全球封鎖，不宣稱可正常觀看。
- 截至查閱日期，官方說明已支援在電腦 Studio 的「內容 → Shorts → 詳情 → 縮圖 → 上傳檔案」新增自訂縮圖，需要帳戶驗證，建議 9:16。有交付縮圖就嘗試此功能並核實儲存；實際帳戶尚無此介面時記限制。不要為了自訂封面擅自修改影片或要求安裝手機模擬器。

## 狀態與避免重複

`youtube-publish-state.json` 至少包含批次 ID、channel ID、更新時間與每支以下欄位：

```json
{
  "id": "short-1",
  "source_path": "absolute path",
  "sha256": "local file fingerprint",
  "video_id": null,
  "url": null,
  "stage": "prepared",
  "visibility_verified": null,
  "last_checked_at": null,
  "subtitles": "pending",
  "thumbnail": "pending",
  "related_video": "pending",
  "error": null
}
```

stage：`prepared`、`uploading`、`uploaded`、`publish_pending`、`published`、`scheduled`、`blocked`、`uncertain`。配件狀態獨立，可為 `pending`、`done`、`not_requested`、`unavailable`、`failed`。每次更新使用暫存檔加原子替換，保留既有 video ID；不要覆蓋同批次其他項目。寫入失敗就停止新的發布，先修復追蹤記錄。

對照鍵為 channel ID + manifest item ID + 成片 SHA-256。相同檔案在同頻道已有 ID 時先核實，不因改名重傳。相同 item ID 但檔案指紋改變時不得沿用舊片狀態，要釐清是否是新版及是否真的要另上傳。

重新開始時：有 video ID 就先開該片 Studio 詳情。已公開只補未完成項；仍為私人／草稿則續填同一筆。上傳後尚無 ID 且連線中斷，先以來源檔名、標題、時間、片長找回；無法排除已上傳時回報 `uncertain`，不自動另傳。清楚未開始上傳的暫時性 UI 錯誤最多重試兩次，之後停止該項並回報。

結果報告列出每支 URL、實際可見度、字幕、縮圖、Shorts 相關影片與未完成原因。主片網址建立後可回填同專案上架文案中的長片連結占位符；不順便發送臉書貼文或其他平台內容。

## 現行規則的官方依據

查閱日期：2026-11-04。平台功能變動或介面與記錄不一致時重查官方說明。

- [上傳影片](https://support.google.com/youtube/answer/57407?hl=zh-Hant)
- [3 分鐘 Shorts 分類及 Content ID 限制](https://support.google.com/youtube/answer/15424877?hl=zh-Hant)
- [Shorts 相關影片：需要進階功能，目標必須公開或不公開](https://support.google.com/youtube/answer/14075157?hl=zh-Hant)
- [判定兒童專屬內容](https://support.google.com/youtube/answer/9528076?hl=zh-Hant)
- [揭露變造或合成內容](https://support.google.com/youtube/answer/14328491?hl=zh-Hant)
- [影片縮圖與 Shorts 封面](https://support.google.com/youtube/answer/72431?hl=zh-Hant)

若未來改用 Data API，要另行具備 OAuth 與相應權限，核實 API 專案的上傳／公開限制及各功能支援；不能只拿 API key 上傳，也不能假設 API 可設定 Shorts 相關影片。現行技能不儲存任何密碼或 token。
