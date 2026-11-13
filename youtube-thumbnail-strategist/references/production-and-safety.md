# Production, accessibility, factual and licensing safeguards

## Source preference
1. User-owned source frame that genuinely shows the result.
2. User-provided licensed photograph or video.
3. Explicitly labeled explanatory illustration / concept art when visual evidence is unavailable.
Never claim a conceptual illustration depicts actual recorded results. Keep a source ledger for each visible external element and approval/license status.

## Generation stages
Stage 1: image backdrop + subject **without text**, subject occupying ~40–70% only as a design starting point; meaningful negative space reserved for typography.
Stage 2: programmatically composite Traditional Chinese copy and brand assets, respecting local licensed fonts. This limits bad CJK glyphs generated inside imagery.
Stage 3: inspect full-size and downscaled preview (~160x90) for legibility, clipping, focus, source authenticity, and mistaken claims.

## Resolution and metadata
Use 16:9. Prepare 3840x2160 master when resources allow; create 1280x720 working preview as useful. YouTube policies and device-specific upload limits change—re-check official page https://support.google.com/youtube/answer/72431 before final upload.
PNG or JPG standard. Keep meaningful margin around edges and away from the lower-right duration badge. Never assume an exact overlay bounding box is universal.

## Safe production prompt template
'Create a single-focus, professional, 16:9 YouTube thumbnail background for [audience/channel]. Verified subject [confirmed subject] is [verified action]. Frame [layout], large readable silhouette, clear background, realistic proportions, credible physical depiction, mobile-friendly contrast, reserved blank space for a Traditional Chinese text overlay. Render NO text, NO logos, NO UI labels, NO invented data. Any conceptual visualization must be marked in the metadata as an illustration.'

## Block conditions
- Missing authority to reuse source photo or footage: do not use it as final art.
- Unverified spectacular science event or unmeasured speed benefit: do not assert it visually or with words.
- Use local frames when available. If the input or tooling supports neither frame rendering nor requested artwork, deliver design specs and prompts with status `planned`.
- No legible Traditional Chinese font: prompt-only or request a licensed font; do not copy unauthorized fonts into the package.
- Never alter video-related evidence or secretly upload content.
