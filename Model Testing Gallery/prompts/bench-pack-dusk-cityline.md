# Dusk Cityline (CSS 3D, DOM only) — bench pack v3.4 prompt

From the one-shot demo bench pack. Verbatim.

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
