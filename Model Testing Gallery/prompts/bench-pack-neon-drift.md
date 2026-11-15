# Neon Drift (raw WebGL, playable) — bench pack v3.4 prompt

From the one-shot demo bench pack. Verbatim.

```text
Build one self-contained HTML file: a playable synthwave racer in real 3D, using raw WebGL. This is a game-feel test. No libraries, no external files.

THE FRAME at t=0: the title card sits over a live 3D scene — a neon highway running to the horizon under a giant striped sun, magenta grid ground, a neon arch overhead, palms at the roadside. The scene is already moving behind the title: sun shimmer, palm sway, road flowing. Never a frozen backdrop.

ART DIRECTION
- Palette: sky #1a0b2e to #ff2e88 at the horizon; sun #ffd36e with magenta stripes; road #0d0a14 with cyan edge lines #35f0ff and magenta centre dashes #ff2ea6; grid #ff2ea6 at low opacity.
- Mood: 1986 arcade, confident and fast.

BUILD, IN THIS ORDER
1. Road: real 3D ribbon geometry extruded along a curving centreline with hills and bends, generated ahead and recycled. Seeded (1337) so the course is identical every run.
2. Roadside: neon arches at intervals, barriers, palms, mountain silhouettes, starfield — all placed in 3D.
3. The hovercraft: a simple 3D body built from boxes, chase camera behind and above it, banking into turns, gentle hover bob, thruster glow.
4. Gameplay: auto-accelerate; left/right or A/D steer with speed-sensitive weight; Space or Shift boosts with a heat meter that punishes overuse; rival cars to dodge; near-miss bonus with a 0.2 s slow-mo flash; crash to particles, "WRECKED — press R", R restarts; best score kept for the session.
5. HUD: speed, score, best, boost meter, monospaced digits that do not reflow, drawn in DOM over the canvas.
6. Audio: a synthesised engine hum whose pitch follows speed, plus a low bass pulse. WebAudio only, starts on the first key, M mutes. Nothing else.

3D RULES — this is the test
- The chase camera follows in world space with real perspective: the road must converge on a vanishing point that moves with the curve, and rival cars must grow as they approach.
- Hills are real elevation in the geometry, not a painted wobble on the horizon line.
- Depth test on, back-face culling on for the road and vehicles. Glow comes from additive blending and fog, not a bloom library.

MOTION: the first curve telegraphs before you reach it; the first rival arrives within 3 seconds of driving; FOV widens from 60° to 72° under boost.

TECHNICAL — hard rules
- One .html file, all CSS and JS inline. No libraries, no CDN, no external assets, no textures. Opens from file://.
- Raw WebGL1 or WebGL2 with your own mat4 helpers. Everything drawn procedurally in code; no images, no fonts beyond the system stack.
- Recycle road segments and roadside objects; no unbounded arrays, no per-frame allocations in the update loop.
- Check shader compile status; on failure show the log on the page, never a silent black canvas.
- Seeded PRNG (mulberry32, seed 1337) for the course. devicePixelRatio capped at 2, resize handled.
- Zero console errors.

SIZE: aim for 900–1,400 lines. If you run out of room, cut features, never the opening frame.

DO NOT: a pseudo-3D road drawn as scaled trapezoids on a flat canvas; steering that feels like a cursor; a static or dim title background; a HUD you cannot read mid-drive.

OUTPUT: return only the complete HTML file, no commentary. If you have file tools, write it as neon-drift-<model>.html and reply DONE.
```
