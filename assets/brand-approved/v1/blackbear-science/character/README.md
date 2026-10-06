# Black Bear Teacher｜黑熊老師

可重複使用的分層 SVG 角色與輕量 2D 動畫控制。造型依 `../造型候選/黑熊老師角色表情與姿勢圖鑑.png` 整理為正面基礎姿勢：深藍黑色圓頭、灰色耳內、淺色口鼻、圓框眼鏡、藍色外套、白色 V 型胸斑及熊掌徽章。每個身體部位和表情零件保留為獨立 SVG 群組或 path，沒有 Canvas 或點陣化。

## 開啟角色

在此資料夾啟動簡易本機伺服器，再瀏覽 `http://localhost:8000`：

```bash
python -m http.server 8000
```

瀏覽器直接以 `file://` 開啟時，部分瀏覽器會阻擋載入外部 `character.svg`；使用本機伺服器即可。若只要檢視靜態角色，也可直接開啟 `character.svg`。

## Demo 控制面板

`index.html` 提供表情、嘴型、眨眼、說話和手勢按鈕。按 Talk 開始循環嘴型，再按 Stop Talk 停止。角色載入後預設每 3–6 秒眨眼。

## JavaScript API

```js
BlackBearTeacher.setExpression("thinking"); // normal, talking, surprised, thinking, panic, wink, sad
BlackBearTeacher.setMouth("A");              // closed, small, A, O（另有 frown、wobble 供表情使用）
BlackBearTeacher.clearMouth();               // 取消強制嘴型，回到表情預設
BlackBearTeacher.blink();
BlackBearTeacher.startAutoBlink();
BlackBearTeacher.stopAutoBlink();
BlackBearTeacher.startTalking();
BlackBearTeacher.stopTalking();
BlackBearTeacher.setGesture("wave");         // idle, wave, point, thinking, celebrate, panic
```

也提供全域別名 `setExpression()`、`setMouth()`、`blink()`、`startAutoBlink()`、`stopAutoBlink()`、`startTalking()`、`stopTalking()`、`setGesture()`。`blink(durationMs)` 預設 150 ms。

## 影片逐格錄製（可重現）

所有動態（眨眼、擺手、呼吸、點頭、手臂轉換）都由同一個時鐘 t（秒）計算，眨眼間隔是固定種子的偽隨機，所以同一個 t 一定畫出同一格：

```js
BlackBearTeacher.useManualClock(true);
// 每一格：
BlackBearTeacher.pose({ expression: "talking", gesture: "point", talking: true, level: 0.42 });
BlackBearTeacher.tick(12.3667);   // 影片時間（秒）
```

`level` 是該格配音音量（0～1），自動換成嘴型：< 0.08 閉嘴、< 0.30 小開、其餘 A／O。

## SVG 圖層

所有圖層均位於 `#character` 下（viewBox `-80 -10 560 530`，留空間給手勢與教鞭）。

| ID | 用途 |
| --- | --- |
| `body_all` | 身體整組（呼吸位移） |
| `body` | 軀幹與深色內搭 |
| `legs` | 左右腿與腳 |
| `head_all` | 頭部整組（點頭、歪頭） |
| `head` | 熊頭輪廓 |
| `ears`、`ear_left`、`ear_right` | 左右耳與內耳色塊 |
| `eyebrows`、`eyebrow_left`、`eyebrow_right` | 表情眉毛 |
| `eyes`、`eye_left`、`eye_right` | 眼白、瞳孔和高光 |
| `eye_left_closed`、`eye_right_closed`、`eye_right_wink` | 閉眼／眨眼線條 |
| `glasses` | 眼鏡鏡框與鼻樑 |
| `muzzle` | 淺色口鼻、鼻子和人中 |
| `mouth`、`mouth_closed`、`mouth_small`、`mouth_A`、`mouth_O`、`mouth_frown`、`mouth_wobble` | 獨立嘴型 |
| `chest_mark` | 白色 V 型胸斑 |
| `jacket` | 外套、衣襟、口袋、排扣與羅紋 |
| `arm_left`、`arm_right` | 左右手臂（原點＝肩膀，JS 設定旋轉） |
| `hand_left`、`hand_right`、`pointer` | 手掌與教鞭 |
| `accessories`、`paw_badge` | 配件群組與胸前熊掌徽章 |
| `fx`、`fx_sweat`、`fx_sparkle`、`fx_shock`、`fx_think` | 汗滴、星光、驚嚇線、思考泡泡 |
| `front_layer` | 手要擋在臉前（thinking、panic）時，手臂會移到這層 |

## 檔案

- `index.html` — Demo 與載入角色的頁面
- `character.svg` — 分層向量角色（由 `make_svg.py` 產生；改造型請改 `make_svg.py` 再執行）
- `character.css` — 容器與狀態樣式
- `character.js` — 表情、嘴型、眨眼、說話、手勢 API 與手動時鐘
- `sheet.py` — 產生 `角色總覽.png`（全部表情與手勢一張圖，檢查用）
