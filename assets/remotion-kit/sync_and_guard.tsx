// 從《如果洋流停止了》production/remotion/src/common.tsx 摘出：逐字同步 kwAt、彈出動畫、文字重疊守門員
// 使用前 import：React, {useLayoutEffect}；remotion 的 cancelRender, getRemotionEnvironment, interpolate, spring, useCurrentFrame, useVideoConfig
// from 一律是全片絕對影格（build_timing.py 產生）；ct＝每個字相對該句配音起點的實際發音影格（char_marks.py 寫入）
export type TimingEvent = {kind: 'teacher'; id: string; text: string; file: string; from: number; dur: number; ct?: number[]};
export type TimingShot = {id: string; from: number; dur: number; events: TimingEvent[]; visual: string; asset_type: string};
export type Timing = {total: number; shots: TimingShot[]};

// 動畫提前量：彈出動畫約 6 格才看得清楚，場景裡也常有 +8 格的連鎖延遲 → 關鍵詞觸發點提前 10 格（0.33 s）
// 2026-11-26 使用者：旁白比畫面早約 1 秒（原因：字數比例估計誤差最大 1.8 s＋動畫延遲）
export const LEAD = 10;

// 旁白關鍵詞在鏡內的觸發影格：有 ct 用實際發音時間，否則退回字數比例估計；找不到回傳 fallback
export const kwAt = (shot: TimingShot, word: string, fallback = 0) => {
  for (const e of shot.events) {
    const i = e.text.indexOf(word);
    if (i >= 0) {
      const rel = e.ct ? e.ct[i] : Math.round((e.dur * i) / e.text.length);
      return Math.max(1, e.from - shot.from + rel - LEAD);   // 至少第 1 格：場景常用 interpolate(f, [0, kw])，0 會讓區間不遞增而中止渲染
    }
  }
  return fallback;
};

// 版面登記：文字標 data-box="text"、圖形標 data-box="graphic"。
// 每一格比對實際外框，文字與任何其他已登記元件重疊（且雙方都看得見）就中止渲染（使用者規定重疊數 0 才渲染）
const visible = (el: Element) => {
  for (let n: Element | null = el; n; n = n.parentElement) {
    const o = parseFloat(getComputedStyle(n).opacity);
    if (o < 0.08) return false;
  }
  return true;
};
export const OverlapGuard: React.FC<{tag: string}> = ({tag}) => {
  const f = useCurrentFrame();
  useLayoutEffect(() => {
    const els = [...document.querySelectorAll('[data-box]')].filter(visible);
    const rects = els.map((e) => ({e, r: e.getBoundingClientRect(), k: e.getAttribute('data-box'), id: e.getAttribute('data-id')}));
    for (let i = 0; i < rects.length; i++)
      for (let j = i + 1; j < rects.length; j++) {
        const a = rects[i], b = rects[j];
        if (a.k !== 'text' && b.k !== 'text') continue;
        if (a.e.contains(b.e) || b.e.contains(a.e)) continue;
        const w = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
        const h = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
        if (w > 0 && h > 0) {   // 任何重疊都算：門檻不隨 --scale 改變（2026-11-25 4K 才抓到 1 px 重疊）
          const box = (r: DOMRect) => `[${Math.round(r.left)},${Math.round(r.top)} ${Math.round(r.width)}×${Math.round(r.height)}]`;
          const msg = `OVERLAP ${tag} f${f}: ${a.id}${box(a.r)} × ${b.id}${box(b.r)}`;
          if (getRemotionEnvironment().isRendering) cancelRender(new Error(msg));
          else console.error(msg);
        }
      }
  });
  return null;
};

// 有登記的文字塊
export const T: React.FC<{id: string; style: React.CSSProperties; children: React.ReactNode}> = ({id, style, children}) => (
  <div data-box="text" data-id={id} style={{position: 'absolute', fontFamily: FONT, ...style}}>{children}</div>
);
export const G: React.FC<{id: string; style: React.CSSProperties; children: React.ReactNode}> = ({id, style, children}) => (
  <div data-box="graphic" data-id={id} style={{position: 'absolute', ...style}}>{children}</div>
);

// 彈出：at 影格起 spring 放大，可選 until 影格淡出
export const usePop = (at: number, until?: number) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f - at, fps, config: {damping: 14, stiffness: 190}});   // 約 8 格到位（原約 20 格）
  const out = until === undefined ? 1 : interpolate(f, [until, until + 10], [1, 0], clamp);
  return {opacity: Math.min(1, s * 1.4) * out, scale: 0.6 + 0.4 * s};
};

