# Cloth Lab (raw WebGL mesh, physics from scratch) — bench pack v3.4 prompt

From the one-shot demo bench pack. Verbatim.

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
