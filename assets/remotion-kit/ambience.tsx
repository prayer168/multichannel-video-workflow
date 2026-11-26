import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Creature} from './sealife';
import type {Species} from './sealife';

// 動態海底背景：光束、焦散紋、海洋雪、氣泡、海帶珊瑚、遠處游過的海洋生物。
// 2026-11-26 使用者：畫面要更豐富，不要空白或只有方框與文字 → 所有深色漸層背景的鏡頭都墊這一層（放在內容之下）。
// level：1＝完整、0.5＝內容很滿時減量；floor：畫海床；creatures：遠景生物數量
type Props = {seed?: number; level?: number; floor?: boolean; creatures?: number; rays?: boolean};

const rnd = (seed: number) => {
  let s = seed * 9301 + 49297;
  return () => ((s = (s * 16807) % 2147483647) / 2147483647);
};

const KINDS: Species[] = ['Manta', 'Tuna', 'Sardines', 'Turtle', 'BlueTang', 'Jellyfish', 'Parrotfish', 'Angelfish'];

export const OceanAmbience: React.FC<Props> = ({seed = 1, level = 1, floor = true, creatures = 4, rays = true}) => {
  const f = useCurrentFrame();
  const r = rnd(seed);
  const snow = Array.from({length: Math.round(110 * level)}, () => [r() * 1920, r() * 1080, 1 + r() * 2.6, r()]);
  const bubbles = Array.from({length: Math.round(16 * level)}, () => [r() * 1920, r(), 4 + r() * 10, r()]);
  const kelp = Array.from({length: 11}, () => [r() * 1920, 140 + r() * 220, r()]);
  const fish = Array.from({length: creatures}, (_, i) => ({kind: KINDS[(seed + i * 3) % KINDS.length], y: 180 + r() * 620, v: 0.6 + r() * 1.6, x0: r() * 2400, s: 0.5 + r() * 0.8, dir: r() > 0.5}));
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
      <defs>
        <radialGradient id={`vig${seed}`} cx="50%" cy="45%" r="75%"><stop offset="60%" stopColor="#000" stopOpacity={0} /><stop offset="100%" stopColor="#000" stopOpacity={0.55} /></radialGradient>
        <linearGradient id={`ray${seed}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#dff6ff" stopOpacity={0.22} /><stop offset="1" stopColor="#dff6ff" stopOpacity={0} /></linearGradient>
      </defs>
      {rays ? Array.from({length: 7}, (_, i) => {
        const x = 120 + i * 280 + Math.sin(f / 50 + i * 1.7) * 60, w = 70 + (i % 3) * 40;
        return <polygon key={`r${i}`} points={`${x},0 ${x + w},0 ${x + w * 2.4 + Math.sin(f / 40 + i) * 80},1080 ${x + w * 0.6 + Math.sin(f / 40 + i) * 80},1080`} fill={`url(#ray${seed})`} opacity={(0.55 + 0.45 * Math.sin(f / 23 + i * 2)) * level} />;
      }) : null}
      {rays ? Array.from({length: 4}, (_, k) => {
        let d = '';
        for (let x = 0; x <= 1920; x += 40) d += `${x ? 'L' : 'M'}${x} ${22 + k * 16 + Math.sin(x / 70 + f / 9 + k * 2) * 7 + Math.sin(x / 23 - f / 6) * 3}`;
        return <path key={`c${k}`} d={d} stroke="#e8fbff" strokeWidth={2} fill="none" opacity={0.18 * level} />;
      }) : null}
      {fish.map((c, i) => {
        const x = c.dir ? ((c.x0 + f * c.v) % 2400) - 240 : 2160 - ((c.x0 + f * c.v) % 2400);
        return <Creature key={`f${i}`} kind={c.kind} x={x} y={c.y + Math.sin(f / 40 + i) * 18} size={c.s} f={f} ph={i} flip={!c.dir} opacity={0.28 * level} />;
      })}
      {snow.map(([x, y, rr, o], i) => {
        const yy = ((y - f * (0.25 + o * 0.5)) % 1080 + 1080) % 1080, xx = x + Math.sin(f / 60 + i) * 14;
        return <circle key={`s${i}`} cx={xx} cy={yy} r={rr} fill="#cfefff" opacity={(0.15 + o * 0.35) * level} />;
      })}
      {bubbles.map(([x, ph, rr, o], i) => {
        const yy = 1080 - ((f * (1.2 + o * 1.4) + ph * 1200) % 1200), xx = x + Math.sin(f / 12 + i) * 10;
        return <circle key={`b${i}`} cx={xx} cy={yy} r={rr} fill="none" stroke="#e8fbff" strokeWidth={2} opacity={0.45 * level} />;
      })}
      {floor ? (
        <g>
          {kelp.map(([x, h, ph], i) => {
            let d = `M${x} 1080`;
            for (let k = 1; k <= 12; k++) d += ` Q${x + Math.sin(f / 30 + ph * 6 + k / 2) * (6 + k * 1.6)} ${1080 - (h * k) / 12 + h / 24} ${x + Math.sin(f / 30 + ph * 6 + k / 2.2) * (6 + k * 2)} ${1080 - (h * k) / 12}`;
            return <path key={`k${i}`} d={d} stroke={['#2f7d5b', '#3f8f4a', '#5a8f3a'][i % 3]} strokeWidth={10 + (i % 3) * 3} fill="none" strokeLinecap="round" opacity={0.75 * level} />;
          })}
          <path d={`M0 1080 L0 1030 Q160 990 320 1020 T640 1010 T980 1030 T1320 1000 T1660 1025 T1920 1010 L1920 1080 Z`} fill="#1b2a2f" opacity={0.95} />
          {Array.from({length: 9}, (_, i) => { const x = 90 + i * 215 + (i % 2) * 40; return <g key={`co${i}`} opacity={0.9 * level}>
            <circle cx={x} cy={1032} r={18 + (i % 3) * 6} fill={['#e0785a', '#f2a541', '#c55a8a', '#7fd8cf'][i % 4]} opacity={0.7} />
            <circle cx={x + 22} cy={1040} r={12} fill={['#f2a541', '#c55a8a', '#7fd8cf', '#e0785a'][i % 4]} opacity={0.6} /></g>; })}
        </g>
      ) : null}
      <rect x={0} y={0} width={1920} height={1080} fill={`url(#vig${seed})`} />
    </svg>
  );
};
