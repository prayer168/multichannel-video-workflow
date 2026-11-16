// 旁白同步元件庫（2.30.0）：每個元件都是「給時間 t 就回傳那一刻的 SVG 字串」的純函式。
// 時間只從 words.json 的落點來（`N02@風化`），不手寫秒數；動作在落點前 LEAD 秒起勢、落點後 TAIL 秒完成，
// 所以變化的中點正好在關鍵詞開口那一刻。規則與來源見 ../../references/narration-sync-components.md。
(() => {
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const back = x => { x = clamp(x); const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const lerp = (a, b, k) => a + (b - a) * k;
  const LEAD = 0.2, TAIL = 0.15;
  // 落點 at 的動作進度 0→1；at 為 null（尚未定義）時永遠 0
  const prog = (t, at, dur = LEAD + TAIL) => at == null ? 0 : clamp((t - (at - LEAD)) / dur);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // 和 scripts/build/narration_word_timing.py 的 resolve() 同一套寫法：S03／S03$／S03@詞／S03@詞#2
  const KEEP = /[一-鿿㐀-䶿0-9A-Za-z]/;
  function resolver(words) {
    const byId = Object.fromEntries(words.sentences.map(s => [s.id, s]));
    return anchor => {
      const m = /^([^@$#]+?)(?:(\$)|@([^#]+)(?:#(\d+))?)?$/.exec(anchor.trim());
      const s = m && byId[m[1]];
      if (!s) throw new Error('沒有這個落點：' + anchor);
      if (m[2]) return s.end;
      if (!m[3]) return s.start;
      const plain = s.chars.map(c => c.c).join(''), key = [...m[3]].filter(c => KEEP.test(c)).join('');
      let k = -1;
      for (let n = +(m[4] || 1); n > 0; n--) { k = plain.indexOf(key, k + 1); if (k < 0) throw new Error(`${s.id} 裡沒有「${key}」#${m[4] || 1}`); }
      return s.chars[k].t;
    };
  }

  // 常駐章節導覽：已講過的打勾、正在講的亮起；觀眾隨時知道講到哪
  function tabs({ t, x, y, items, w = 250, h = 64, gap = 18, T }) {
    let cur = -1;
    items.forEach((it, i) => { if (t >= it.at - LEAD) cur = i; });
    return items.map((it, i) => {
      const k = ease(prog(t, it.at)), done = i < cur, on = i === cur;
      const px = x + i * (w + gap);
      const fill = on ? T.accent : done ? T.card : T.paper, txt = on ? T.paper : done ? T.ink : T.mute;
      return `<g opacity="${lerp(0.55, 1, k)}">
        <rect x="${px}" y="${y}" width="${w}" height="${h}" rx="${h / 2}" fill="${fill}" stroke="${on ? T.accent : T.line}" stroke-width="3"/>
        <text x="${px + w / 2}" y="${y + h / 2 + 12}" font-size="34" font-weight="700" fill="${txt}" text-anchor="middle">${done ? '✓ ' : ''}${esc(it.label)}</text></g>`;
    }).join('');
  }

  // 先排版位再填內容：句子一提到「有幾樣」就把空位全排好（問號），講到哪一樣才翻成內容，中途不重排
  function slots({ t, x, y, w, h, gap, appear, items, T, icon }) {
    return items.map((it, i) => {
      const a = ease(prog(t, appear + i * 0.08, 0.35)), f = prog(t, it.at), px = x + i * (w + gap);
      if (a <= 0) return '';
      const flip = Math.abs(Math.cos(Math.PI * f));          // 0.5 時卡片側轉到看不見，翻面
      const front = f >= 0.5, cx = px + w / 2;
      const body = front
        ? `${icon(it.icon, cx, y + h * 0.42, T)}<text x="${cx}" y="${y + h - 46}" font-size="44" font-weight="800" fill="${T.ink}" text-anchor="middle">${esc(it.label)}</text>`
        : `<text x="${cx}" y="${y + h / 2 + 34}" font-size="110" font-weight="800" fill="${T.line}" text-anchor="middle">?</text>`;
      return `<g opacity="${a}" transform="translate(${cx} 0) scale(${flip} 1) translate(${-cx} ${lerp(30, 0, a)})">
        <rect x="${px}" y="${y}" width="${w}" height="${h}" rx="28" fill="${front ? T.card : T.paper}" stroke="${front ? T.accent : T.line}" stroke-width="${front ? 5 : 3}" ${front ? '' : 'stroke-dasharray="14 12"'}/>${body}</g>`;
    }).join('');
  }

  // 問題標籤：從主體上方彈出
  function tag({ t, at, x, y, text, T }) {
    const k = back(prog(t, at)); if (k <= 0) return '';
    return `<g transform="translate(${x} ${y}) scale(${k})"><rect x="-150" y="-48" width="300" height="96" rx="48" fill="${T.ink}"/>
      <text y="16" font-size="46" font-weight="800" fill="${T.paper}" text-anchor="middle">${esc(text)}</text></g>`;
  }

  // 印章：從大縮到定位，略帶旋轉
  function stamp({ t, at, x, y, text, T }) {
    const p = prog(t, at); if (p <= 0) return '';
    const s = lerp(2.2, 1, ease(p));
    return `<g opacity="${clamp(p * 2)}" transform="translate(${x} ${y}) rotate(-8) scale(${s})">
      <rect x="-190" y="-70" width="380" height="140" rx="18" fill="none" stroke="${T.accent}" stroke-width="10"/>
      <text y="30" font-size="88" font-weight="900" fill="${T.accent}" text-anchor="middle">${esc(text)}</text></g>`;
  }

  // 一行標註：關鍵詞那一刻滑入
  function label({ t, at, x, y, text, T, size = 44, color }) {
    const k = ease(prog(t, at)); if (k <= 0) return '';
    return `<text x="${x}" y="${y + lerp(24, 0, k)}" opacity="${k}" font-size="${size}" font-weight="800" fill="${color || T.ink}" text-anchor="middle">${esc(text)}</text>`;
  }

  window.NSC = { clamp, ease, back, lerp, prog, esc, resolver, tabs, slots, tag, stamp, label, LEAD, TAIL };
})();
