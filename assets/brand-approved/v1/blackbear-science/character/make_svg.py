"""產生 character.svg（分層向量角色）。改造型就改這支再執行：python make_svg.py"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
C = dict(fur="#141B2E", line="#0A0F1C", ear_in="#5B6478", muzzle="#E8DED2", nose="#0E1424",
         jacket="#2D4E9E", jacket_dk="#1F3A7E", rib="#1A3170", white="#FFFFFF", glass="#B9BEC8",
         brow="#5A6378", mouth="#5A2228", tongue="#E57F72", pupil="#0E1424", stick="#8A5A2B")


def fluffy(cx, cy, rx, ry, n=34, amp=4.5, tuft=True, start=-90):
    """毛茸茸的輪廓：橢圓＋小鋸齒；頂端加一撮毛"""
    pts = []
    for i in range(n * 2):
        a = math.radians(start + i * 180 / n)
        r = 1 + (amp / rx if i % 2 else 0)
        x, y = cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)
        if tuft and abs(math.degrees(a) - start) % 360 < 8 or (tuft and abs((math.degrees(a) - start) % 360 - 360) < 8):
            y -= 10
        pts.append((x, y))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(1, len(pts) + 1, 2):
        p1, p2 = pts[i % len(pts)], pts[(i + 1) % len(pts)]
        d += f"Q{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + "Z"


def arm(side):
    """手臂畫成「從肩膀往下垂」，原點＝肩膀；由 JS 設定旋轉角度"""
    s = 1 if side == "right" else -1
    return f"""
    <g id="arm_{side}" class="arm" data-x="{200 + 78 * s}" data-y="318">
      <path class="sleeve" d="M-20,0 Q-24,40 -18,74 L18,74 Q24,40 20,0 Q0,-12 -20,0Z" fill="{C['jacket']}" stroke="{C['line']}" stroke-width="3.5"/>
      <path d="M-6,8 Q-8,40 -4,70" stroke="{C['jacket_dk']}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".7"/>
      <rect class="cuff" x="-19" y="66" width="38" height="16" rx="6" fill="{C['jacket_dk']}" stroke="{C['line']}" stroke-width="3"/>
      <path d="M-11,69 v10 M-4,69 v10 M3,69 v10 M10,69 v10" stroke="{C['rib']}" stroke-width="2"/>
      <g id="hand_{side}" class="hand">
        {'<g id="pointer"><line x1="0" y1="92" x2="0" y2="200" stroke="' + C['line'] + '" stroke-width="9" stroke-linecap="round"/><line x1="0" y1="92" x2="0" y2="200" stroke="' + C['stick'] + '" stroke-width="5.5" stroke-linecap="round"/></g>' if side == 'right' else ''}
        <ellipse cx="0" cy="94" rx="19" ry="17" fill="{C['fur']}" stroke="{C['line']}" stroke-width="3.5"/>
        <path d="M-8,101 q4,4 8,0 q4,4 8,0" stroke="#2A3350" stroke-width="2" fill="none"/>
      </g>
    </g>"""


svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-80 -10 560 530" width="560" height="530" id="bbt-svg">
<title>Black Bear Teacher 黑熊老師</title>
<g id="character" class="expression-normal mouth-closed gesture-idle">
  <ellipse id="shadow" cx="200" cy="505" rx="105" ry="11" fill="#000" opacity=".12"/>
  <g id="legs">
    <path d="M148,420 L146,488 Q146,502 172,502 Q192,502 192,490 L194,420Z" fill="{C['fur']}" stroke="{C['line']}" stroke-width="3.5"/>
    <path d="M206,420 L208,490 Q208,502 228,502 Q254,502 254,488 L252,420Z" fill="{C['fur']}" stroke="{C['line']}" stroke-width="3.5"/>
  </g>
  <g id="body_all">
  <g id="body">
    <path d="M128,330 Q118,400 134,440 Q200,456 266,440 Q282,400 272,330 Q200,300 128,330Z" fill="{C['fur']}" stroke="{C['line']}" stroke-width="3.5"/>
  </g>
  <g id="jacket">
    <path d="M124,322 Q112,390 124,436 L186,440 L188,350 L170,312Z" fill="{C['jacket']}" stroke="{C['line']}" stroke-width="3.5" stroke-linejoin="round"/>
    <path d="M276,322 Q288,390 276,436 L214,440 L212,350 L230,312Z" fill="{C['jacket']}" stroke="{C['line']}" stroke-width="3.5" stroke-linejoin="round"/>
    <path d="M170,312 L188,350 L186,440" fill="none" stroke="{C['jacket_dk']}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M230,312 L212,350 L214,440" fill="none" stroke="{C['jacket_dk']}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M124,424 Q155,432 186,430 L186,442 L124,438Z M276,424 Q245,432 214,430 L214,442 L276,438Z" fill="{C['jacket_dk']}" stroke="{C['line']}" stroke-width="3"/>
    <path d="M134,428 v10 M146,429 v11 M158,430 v11 M170,430 v11 M230,430 v11 M242,430 v11 M254,429 v11 M266,428 v10" stroke="{C['rib']}" stroke-width="2"/>
    <rect x="136" y="390" width="34" height="26" rx="4" fill="none" stroke="{C['jacket_dk']}" stroke-width="3"/>
    <rect x="230" y="390" width="34" height="26" rx="4" fill="none" stroke="{C['jacket_dk']}" stroke-width="3"/>
    <circle cx="196" cy="372" r="3.5" fill="{C['jacket_dk']}"/><circle cx="196" cy="398" r="3.5" fill="{C['jacket_dk']}"/>
  </g>
  <g id="chest_mark">
    <path d="M168,314 Q200,330 232,314 L212,352 Q200,362 188,352Z" fill="{C['white']}" stroke="{C['line']}" stroke-width="2.5" stroke-linejoin="round"/>
  </g>
  <g id="accessories">
    <g id="paw_badge" transform="translate(252,356)">
      <ellipse cx="0" cy="4" rx="7" ry="6" fill="{C['white']}"/>
      <circle cx="-8" cy="-4" r="2.8" fill="{C['white']}"/><circle cx="-3" cy="-8" r="2.8" fill="{C['white']}"/>
      <circle cx="3" cy="-8" r="2.8" fill="{C['white']}"/><circle cx="8" cy="-4" r="2.8" fill="{C['white']}"/>
    </g>
  </g>
  {arm('left')}
  {arm('right')}
  </g>
  <g id="head_all"><g transform="translate(0,16)">
    <g id="ears">
      <g id="ear_left"><circle cx="92" cy="74" r="42" fill="{C['fur']}" stroke="{C['line']}" stroke-width="4"/><circle cx="94" cy="78" r="23" fill="{C['ear_in']}"/></g>
      <g id="ear_right"><circle cx="308" cy="74" r="42" fill="{C['fur']}" stroke="{C['line']}" stroke-width="4"/><circle cx="306" cy="78" r="23" fill="{C['ear_in']}"/></g>
    </g>
    <g id="head">
      <path d="{fluffy(200, 178, 140, 122)}" fill="{C['fur']}" stroke="{C['line']}" stroke-width="4" stroke-linejoin="round"/>
      <path d="M150,72 Q200,60 250,72" stroke="#26304A" stroke-width="6" fill="none" stroke-linecap="round" opacity=".6"/>
    </g>
    <g id="eyebrows">
      <path id="eyebrow_left" d="M128,116 Q150,104 172,114" stroke="{C['brow']}" stroke-width="7" fill="none" stroke-linecap="round"/>
      <path id="eyebrow_right" d="M228,114 Q250,104 272,116" stroke="{C['brow']}" stroke-width="7" fill="none" stroke-linecap="round"/>
    </g>
    <g id="eyes">
      <g id="eye_left">
        <circle cx="152" cy="168" r="26" fill="{C['white']}"/>
        <g class="pupil"><circle cx="154" cy="170" r="17" fill="{C['pupil']}"/><circle cx="160" cy="162" r="6" fill="#fff"/><circle cx="148" cy="177" r="2.6" fill="#fff"/></g>
      </g>
      <g id="eye_right">
        <circle cx="248" cy="168" r="26" fill="{C['white']}"/>
        <g class="pupil"><circle cx="246" cy="170" r="17" fill="{C['pupil']}"/><circle cx="252" cy="162" r="6" fill="#fff"/><circle cx="240" cy="177" r="2.6" fill="#fff"/></g>
      </g>
      <path id="eye_left_closed" d="M130,170 Q152,184 174,170" stroke="{C['white']}" stroke-width="5" fill="none" stroke-linecap="round" display="none"/>
      <path id="eye_right_closed" d="M226,170 Q248,184 270,170" stroke="{C['white']}" stroke-width="5" fill="none" stroke-linecap="round" display="none"/>
      <path id="eye_right_wink" d="M228,174 Q248,156 268,174" stroke="{C['white']}" stroke-width="5.5" fill="none" stroke-linecap="round" display="none"/>
    </g>
    <g id="glasses" fill="none" stroke="{C['glass']}" stroke-width="5.5">
      <circle cx="152" cy="168" r="35"/><circle cx="248" cy="168" r="35"/>
      <path d="M187,164 Q200,156 213,164"/>
      <path d="M117,160 L98,152 M283,160 L302,152" stroke-linecap="round"/>
    </g>
    <g id="muzzle">
      <ellipse cx="200" cy="232" rx="54" ry="40" fill="{C['muzzle']}"/>
      <ellipse cx="200" cy="210" rx="17" ry="11" fill="{C['nose']}"/>
      <ellipse cx="195" cy="206" rx="5" ry="2.6" fill="#fff" opacity=".55"/>
      <path d="M200,221 v8" stroke="{C['nose']}" stroke-width="3.5" stroke-linecap="round"/>
    </g>
    <g id="mouth">
      <path id="mouth_closed" d="M180,234 Q200,250 220,234" stroke="{C['nose']}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
      <g id="mouth_small" display="none">
        <path d="M184,233 Q200,230 216,233 Q213,251 200,252 Q187,251 184,233Z" fill="{C['mouth']}" stroke="{C['nose']}" stroke-width="3.5"/>
        <ellipse cx="200" cy="246" rx="9" ry="4.5" fill="{C['tongue']}"/>
      </g>
      <g id="mouth_A" display="none">
        <path d="M176,229 Q200,225 224,229 Q222,264 200,266 Q178,264 176,229Z" fill="{C['mouth']}" stroke="{C['nose']}" stroke-width="3.5"/>
        <ellipse cx="200" cy="256" rx="14" ry="7.5" fill="{C['tongue']}"/>
      </g>
      <g id="mouth_O" display="none">
        <ellipse cx="200" cy="244" rx="10" ry="14" fill="{C['mouth']}" stroke="{C['nose']}" stroke-width="3.5"/>
        <ellipse cx="200" cy="252" rx="6" ry="4" fill="{C['tongue']}"/>
      </g>
      <path id="mouth_frown" d="M184,246 Q200,234 216,246" stroke="{C['nose']}" stroke-width="4.5" fill="none" stroke-linecap="round" display="none"/>
      <g id="mouth_wobble" display="none">
        <path d="M178,236 q5.5,-6 11,0 q5.5,6 11,0 q5.5,-6 11,0 q5.5,6 11,0 L222,250 Q200,258 178,250Z" fill="{C['mouth']}" stroke="{C['nose']}" stroke-width="3.5" stroke-linejoin="round"/>
      </g>
    </g>
    <g id="fx">
      <g id="fx_sweat" display="none">
        <path d="M318,118 q10,16 0,24 q-10,-8 0,-24Z" fill="#4FA3F0" stroke="#1F5FA8" stroke-width="2"/>
        <path d="M70,150 q8,13 0,19 q-8,-6 0,-19Z" fill="#4FA3F0" stroke="#1F5FA8" stroke-width="2"/>
      </g>
      <g id="fx_sparkle" display="none">
        <path d="M330,120 l5,14 l14,5 l-14,5 l-5,14 l-5,-14 l-14,-5 l14,-5Z" fill="#F7B733"/>
      </g>
      <g id="fx_shock" display="none" stroke="#F28C28" stroke-width="6" stroke-linecap="round">
        <path d="M58,92 l-18,-14 M50,120 l-22,-2 M342,92 l18,-14 M350,120 l22,-2"/>
      </g>
      <g id="fx_think" display="none" fill="#fff" stroke="{C['line']}" stroke-width="2.5">
        <circle cx="352" cy="96" r="7"/><circle cx="376" cy="70" r="13"/>
        <text x="376" y="77" font-size="18" font-weight="900" text-anchor="middle" fill="{C['line']}" stroke="none">?</text>
      </g>
    </g>
  </g></g>
  <g id="front_layer"></g>
</g>
</svg>
"""
open(os.path.join(HERE, "character.svg"), "w", encoding="utf-8").write(svg)
print("character.svg written")
