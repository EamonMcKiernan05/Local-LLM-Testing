# Pulse Engine (raw WebGL + WebAudio) — bench pack v3.4 prompt

From the one-shot demo bench pack. Verbatim.

```text
Build one self-contained HTML file: PULSE ENGINE, a generative audiovisual instrument in 3D, using raw WebGL and WebAudio. No libraries, no external files. It plays music by itself, you can steer it, and the visuals are driven by the sound.

THE FRAME at t=0: behind a start overlay, the scene already fills the frame and is moving — a deep blue field with a breathing torus at centre, slow camera drift through 3D space, sparks falling past the camera. It reads as a designed instrument, not an oscilloscope.

ART DIRECTION
- Palette: field #0a0f2e to #1a0b3a, cyan #35f0ff, magenta #ff2ea6, warm white accents. Additive glow, never a flat fill.
- Composition: one strong central motif (the torus), a radial spectrum ring around it, particles between them. Generous negative space.

BUILD, IN THIS ORDER
1. Audio engine: a 16-step sequencer with four synthesised drums — kick (pitch-swept sine, fast decay), snare (noise plus tone), hats (high-passed noise), clap (short noise bursts). A bassline and an arpeggio, subtractive, in one key, over a seeded four-chord progression.
2. Generative mode ON by default: seeded (1337) mutation of patterns and melody that stays musical. A Randomise button reseeds it.
3. Timing: all events scheduled against AudioContext.currentTime with a lookahead window — never setTimeout per step. Master chain with soft limiting and a gentle sidechain pump.
4. Visuals in 3D: an AnalyserNode drives one unmistakable mapping per band — kick blooms the torus outward, bass warps the surrounding field, hats spark at the rim in depth, mids and highs drive the radial spectrum. The kick pulse must be visible from across the room.
5. UI: start overlay "CLICK TO START AUDIO" that does not dim the scene to black; a slim bottom bar with Play/Stop, tempo 90–160, mute, generative toggle, Randomise; hotkeys 1–4 mute drums, G toggles generative.

3D RULES — this is the test
- The instrument lives in 3D: the torus is ring geometry generated in code, particles are points in three dimensions drawn with a depth test so they pass in front of and behind it, and the camera drifts on a 10-second loop that returns exactly to frame 1.
- Bloom is fake: additive blending, emissive colours and sprite glow. No post-processing.

MOTION: rings bloom and decay on each kick; sparks vary in size and count and pass in front of and behind the torus; slow drift so the composition never sits still.

TECHNICAL — hard rules
- One .html file, all CSS and JS inline. No libraries, no CDN, no audio files, no images, no textures. Opens from file://.
- Raw WebGL1 or WebGL2 with your own mat4 helpers, plus WebAudio. WebAudio starts on the first click (autoplay policy); everything before that is silent but visible.
- Check shader compile status; on failure show the log on the page, never a silent black canvas.
- Seeded PRNG (mulberry32, seed 1337). devicePixelRatio capped at 2, resize handled.
- 60fps at 1080p with audio running. Parameter changes ramped over ~50 ms — no zipper noise.
- Zero console errors.

SIZE: aim for 800–1,200 lines. If you run out of room, cut features, never the opening frame.

DO NOT: a near-black scene behind the overlay; a debug-looking spectrum; clicks or pops when patterns change; a flat 2D canvas with a fake glow.

OUTPUT: return only the complete HTML file, no commentary. If you have file tools, write it as pulse-engine-<model>.html and reply DONE.
```

## Outputs collected so far

Files only — no scores recorded yet. These are the run artefacts on eamon-hermes, kept so the same prompt can be re-judged later.

- **Sky Temple:** `/home/eamon/sky-temple.html` (51 KB, 2026-10-21 22:30) and `/home/eamon/Desktop/old prompt tests/sky-temple-minimax-m3-1-flash.html` + `sky-temple-deepseek-v4.1-flash-1017.html` (2026-10-20/21). One-shot, self-contained.
- **Older v2-era runs** (2026-10-20, `Desktop/old prompt tests/`): `city-test1-minimax-m3.1-flash.html` 703 KB, `cloth-lab-test1-…` 129 KB, `neon-drift-test1-…`, `test1-minimax-m3.1-flash.html` 724 KB.

Rule for judging: open from `file://` at 1920×1080 in a real browser. A 2D canvas faking depth is the failure mode v3.3 was written to catch.
```
