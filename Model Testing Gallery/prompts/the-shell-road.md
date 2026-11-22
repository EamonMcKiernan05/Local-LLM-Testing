# 012 — The Shell Road

Make a hooked sand island linked to a tiny mainland chapel by a strip of crushed shell. A rising tide cuts the road in two at a shallow dip.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Model an arched chapel door, a kissing gate, two pairs of tide posts and bent marram tufts. Separate the two beaches by their grain and slope. Give the route a crown high enough to remain dry at either end.

## Daylight and materials

Use soft late-afternoon sun. The shell road should start almost white and turn translucent grey as it wets. Keep the sea-facing slope bright in patches as small fair-weather clouds pass.

## Environmental motion

- Let short waves approach both flanks over different depths. First isolated tongues reach across the dip. Later the overlap becomes a continuous shallow crossing with a net current through the lowest part.
- Show shell fragments that shift only under stronger flow and wrack that floats away sooner. The marram bends from the advancing breeze with its deepest roots exposed in the cut face, above the active waterline.

## Cinematic camera

Open above the chapel looking back along the road. From the crosswise bearing, keep the two shores far enough apart in projection to show water crossing the dip.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add a slow “Tide height” control. At an intermediate setting some individual waves should still expose the dip between crests. At high water the two tide posts stand in uninterrupted water.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.