# 026 — First Hooves at the Ford

Create a miniature piece of floodplain where four zebras cross a shallow brown ford one by one, leaving prints that fill with water behind them.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Give the island a steep dry approach, two small gravel bars and a grassy exit ramp with hoof-worn tracks. Build animals with articulated legs, distinct stripe patterns and a clear walking sequence.

## Daylight and materials

Choose low sun along the river so the stripes read against amber dust and brown water. Dry grass is straw at the top, green at the roots. Soft high clouds move patches of cool shade across the bars.

## Environmental motion

- Sample the sloping bed at each footfall. A grounded hoof on dry mud leaves a depression, at the margin squeezes out wet silt, and underwater displaces a small splash. Time every response to actual contact.
- Let the current carry each silt trail downstream. The following animal intersects the first animal’s still-dissipating wake. At the exit ramp, trampled grass bends down and recovers only partly.

## Cinematic camera

Open from the shallow bank with dark legs visible against bright water. Keep the crossing diagonal to the first quarter of the orbit so the prints and travelling plume remain separate.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Wait at bank” for the trailing pair. Their stripe reflections and splashes should appear only when released. Existing silt still moves and the first pair’s prints slowly fill.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.