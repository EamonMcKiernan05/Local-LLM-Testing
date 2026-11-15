# One-Shot Demo Bench — prompt pack v3.4

Six one-shot prompts for comparing model craft: composition, light, motion, feel. One message, no follow-ups, same prompt for every model.

**Status (2026-10-22):** v3.4. **Sky Temple is an interactive scene now, not a still:** drag-orbit and zoom, a cinematic auto-orbit, a 60-second day/night cycle with time presets, and a cloud sea that has to be visible in the frame. v3.3 fixed delivery — one self-contained `.html` per test, nothing external, zero network requests. v3.2 briefly allowed a `three.min.js` beside the page; that was wrong for a bench, because the pack measures the model's coding and a library hands it the hard part. 3D means raw WebGL written from scratch: your own matrices, your own buffers, your own shaders. Five tests are hand-written WebGL, one is CSS 3D, and every file opens by double-click.

## Why v3.1 looked 2D

1. **A fixed projection is a drawing.** Canvas 2D has no depth buffer and no camera, so "3D" meant hand-sorting cubes and painting three faces each. Convincing at one angle, dead the moment anything moves.
2. **The technical rules forced it.** "Canvas 2D only, no WebGL, no libraries" is a hard ceiling on dimensionality, not a style choice.
3. **Depth cues were painted, not computed.** Shadows were darker polygons, fog was a gradient overlay, occlusion was draw order. None of it survives a camera move.

## What "3D" must mean here

Four requirements, in words, in every 3D prompt:

- **Real geometry** in a world coordinate system — vertex buffers, a transform pipeline — not sprites or stacked 2D layers.
- **A perspective camera** with position, target and fov stated, so frames from different models compare.
- **Light and occlusion computed** — per-face or per-pixel shading from a light in the scene, a depth buffer doing the hiding, the underside visible.
- **A camera move with real parallax** that returns exactly to frame 1 after 10 seconds.

Banned outright: a 2D canvas faking depth, orthographic-as-isometric, painter-sorted polygons pretending to be a renderer.

## What changed in v3.2 (kept)

- True 3D in every test, one subject one frame, a fixed camera at t=0 plus a 10-second looping move.
- A line budget per test: if you run out of room, cut features, never the opening frame.
- No self-checks in the prompt. Evidence checks live in the operator notes.
- Both output contracts: one fenced HTML block if the model has no file tools; write the file and reply DONE if it does.

## What changed in v3.3

- **The vendored library is gone.** A model handed three.js is not being tested on the same thing as one that is not, and the bench exists to measure coding ability.
- Every test is **one file, zero dependencies**. That raises the difficulty of the WebGL tests, and that is the point: hand-written matrix maths, vertex buffers and GLSL.
- Line budgets go up, because a WebGL pipeline is a few hundred lines before the scene starts.

## What changed in v3.4

- **Sky Temple becomes interactive.** Drag-orbit, scroll zoom, a cinematic auto-orbit toggle and a reset, replacing the fixed ±10° loop. The t=0 poster frame is unchanged, so stills from different models still compare.
- **A 60-second day/night cycle**, golden hour at t=0, with pause and MORNING / GOLDEN / NIGHT presets. The light, sky, fog, stars and lantern glow all follow it — not just the sky colour.
- **The cloud sea is a hero element.** Three stacked layers below the island, filling the lower third of the frame, drifting at different speeds, and catching the island's cast shadow. A model that builds clouds that never appear on screen has failed that part of the test, which is what the v3.3 MiniMax run did.
- Only Test 1 changed. The other five keep fixed cameras so the pack still has clean, comparable stills.

## How to run it (operator, not part of the prompt)

- **Sampler:** temperature 0.7, top_p 0.95. **No artificial output cap.** Set `max_tokens` to the highest value the endpoint accepts for that model — usually 64k on hosted endpoints, 128k where offered, unbounded on local llama.cpp. Leaving it unset is *not* unlimited: providers fall back to a small default (often 4k–8k) and the file truncates mid-tag. A run that hits the real ceiling produced too much and that is a legitimate result; a run cut off by a default setting is an operator mistake, not a model failure. One attempt each; a refusal is that model's result.
- **Open from `file://`** in Chrome at 1920×1080. No server, no assets folder, nothing beside the file.
- **Pass/fail gates:** page renders; console error count zero; **zero network requests in the Network tab**; the scene changes on its own — two frames 5 s apart differ by more than the idle bob.
- **Interaction gates for Sky Temple:** drag orbits and wheel zooms; Cinematic runs a slow orbit and any drag cancels it; Pause freezes the cycle; MORNING / GOLDEN / NIGHT change the *light*, not just the sky colour — check a lit face and a shadow direction at each preset. The cloud sea must be visible in the opening frame, filling the lower third.
- **Black-canvas checklist for hand-written WebGL** (the failures that actually happen): a shader compile or program link failure swallowed with no message; a zero-height canvas from CSS; a projection matrix that puts the scene behind the near plane; depth test left off so the last triangle wins; a buffer bound with the wrong stride or item size.
- **Screenshots on a software rasteriser are slow.** Under llvmpipe a WebGL scene renders fine but a CDP capture can exceed a 60 s timeout. Capture with the scene paused or raise the timeout; never record that as a model failure.
- **Score the frame first**, motion second, detail third. Judge blind — strip the model name from the filename.
- Record failures as failures. A black frame is a result.

## Scoring (1–5 each)

Composition · light and colour · motion and feel · craft detail · technical validity. Total out of 25.

---

## Test 1 — Sky Temple (raw WebGL, voxel geometry)

### PROMPT

```text
Build one self-contained HTML file: a floating Japanese temple island in the sky, built from voxel cubes in real 3D with raw WebGL. No libraries, no images, no external anything — you write the matrices, the buffers and the shaders.

THE FRAME at t=0: golden hour. Perspective camera at (16, 11, 20) looking at (0, 3.4, 0), vertical fov 34°. The island sits slightly right of centre, entirely inside the frame with at least 8% empty margin on every edge, against a warm amber-to-rose sky. A five-tier pagoda on the highest ground is the silhouette anchor. Overlay the title "SKY TEMPLE" in the lower left with one line of hint text under it, as HTML on top of the canvas.

SCENE, built in this order
1. The island: an irregular floating mass of 1-unit cubes — grass on top with a ragged edge, soil and rock strata below, tapering to a torn point about 60-80 cubes deep. Not a circle, not a cylinder, and not flat: it has real thickness from every angle.
2. The pagoda: seven shrinking tiers, wide dark roofs with upturned corner cubes, a gold finial, standing on the highest ground.
3. A red torii at the head of a curving stone path, four stone lanterns with a warm glow, two small houses with lit windows.
4. One cherry tree with a pink cube canopy, a small pond that picks up and reflects the lantern light.
5. THE CLOUD SEA — a hero element, not background. At least three stacked layers of soft cloud below the island, filling the lower third of the opening frame and fading down into haze. The layers drift at different speeds so the parallax reads as real depth. The island casts a visible shadow onto the top layer. A flat gradient, or clouds built but never visible on screen, fails this test.
6. Sky: a gradient that follows the time of day, a sun disc (and a moon at night), stars that fade in after sunset.

DAY / NIGHT CYCLE — a hard requirement
- One continuous 60-second cycle: dawn → noon → golden hour → night → dawn. t=0 is golden hour.
- The sun and moon orbit the scene; the key light direction, colour and intensity follow them; sky gradient, horizon haze and fog colour shift with the time; lanterns and windows ramp up at dusk and glow through the night; stars fade in.
- Golden hour is the best beat in the cycle: long warm light, strong contrast, a rim on the pagoda.
- Controls: a "Pause time" toggle, and three preset buttons MORNING / GOLDEN / NIGHT that jump the cycle to that state.

CAMERA & CONTROLS
- The default view IS the frame above. Drag to orbit — yaw free, pitch clamped so the camera never goes under the island; scroll to zoom with the distance clamped; light damping on both. The camera must never pass inside the pagoda or through the geometry.
- A "Cinematic" toggle: a slow low-angle orbit, about 40 seconds per revolution, with a gentle vertical drift. Any drag cancels it and hands back free orbit.
- A "Reset view" button returns to the poster frame.

UI: title, one-line hint "Drag to orbit · Scroll to zoom", the Cinematic and Pause toggles, the three time presets, Reset view. Fades to low opacity after 10 seconds idle and returns on mouse move. Nothing else.

ART DIRECTION
- Palette by day: grass #4f7a3a with #86b05a sunlit tops; soil #5a4130; rock #4a4a52; roofs #2a2622; lanterns and windows #ffb469; torii #c8402f. At golden hour the sky runs amber to rose; at night it is deep indigo #1b1f3b with cool moonlight and warm lantern pools.
- Light: one warm directional key from the upper left, cool ambient from the right. Every cube face reads at a different brightness — top brightest, sides progressively darker.
- Mood: quiet, storybook, a place rather than a level.

3D RULES — this is the test
- Cubes are real 3D geometry on a real x/y/z grid. Bake all cube faces into ONE vertex buffer (positions, normals, per-vertex colour) and draw it in one or a few calls. Never one draw call per cube.
- Depth test on, back faces culled. Front cubes must hide rear ones and the camera must see the underside of the island.
- Shadows are computed, not painted: project the geometry along the sun onto the cloud plane with a flattened matrix, or run a small shadow-map pass. The shadow direction must follow the moving sun.
- Perspective camera, never orthographic. The cinematic orbit and the user orbit are the same real camera path, not a zoom trick.

MOTION: the island bobs ±0.1 units on a slow sine; cherry petals are small quads drifting and tumbling in 3D; cloud layers drift at different speeds; lantern glow pulses gently.

TECHNICAL — hard rules
- One .html file. No libraries, no CDN, no fonts, no images, no textures, no external request of any kind. It must open by double-click from file://.
- Raw WebGL1 or WebGL2. Write your own mat4 helpers — perspective, lookAt, multiply.
- Typed-array vertex buffers; a vertex shader that transforms by your matrices; a fragment shader with directional light, ambient and distance fog, all driven by a time uniform.
- Pointer and wheel input must update camera state only — never rebuild the geometry.
- Check shader compile and program link status. On failure, print the log into a visible DOM element — never a silent black canvas.

DO NOT: draw the scene with Canvas 2D and call it 3D; use an orthographic camera and call it isometric; a pagoda that is five stacked boxes; one flat colour per face; painter-sort polygons instead of using the depth buffer; clouds that never appear in frame; a day/night cycle that only recolours the sky and leaves the light static; camera controls that are just a zoom.

OUTPUT: return only the complete HTML file, no commentary. If you have file tools, write it as sky-temple-<model>.html on the desktop and reply DONE.
```

---

## Test 2 — Dusk Cityline (CSS 3D, DOM only)

### PROMPT

```text
Build one self-contained HTML file: a city skyline at dusk, built as real 3D geometry with CSS 3D transforms. No canvas, no WebGL, no libraries — DOM and CSS only. The buildings are true 3D boxes with six faces seen in real perspective, not flat layered silhouettes.

THE FRAME at t=0: a low viewpoint across the river toward the skyline, camera looking slightly up. The stage has perspective: 1200px and transform-style: preserve-3d, inherited by everything inside it. River fills the bottom third, skyline across the middle, deep blue-violet sky above with an amber band at the horizon. A suspension bridge crosses the river on the right third. Title "DUSK CITYLINE" bottom left in small, wide-tracked capitals.

3D RULES — this is the test
- Every tower is a box: one element with six child faces (front, back, left, right, top, bottom) placed with translateZ / rotateY / rotateX inside a preserve-3d parent. Right-hand faces catch the sun; left and back faces fall into cool shade.
- Buildings sit at real x and z depths on one ground plane. Nearer towers occlude farther ones, and nothing floats or intersects.
- Camera: a 10-second loop that trucks ±6% along x and rises 2%, returning exactly to frame 1. Parallax between near and far towers must be visible.
- Window lights come from repeating-linear-gradient on each face, not one div per window.

ART DIRECTION
- Palette: sky #1a1e3a at the top to #e8895a at the horizon; concrete #3a3f4a with a warm bias; window light #ffd9a0 and #bcd8ff; sodium streetlights #ffab4d; water #0e1424.
- Light: the last sun low on the right, rimming the towers on that side. Shadowed faces stay cool.
- Mood: the ten minutes after sunset, city still busy.

BUILD, IN THIS ORDER
1. Ground plane, river plane and sky in the same 3D space.
2. 30–40 towers as 3D boxes at varied depths, widths and heights, window gradients, rooftop clutter on the nearest few.
3. The bridge in 3D: two towers, a catenary cable curve, a road deck with tiny warm lights along it.
4. Water: a mirrored, flipped copy of the towers with blur and reduced opacity, broken by drifting ripple bands.
5. Traffic: 6–10 headlight and tail-light pairs moving along the waterfront road.

MOTION: window lights switch on in small groups over the first 8 seconds; car lights glide; ripples drift. The loop is 10 seconds and returns exactly to the opening frame.

TECHNICAL — hard rules
- One .html file, all CSS and JS inline. No external anything: no fonts, images, libraries, CDN. System font stack only.
- No <canvas>, no WebGL. CSS 3D transforms and DOM only.
- 60fps: animate transform and opacity only, never layout properties.
- Seeded PRNG (mulberry32, seed 1337) for window lights and building variation.
- Zero console errors.


DO NOT: a flat layered skyline with a fake perspective scale; a purple gradient sky; one face per building; evenly spaced windows; a static backdrop.

OUTPUT: return only the complete HTML file, no commentary. If you have file tools, write it as dusk-cityline-<model>.html and reply DONE.
```

---

## Test 3 — Red Canyon (raw WebGL, raymarched)

### PROMPT

```text
Build one self-contained HTML file: a raymarched alien canyon at golden hour, in three dimensions. One fullscreen fragment shader written against the browser's own WebGL API. No libraries, no external files. Everything is computed in GLSL and the camera moves through the scene.

THE FRAME at t=0: looking down the canyon. Layered sandstone mesas on both sides converging to a hazy horizon; a giant ringed planet low and left, partly behind haze; three black monoliths floating above the floor casting long shadows toward the camera; mist pooling on the canyon floor; sun glare from the right. It must read as a matte painting, not a shader demo.

ART DIRECTION
- Palette: ochre #c98a4b, rust #8f3f2a, amber highlights, violet shadows #3a2a4f, pale gold haze at the horizon.
- Light: low sun from the right, long soft shadows, aerial perspective — distance loses contrast and shifts violet.
- Surface: every surface shaded. No flat unlit patches, no visible banding.

SCENE (SDF raymarching)
1. Canyon: stratified plateaus and mesas, a dry riverbed floor, one arch for silhouette interest.
2. Ringed planet: banded sphere, ring system with the planet's shadow across the rings.
3. Three to five black monoliths floating and slowly rotating, casting shadows.
4. Sky: golden gradient, sun disc with glare, sparse stars high up, thin drifting cloud noise.
5. Ground mist and a still pool with a rough fresnel reflection of the sky.

TECHNIQUE: sphere tracing, soft shadows, ambient occlusion, fog. Dither the sky and fog to kill banding. Fixed hash noise — deterministic every load.

CAMERA: a slow 10-second looping dolly down the canyon in real 3D space, eye height about 2 units, so near mesas slide past far ones with correct parallax. Mouse adds at most 5 degrees of parallax lean. No free look.

PERFORMANCE: render at 0.75x device resolution, upscale with linear filtering; under 100 march steps per pixel. Compile the shader before the first visible frame.

TECHNICAL — hard rules
- One .html file, all JS inline. Raw WebGL1 or WebGL2, one fullscreen quad, your own shader source in a string. No three.js, no helpers, no assets, no CDN, no external request.
- Resolution and pause buttons: resolution cycles 0.5x / 0.75x / 1x.
- Zero console errors. Never show a black frame while compiling — draw the first frame only when the program has linked.
- If WebGL2 is unavailable, fall back to WebGL1 or print a visible message. A blank page is a failed test.

SIZE: aim for 400–800 lines.

DO NOT: a wall of noise where mesas should be; visible banding; a black frame at load; a camera that never moves in depth.

OUTPUT: return only the complete HTML file, no commentary. If you have file tools, write it as red-canyon-<model>.html and reply DONE.
```

---

## Test 4 — Cloth Lab (raw WebGL mesh, physics from scratch)

### PROMPT

```text
Build one self-contained HTML file: a cloth lab with the physics and the 3D renderer both written from scratch. Raw WebGL for the geometry, Verlet physics in JavaScript. No libraries — cannon-es, ammo, rapier and matter.js are banned, and so is every CDN.

THE FRAME at t=0: a dark warm studio. A deep-red fabric sheet hangs from two dark wooden posts, sagging in the middle, lit from the upper left; one glossy black sphere sits on a low stone pedestal to the right; a soft elliptical shadow under both. Camera at (3.2, 2.0, 4.6) looking at (0, 1.1, 0), fov 40. It must read as fabric at a glance: visible folds, shading that changes across each fold, no spikes.

HOW TO DRAW IT
- The cloth is a 60 x 40 particle grid (2,400 particles) with real 3D positions. Each frame, write the positions into a Float32Array, recompute per-vertex normals from the neighbouring grid points, and upload both with bufferSubData.
- One indexed triangle list, drawn double-sided, shaded with a Blinn-Phong fragment shader. The normals are what sell the folds — never draw unshaded triangles.
- Pin the two top corners to the posts. Settle the cloth before the first visible frame. No loading state.

PHYSICS
1. Verlet integration: velocity from position delta, gravity 9.8, damping 0.99, fixed timestep with an accumulator.
2. Constraints: structural, shear and bend, 3–5 relaxation iterations. At rest the cloth must be perfectly still — any shimmer is a bug.
3. Collisions: against the sphere (push-out with friction) and the floor plane.
4. Interaction: drag any particle to grab and fling; T tears at the pointer by removing constraints, and high strain keeps breaking springs for a few seconds after; R resets.
5. HUD: small overlay with "CLOTH LAB", hints "drag / T tear / R reset", particle count and sim steps per second.

MOTION: the cloth settles within 3 seconds of load, then only the slowest residual sway. The camera orbits 8° over 10 seconds and returns exactly to frame 1.

TECHNICAL — hard rules
- One .html file, all CSS and JS inline. No libraries, no CDN, no images, no fonts beyond the system stack, no external request of any kind. Opens from file://.
- Raw WebGL1 or WebGL2 with your own mat4 helpers. Depth test on, back-face culling OFF for the cloth (it is double-sided).
- Typed arrays, no per-frame allocations. devicePixelRatio capped at 2, resize handled. 2,400 particles without a frame drop.
- Check shader compile status; on failure show the log on the page, never a silent black canvas.
- Seeded PRNG (mulberry32, seed 1337) for the initial drape jitter.
- Zero console errors. A blank canvas is a failed test.

SIZE: aim for 800–1,300 lines. If you run out of room, cut features, never the opening frame.

DO NOT: visible jitter at rest; the sheet exploding; a tear that unzips the whole cloth at once; flat unshaded triangles; a camera that never moves.

OUTPUT: return only the complete HTML file, no commentary. If you have file tools, write it as cloth-lab-<model>.html and reply DONE.
```

---

## Test 5 — Neon Drift (raw WebGL, playable)

### PROMPT

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

---

## Test 6 — Pulse Engine (raw WebGL + WebAudio)

### PROMPT

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
