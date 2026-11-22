# 005 — Linen on the Bleaching Green

Create a river-island bleaching green with lengths of white linen pinned across closely mown grass. One loose corner lets the wind underneath and briefly shows the damp shape it has left on the turf.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Give the island two shoulders. Build a stone washhouse on one, a drying field on the other and a shallow dipping stair between them. Give each linen strip visible hems, creases and corner pegs.

## Daylight and materials

Use fresh late-morning sun and cool river bounce. Keep fold detail in white cloth, with darker translucent patches where the linen is still wet. Uncovered turf is upright and lighter at the tips.

## Environmental motion

- Move a gust from the river across the field. Water ripples appear first, bank grass leans second and then one cloth edge peels away. Integrate tension from the remaining pegs and give wet linen more weight than dry linen.
- Show the newly uncovered turf lying flat and dark. The loose corner lifts to the limit of its tether, flutters and settles with a little slack. Short river chop breaks around the dipping stair.

## Cinematic camera

Frame the cloth as diagonal bands seen over the washhouse roof. On the river side of the circle, the lifted hem should reveal a shadow on the turf.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Loosen one peg”. Replaying the gust with the corner fastened should produce small wrinkles. With it released, daylight reaches the damp rectangle beneath.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.