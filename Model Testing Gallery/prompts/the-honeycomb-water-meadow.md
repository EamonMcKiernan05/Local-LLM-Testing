# 019 — The Honeycomb Water Meadow

Build a mound of alpine turf made of lumpy hummocks and small pools. A pair of rubber boots on a timber boardwalk tells the viewer how small this entire wet meadow is.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Make the crown irregular and dense with cotton grass. The boardwalk steps down on short posts. In the cut face expose fibrous peat over waterlogged gravel, with pale roots hanging through the seam.

## Daylight and materials

Use warm light from just above the far horizon and a broad cool sky. Cotton-grass heads catch the light individually. Preserve little pools with different reflections according to which hummock shelters them.

## Environmental motion

- Send a shallow pulse through a channel mostly hidden under vegetation. Pools rise in sequence only when a low connecting neck overtops. The high pools stay isolated until a second, stronger pulse.
- Let cotton heads swing as masses on slender stems, with a slight overshoot after a gust. Their reflections change with the actual stem position. Small surface ripples die against the fibrous banks.

## Cinematic camera

Open over the boardwalk looking across the white cotton heads. Choose a high enough orbit for the temporary connections between pools to stay legible.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Raise water one notch”. A newly wet saddle should turn two mirrored surfaces into one. A dry higher hummock should still cast a distinct shadow across the joined pool.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.