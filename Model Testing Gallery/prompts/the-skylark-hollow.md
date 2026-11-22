# 010 — The Skylark Hollow

Create a saucer of upland grass around a skylark nest, with one skylark climbing above the field. Let its ascent reveal the direction and height of wind over the little hollow.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Give the hollow an upwind bank, a shallow runnel, a flattened nesting patch beneath long grass and a bent fence with a single pale wool tuft. Leave space between the crest and the bird.

## Daylight and materials

Light it at golden hour from the western ridge, low enough for the bird’s moving shadow to touch the slope. Use subdued green in the hollows and straw tips on the exposed bank, with high drifting cloud behind.

## Environmental motion

- Make the wind stronger at the lip and weaker near the nest. A burst of seed husks lifts from one stem, crosses the hollow aloft and settles only after entering slower air behind the opposite bank.
- The skylark climbs in short beating arcs, briefly holds into wind and drops back into the long grass. Fold stems aside where the bird lands and let them spring partway over the hidden nest.

## Cinematic camera

Start above the hollow with bird and nest both in frame. From the opposite bearing, place the waving grass heads against the darker slope so their different heights read in silhouette.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Show sheltered air” by releasing a few pale husks at three different heights. The lowest should travel the least. Roots stay fixed and the bent fence should never move with the grass.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.