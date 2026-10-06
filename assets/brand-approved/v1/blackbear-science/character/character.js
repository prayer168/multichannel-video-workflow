/* Black Bear Teacher｜黑熊老師 — 表情、嘴型、眨眼、說話、手勢控制
 * 所有動態都由同一個時鐘 t（秒）算出：
 *   - 一般瀏覽：自動用 requestAnimationFrame 跑即時時鐘
 *   - 影片逐格錄製：BlackBearTeacher.useManualClock(true) 後，每格呼叫 BlackBearTeacher.tick(t)，畫面完全可重現
 */
(function () {
  const EXPRESSIONS = ["normal", "talking", "surprised", "thinking", "panic", "wink", "sad"];
  const MOUTHS = ["closed", "small", "A", "O"];
  // 手臂角度（度，SVG 順時針為正；0＝自然下垂）。right＝畫面右側手臂
  const GESTURES = {
    idle:      { right: -14,  left: 14,   pointer: 0 },
    wave:      { right: -122, left: 14,   pointer: 0, osc: { right: [18, 3.2] } },
    point:     { right: -104, left: 14,   pointer: 1, osc: { right: [3, 1.1] } },
    thinking:  { right: 116,  left: 14,   pointer: 0, front: ["right"] },
    celebrate: { right: -124, left: 124,  pointer: 0, osc: { right: [10, 4], left: [-10, 4] } },
    panic:     { right: -166, left: 166,  pointer: 0, front: ["right", "left"], osc: { right: [5, 11], left: [-5, 11] } },
  };
  // 表情：眉毛位移／旋轉、瞳孔位移與縮放、預設嘴型、特效
  const EXPR = {
    normal:    { brow: [0, 0, 0, 0], pupil: [0, 0, 1], mouth: "closed", fx: [] },
    talking:   { brow: [0, -2, 0, -2], pupil: [0, 0, 1], mouth: "small", fx: [] },
    surprised: { brow: [0, -14, 0, -14], pupil: [0, 0, .72], mouth: "O", fx: ["shock"] },
    thinking:  { brow: [-8, -10, 10, 4], pupil: [-7, -8, 1], mouth: "frown", fx: ["think"] },
    panic:     { brow: [18, -4, -18, -4], pupil: [0, 2, .8], mouth: "wobble", fx: ["sweat"] },
    wink:      { brow: [0, -4, 6, 4], pupil: [0, 0, 1], mouth: "small", fx: ["sparkle"], wink: true },
    sad:       { brow: [16, 2, -16, 2], pupil: [0, 7, 1], mouth: "frown", fx: [] },
  };
  const ALL_MOUTHS = ["closed", "small", "A", "O", "frown", "wobble"];

  const S = {
    expression: "normal", mouth: "closed", mouthForced: null, gesture: "idle",
    talking: false, talkStart: 0, autoBlink: true, blinkUntil: -1, nextBlink: 2,
    manual: false, t: 0, arms: { right: -14, left: 14 }, lastT: 0, pointer: 0,
    blinkSeed: 7, mouthLevel: null,
  };
  let root, svg, el = {};

  const $ = (id) => svg.querySelector("#" + id);
  const show = (node, on) => node && node.setAttribute("display", on ? "inline" : "none");
  const rnd = (n) => { const x = Math.sin(n * 127.1 + S.blinkSeed * 311.7) * 43758.5453; return x - Math.floor(x); };

  function setClass(prefix, v) {
    root.classList.forEach((c) => c.startsWith(prefix + "-") && root.classList.remove(c));
    root.classList.add(prefix + "-" + v);
  }

  function setExpression(name) {
    if (!EXPR[name]) return console.warn("unknown expression", name);
    S.expression = name; setClass("expression", name);
    if (name === "talking") startTalking();
  }
  function setMouth(m) { if (ALL_MOUTHS.includes(m)) { S.mouthForced = m; setClass("mouth", m); } }
  function clearMouth() { S.mouthForced = null; }
  function setGesture(g) { if (GESTURES[g]) { S.gesture = g; setClass("gesture", g); } }
  function blink(ms = 150) { S.blinkUntil = S.t + ms / 1000; }
  function startAutoBlink() { S.autoBlink = true; }
  function stopAutoBlink() { S.autoBlink = false; }
  function startTalking() { S.talking = true; S.talkStart = S.t; }
  function stopTalking() { S.talking = false; S.mouthForced = null; }
  /** 影片用：0～1 的音量（每格由配音振幅給），自動換算嘴型 */
  function setMouthLevel(v) { S.mouthLevel = v; }

  function talkMouth(t) {
    if (S.mouthLevel != null) {
      const v = S.mouthLevel;
      if (v < 0.08) return "closed";
      if (v < 0.30) return "small";
      return (Math.floor(t * 9) % 5 === 0) ? "O" : "A";
    }
    const seq = ["small", "A", "small", "O", "A", "closed", "small", "A"];
    return seq[Math.floor((t - S.talkStart) * 9) % seq.length];
  }

  function lerpAngle(a, b, k) { return a + (b - a) * k; }

  function render(t) {
    const dt = Math.max(0, Math.min(0.1, t - S.lastT)); S.lastT = t; S.t = t;
    const ex = EXPR[S.expression], g = GESTURES[S.gesture];

    // 眨眼（可重現的偽隨機間隔 3～6 秒）
    if (S.autoBlink && t >= S.nextBlink) { S.blinkUntil = t + 0.15; S.nextBlink = t + 3 + rnd(Math.floor(t)) * 3; }
    const closed = t < S.blinkUntil;
    show(el.eyeL, !closed); show(el.eyeLc, closed);
    show(el.eyeR, !closed && !ex.wink); show(el.eyeRc, closed && !ex.wink); show(el.eyeRw, !!ex.wink);

    // 眉毛
    const [lr, ly, rr, ry] = ex.brow;
    el.browL.setAttribute("transform", `translate(0,${ly}) rotate(${lr},150,112)`);
    el.browR.setAttribute("transform", `translate(0,${ry}) rotate(${rr},250,112)`);
    // 瞳孔
    const [px, py, ps] = ex.pupil;
    const shake = S.expression === "panic" ? Math.sin(t * 40) * 1.5 : 0;
    el.pupils.forEach((p, i) => {
      const cx = i ? 246 : 154;
      p.setAttribute("transform", `translate(${px + shake},${py}) translate(${cx},170) scale(${ps}) translate(${-cx},-170)`);
    });

    // 嘴型
    let m = S.mouthForced || (S.talking ? talkMouth(t) : ex.mouth);
    if (S.talking && !S.mouthForced && ["panic"].includes(S.expression) && m !== "closed") m = "wobble";
    ALL_MOUTHS.forEach((k) => show(el.mouth[k], k === m));

    // 特效
    ["sweat", "sparkle", "shock", "think"].forEach((k) => show(el.fx[k], ex.fx.includes(k)));
    if (ex.fx.includes("sweat")) el.fx.sweat.setAttribute("transform", `translate(0,${(t * 30) % 14})`);
    if (ex.fx.includes("sparkle")) { const s = 0.8 + 0.25 * Math.sin(t * 6); el.fx.sparkle.setAttribute("transform", `translate(337,141) scale(${s}) translate(-337,-141)`); }

    // 手臂：平滑轉到目標角度（約 0.2 秒）＋擺動
    const k = 1 - Math.exp(-dt * 14);
    ["right", "left"].forEach((side) => {
      let target = g[side];
      if (g.osc && g.osc[side]) target += g.osc[side][0] * Math.sin(t * Math.PI * 2 * g.osc[side][1] / 2);
      S.arms[side] = dt === 0 ? target : lerpAngle(S.arms[side], target, k);
      const a = el.arms[side];
      const wantFront = (g.front || []).includes(side) && Math.abs(S.arms[side] - target) < 60;
      const parent = wantFront ? el.front : el.back;
      if (a.parentNode !== parent) parent.appendChild(a);
      a.setAttribute("transform", `translate(${a.dataset.x},${a.dataset.y}) rotate(${S.arms[side].toFixed(2)})`);
    });
    S.pointer = lerpAngle(S.pointer, g.pointer, dt === 0 ? 1 : k);
    el.pointer.setAttribute("opacity", S.pointer.toFixed(2));
    el.pointer.setAttribute("transform", `translate(0,94) scale(1,${(0.3 + 0.7 * S.pointer).toFixed(3)}) translate(0,-94)`);

    // 呼吸＋說話時點頭
    const breath = Math.sin(t * 2.2) * 1.6;
    const nod = S.talking ? Math.sin(t * 7) * 1.8 : 0;
    const tilt = S.expression === "thinking" ? -5 : S.expression === "sad" ? 3 : 0;
    el.body.setAttribute("transform", `translate(0,${(-breath * 0.4).toFixed(2)})`);
    el.head.setAttribute("transform", `translate(0,${(-breath + nod).toFixed(2)}) rotate(${tilt},200,300)`);
  }

  function loop(now) { if (!S.manual) render(now / 1000); requestAnimationFrame(loop); }

  async function mount(container, svgUrl) {
    const box = typeof container === "string" ? document.querySelector(container) : container;
    if (!svgUrl) svgUrl = new URL("character.svg", document.currentScript ? document.currentScript.src : location.href).href;
    box.innerHTML = await (await fetch(svgUrl)).text();
    svg = box.querySelector("svg"); root = svg.querySelector("#character");
    el = {
      eyeL: $("eye_left"), eyeR: $("eye_right"), eyeLc: $("eye_left_closed"), eyeRc: $("eye_right_closed"), eyeRw: $("eye_right_wink"),
      browL: $("eyebrow_left"), browR: $("eyebrow_right"), pupils: [...svg.querySelectorAll(".pupil")],
      mouth: Object.fromEntries(ALL_MOUTHS.map((k) => [k, $("mouth_" + k)])),
      fx: { sweat: $("fx_sweat"), sparkle: $("fx_sparkle"), shock: $("fx_shock"), think: $("fx_think") },
      arms: { right: $("arm_right"), left: $("arm_left") }, pointer: $("pointer"),
      body: $("body_all"), head: $("head_all"), front: $("front_layer"), back: $("body_all"),
    };
    render(0);
    requestAnimationFrame(loop);
    return api;
  }

  const api = {
    mount, setExpression, setMouth, clearMouth, setGesture, blink, startAutoBlink, stopAutoBlink,
    startTalking, stopTalking, setMouthLevel, EXPRESSIONS, MOUTHS, GESTURES: Object.keys(GESTURES),
    useManualClock(on = true) { S.manual = on; },
    tick(t) { render(t); },
    /** 影片用：一次設定整個狀態 */
    pose({ expression, gesture, talking, level, mouth } = {}) {
      if (expression && expression !== S.expression) { S.expression = expression; setClass("expression", expression); }
      if (gesture && gesture !== S.gesture) setGesture(gesture);
      if (talking !== undefined) S.talking = talking;
      if (level !== undefined) S.mouthLevel = level;
      S.mouthForced = mouth || null;
    },
    get state() { return { ...S }; },
  };
  window.BlackBearTeacher = api;
  Object.assign(window, { setExpression, setMouth, blink, startAutoBlink, stopAutoBlink, startTalking, stopTalking, setGesture });
})();
