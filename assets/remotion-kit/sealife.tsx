import React from 'react';

// 原創向量海洋生物：依真實物種配色，頭朝 +x，中心在原點，約 200×100 單位；s 為縮放、f 為影格（尾鰭擺動）
// 2026-11-25 使用者：「魚要畫的像真正的海洋一樣，有大有小，顏色豐富的各種海洋生物」
type P = {f: number; ph?: number};
const wag = (f: number, ph = 0, amp = 10, sp = 0.35) => Math.sin(f * sp + ph) * amp;

const Eye: React.FC<{x: number; y: number; r?: number}> = ({x, y, r = 6}) => (
  <g><circle cx={x} cy={y} r={r} fill="#fff" /><circle cx={x + r * 0.2} cy={y} r={r * 0.6} fill="#111" /></g>
);

// 小丑魚：橘色、三條鑲黑邊白帶
const Clownfish: React.FC<P> = ({f, ph}) => (
  <g>
    <path d={`M-58 0 L-92 ${-24 + wag(f, ph, 6)} L-86 0 L-92 ${24 + wag(f, ph, 6)} Z`} fill="#f26a1b" stroke="#111" strokeWidth={3} />
    <ellipse rx={62} ry={30} fill="#f47a20" />
    {[-28, 6, 38].map((x, i) => <path key={i} d={`M${x} -30 Q${x + 10} 0 ${x} 30`} stroke="#111" strokeWidth={16} fill="none" />)}
    {[-28, 6, 38].map((x, i) => <path key={i} d={`M${x} -29 Q${x + 10} 0 ${x} 29`} stroke="#fff" strokeWidth={10} fill="none" />)}
    <path d="M-20 -28 Q0 -48 30 -28" fill="#f47a20" stroke="#111" strokeWidth={3} />
    <Eye x={46} y={-6} r={6} />
  </g>
);

// 擬刺尾鯛：寶藍身體、黑色調色盤紋、黃色尾
const BlueTang: React.FC<P> = ({f, ph}) => (
  <g>
    <path d={`M-62 0 L-98 ${-30 + wag(f, ph, 7)} L-90 0 L-98 ${30 + wag(f, ph, 7)} Z`} fill="#ffd21f" />
    <path d="M-66 0 C-50 -52 40 -56 70 -6 C74 4 60 30 20 40 C-20 50 -60 30 -66 0 Z" fill="#1f5fd6" />
    <path d="M-50 -10 C-20 -40 30 -36 50 -18 C20 -24 -10 -8 -24 10 C-10 20 20 22 30 24 C0 34 -40 20 -50 -10 Z" fill="#0b1a3c" />
    <path d="M-40 -34 Q10 -64 56 -22" stroke="#0b1a3c" strokeWidth={6} fill="none" />
    <Eye x={50} y={-8} r={6} />
  </g>
);

// 皇帝神仙魚：藍黃斜紋
const Angelfish: React.FC<P> = ({f, ph}) => (
  <g>
    <path d={`M-50 0 L-78 ${-22 + wag(f, ph, 5)} L-74 0 L-78 ${22 + wag(f, ph, 5)} Z`} fill="#ffcc1a" />
    <ellipse rx={56} ry={44} fill="#1d3fa0" />
    {[-40, -24, -8, 8, 24].map((x, i) => <path key={i} d={`M${x} -42 L${x + 22} 42`} stroke="#ffd84a" strokeWidth={6} />)}
    <path d="M30 -30 Q58 -10 52 20 Q40 30 30 18 Z" fill="#cfe6ff" />
    <path d="M28 -26 L40 -40 L46 -30" stroke="#111" strokeWidth={8} fill="none" />
    <Eye x={42} y={-6} r={5} />
  </g>
);

// 鸚哥魚：青綠身體、粉橘鱗紋、喙狀嘴
const Parrotfish: React.FC<P> = ({f, ph}) => (
  <g>
    <path d={`M-70 0 L-108 ${-32 + wag(f, ph, 7)} Q-96 0 -108 ${32 + wag(f, ph, 7)} Z`} fill="#2bc4a4" stroke="#f08a9c" strokeWidth={4} />
    <ellipse rx={78} ry={36} fill="#22b39a" />
    {Array.from({length: 12}, (_, i) => <path key={i} d={`M${-50 + (i % 6) * 18} ${i < 6 ? -10 : 12} q8 -8 16 0`} stroke="#f2a0ae" strokeWidth={3} fill="none" />)}
    <path d="M-40 -34 Q10 -52 60 -28" stroke="#f08a9c" strokeWidth={6} fill="none" />
    <path d="M70 -8 Q86 0 70 10 Z" fill="#e8e0c8" />
    <Eye x={52} y={-10} r={6} />
  </g>
);

// 黃鰭鮪：深藍背、銀白腹、黃色小離鰭、新月形尾鰭
const Tuna: React.FC<P> = ({f, ph}) => (
  <g>
    <path d={`M-92 0 L-128 ${-40 + wag(f, ph, 8, 0.25)} Q-110 0 -128 ${40 + wag(f, ph, 8, 0.25)} Z`} fill="#1b3558" />
    <path d="M-96 0 C-60 -40 40 -44 96 -4 C40 36 -60 38 -96 0 Z" fill="#c9d6e2" />
    <path d="M-96 0 C-60 -40 40 -44 96 -4 C40 -10 -40 -8 -96 0 Z" fill="#1d3d68" />
    <path d="M-20 -30 L0 -62 L14 -32 Z" fill="#f2c21b" /><path d="M-20 28 L0 56 L12 28 Z" fill="#f2c21b" />
    {[-40, -52, -64, -76].map((x, i) => <path key={i} d={`M${x} -18 l5 -8 l5 8 Z M${x} 18 l5 8 l5 -8 Z`} fill="#f2c21b" />)}
    <path d="M-20 -2 Q30 4 70 -4" stroke="#e6c84a" strokeWidth={3} fill="none" opacity={0.8} />
    <Eye x={74} y={-8} r={6} />
  </g>
);

// 綠蠵龜：龜甲六角紋、前肢划水
const Turtle: React.FC<P> = ({f, ph}) => {
  const fl = Math.sin(f * 0.12 + (ph ?? 0)) * 22;
  return (
    <g>
      <path d={`M10 -30 Q40 ${-70 - fl} 70 ${-64 - fl} Q50 -40 30 -24 Z`} fill="#8a9a5b" />
      <path d={`M10 30 Q40 ${70 + fl} 70 ${64 + fl} Q50 40 30 24 Z`} fill="#8a9a5b" />
      <path d={`M-50 -20 Q-74 ${-40 + fl / 2} -86 -34 Q-70 -18 -56 -12 Z`} fill="#7a8a4b" />
      <path d={`M-50 20 Q-74 ${40 - fl / 2} -86 34 Q-70 18 -56 12 Z`} fill="#7a8a4b" />
      <ellipse cx={74} cy={0} rx={24} ry={18} fill="#9aaa6a" />
      <ellipse rx={66} ry={46} fill="#6b5232" />
      {[[-28, -16], [0, -22], [28, -16], [-28, 16], [0, 22], [28, 16], [0, 0]].map(([x, y], i) => (
        <polygon key={i} points={`${x - 12},${y} ${x - 6},${y - 10} ${x + 6},${y - 10} ${x + 12},${y} ${x + 6},${y + 10} ${x - 6},${y + 10}`} fill="#8b6a3e" stroke="#4a3620" strokeWidth={2} />
      ))}
      <Eye x={84} y={-6} r={4} />
    </g>
  );
};

// 海月水母：半透明粉紫傘、四葉生殖腺、長觸手（向上漂）
const Jellyfish: React.FC<P> = ({f, ph}) => {
  const pulse = 1 + Math.sin(f * 0.15 + (ph ?? 0)) * 0.1;
  return (
    <g>
      <g transform={`scale(${pulse} ${2 - pulse})`}>
        <path d="M-50 0 Q-50 -54 0 -54 Q50 -54 50 0 Q25 8 0 4 Q-25 8 -50 0 Z" fill="#e7a7d8" opacity={0.55} />
        {[-18, 0, 18].map((x, i) => <circle key={i} cx={x} cy={-24} r={9} fill="none" stroke="#c45aa8" strokeWidth={3} opacity={0.8} />)}
      </g>
      {Array.from({length: 7}, (_, i) => (
        <path key={i} d={`M${-36 + i * 12} 4 q${wag(f, i, 8, 0.2)} 30 0 60 t0 60`} stroke="#f3c6e8" strokeWidth={2} fill="none" opacity={0.6} />
      ))}
    </g>
  );
};

// 鬼蝠魟：寬大三角翼、深色背、白色前緣
const Manta: React.FC<P> = ({f, ph}) => {
  const w = Math.sin(f * 0.08 + (ph ?? 0)) * 16;
  return (
    <g>
      <path d={`M80 0 Q20 ${-40} -10 ${-110 + w} Q-40 -40 -60 0 Q-40 40 -10 ${110 - w} Q20 40 80 0 Z`} fill="#3d5f7c" />
      <path d={`M60 0 Q14 -26 -8 ${-80 + w * 0.7} Q-30 -30 -44 0 Q-30 30 -8 ${80 - w * 0.7} Q14 26 60 0 Z`} fill="#2a465e" />
      <path d={`M80 0 Q20 -40 -10 ${-110 + w}`} stroke="#d8dee4" strokeWidth={4} fill="none" />
      <path d={`M80 0 Q20 40 -10 ${110 - w}`} stroke="#d8dee4" strokeWidth={4} fill="none" />
      <path d="M-60 0 L-140 4" stroke="#3d5f7c" strokeWidth={5} />
      <path d="M80 -12 l18 -6 M80 12 l18 6" stroke="#3d5f7c" strokeWidth={8} strokeLinecap="round" />
    </g>
  );
};

// 沙丁魚群：數十條銀色小魚
const Sardines: React.FC<P> = ({f, ph}) => {
  let s = 7 + Math.round((ph ?? 0) * 10);
  const r = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  return (
    <g>
      {Array.from({length: 26}, (_, i) => {
        const x = (r() - 0.5) * 220, y = (r() - 0.5) * 110 + Math.sin(f * 0.1 + i) * 6;
        return (
          <g key={i} transform={`translate(${x} ${y}) scale(${0.7 + r() * 0.4})`}>
            <path d={`M-14 0 L-22 ${-6 + wag(f, i, 3, 0.6)} L-22 ${6 + wag(f, i, 3, 0.6)} Z`} fill="#9fb3c2" />
            <ellipse rx={16} ry={5} fill="#d6e1ea" /><path d="M-14 -2 L14 -2" stroke="#4d6a85" strokeWidth={2.5} />
          </g>
        );
      })}
    </g>
  );
};

export const SPECIES = {Clownfish, BlueTang, Angelfish, Parrotfish, Tuna, Turtle, Jellyfish, Manta, Sardines};
export type Species = keyof typeof SPECIES;

// 一隻生物：x/y 為畫面座標、size 為倍率、flip 為頭朝左
export const Creature: React.FC<{kind: Species; x: number; y: number; size: number; f: number; ph?: number; rot?: number; flip?: boolean; opacity?: number}> = ({kind, x, y, size, f, ph, rot = 0, flip, opacity = 1}) => {
  const K = SPECIES[kind];
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${flip ? -size : size} ${size})`} opacity={opacity}>
      <K f={f} ph={ph} />
    </g>
  );
};
