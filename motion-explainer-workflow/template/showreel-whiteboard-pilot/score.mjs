// score.mjs — 試跑只合成「有資訊作用」的音效，不做配樂（配樂沿用頻道原創 lo-fi，於正式片接入）。
import { DUR, CUES } from './timeline.js';
export { DUR };
export default function score(S) {
  const sfx = S.bus('sfx', { gain: 0.7, reverb: 0.12 });
  for (const c of CUES) {
    if (c.sfx === 'pop') sfx.add(S.pop('E6'), c.t, { gain: 0.45 });
    if (c.sfx === 'tick') sfx.add(S.tick(), c.t, { gain: 0.5 });
  }
}
