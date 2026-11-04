// timeline.js — 試跑：白板手繪＋右下黑熊。畫面、音效與 QA 共用同一張時間表。
// 句段時間來自核定 Achird 樣本（S01 前 14.3 秒）的停頓偵測，不是逐字轉寫。
export const BPM = 120;
export const BEAT = 60 / BPM;
export const BAR = BEAT * 4;
export const b = n => n * BEAT;
export const revealOn = (hit, dur, reveal = 0) => hit - reveal * dur;

export const DUR = 14.6;

// 旁白句段（秒）
export const SEG = {
  a: [0.0, 2.0], b: [2.36, 3.28], c: [3.8, 9.54], d: [10.02, 12.48], e: [12.79, 14.09],
};

export const SHOTS = [
  { id: 'bird', t0: 0, t1: 3.8 },      // 白板畫出黑面琵鷺，圈出湯匙嘴
  { id: 'map', t0: 3.8, t1: 12.6 },    // 鏡頭沿白板右移：示意路線從北方畫到台南
  { id: 'overview', t0: 12.6, t1: DUR } // 拉遠成一張關係圖，停留
];

// 畫面事件與音效：放在句段停頓或句尾，避開句首與關鍵詞
export const CUES = [
  { t: 3.3, sfx: 'pop' },     // b 句尾停頓：圈注完成
  { t: 9.56, sfx: 'tick' },   // c 句尾停頓：箭頭落定
  { t: 12.55, sfx: 'pop' },  // d、e 之間停頓：底線畫完
];

export const HOLDS = [[13.7, DUR]];
export const DROPS = [];
