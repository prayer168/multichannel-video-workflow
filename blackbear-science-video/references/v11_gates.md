# V1.1 閘門規格

- handoff: 檔案完整、原稿 hash 不變、欄位關聯與時間軸正確；缺圖、缺 prompt、科學/授權未審可作警告，僅供交接，不得成片發布。
- production: 所有鏡頭具提示詞、實際素材、逐句主張查證及素材權利放行後才可啟動正式渲染。原創尚未生成不等於 cleared。
- release: production 全部通過，另外提供 `reports/release_evidence.json`，人工同意科學、授權、配音對時、字幕與實際輸出。不可自行製造核准紀錄。
- 保護原稿: lock 為編輯者已接受的 hashes，審計工具僅讀取，絕不自動刷新。
- asset local_path 應為相對專案路徑，不可引入外部路徑。當前工具只檢查檔案存在，尚不能審查真實授權真偽；請人工確認 license_evidence。
