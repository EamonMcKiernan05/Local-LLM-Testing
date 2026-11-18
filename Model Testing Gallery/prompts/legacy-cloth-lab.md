Build one complete, self-contained web demo: a cloth and rigid-body physics lab, with the physics written from scratch. This is a simulation-quality test.

DELIVERABLE
A single HTML file, self-contained: all HTML, CSS and JavaScript inline. Three.js r160 via importmap from unpkg — "three": https://unpkg.com/three@0.160.0/build/three.module.js and "three/addons/": https://unpkg.com/three@0.160.0/examples/jsm/ — ES modules, OrbitControls from three/addons. No assets. No build step, no TypeScript, no npm. Zero console errors.
NO physics libraries: cannon-es, ammo, rapier, physx, matter.js and the like are banned. Write the solver yourself (Verlet/XPBD or similar) — not a reworded copy of a published tutorial implementation.

THE SIMULATION
1. A cloth sheet — a grid of at least 60 x 40 = 2400 particles — pinned at its two top corners, hanging like a curtain between two posts. Structural, shear and bend constraints. It must drape and fold naturally with zero jitter at rest.
2. A solid sphere pedestal near the cloth that the cloth drapes over when pulled across it (cloth-vs-sphere collision).
3. A floor at ground level (cloth-vs-floor collision); gravity 9.8.
4. Interaction:
   - Left-drag any cloth particle: grab it (spring to cursor) and fling the cloth — it must ripple believably.
   - T key or right-click on the cloth: tear it — remove that particle's constraints so it splits and hangs open; for a few seconds after a tear, springs under high strain should keep breaking.
   - W: toggle gusty wind (smooth time-varying noise, not a constant push).
   - B: spawn 10 falling spheres (radius ~0.2m) that collide with the cloth — the cloth must catch them, drape around them and not explode.
   - R: reset the scene.
5. Fixed-timestep simulation with an accumulator (never step physics from raw frame delta), with enough solver iterations for stability. It must stay stable for minutes of abuse — flinging, tearing, dozens of balls.

RENDERING
- Cloth as a lit double-sided mesh with subtle sheen (back face must look right when it flips), glossy spheres, soft studio lighting and gentle shadows (real shadow maps or fake blob shadows — either, but the cloth must not look flat). F key toggles a wireframe view of the particle grid.

HUD
Small overlay: title "CLOTH LAB", key hints (drag / T tear / W wind / B balls / F wire / R reset), particle count, sim steps per second.

PERFORMANCE
- 2400+ particles at a comfortable 60fps: typed arrays, no per-frame allocations, flat constraint loops.

QUALITY BAR
- The cloth must look like fabric: no oscillating spikes, no visible interpenetration through itself, graceful tearing (never a whole-sheet explosion).

OUTPUT
Return the complete file as one HTML code block. No explanations, no commentary.
