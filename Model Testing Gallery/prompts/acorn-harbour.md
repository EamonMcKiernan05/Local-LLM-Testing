# 062 — Acorn Harbour

Build a complete riverside hamlet for thumb-sized inhabitants around the roots of one oak stump. The harbour is a puddle deep enough to float an acorn-cap coracle, and a single raindrop is a harbour-sized event.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Give the hamlet seedpod roofs, pegged bark jetties and grass-stem footbridges with tied joints. Put one tiny figure on the quay beside a carved mooring bollard. Show the whole stump, rooted turf and the hollow beneath the nearest buttress.

## Daylight and materials

Use soft morning light coming through an unseen high canopy, with moving patches shaped by real procedural leaves overhead. Bark is rough, seed husks satiny and clear puddle water has a curved meniscus beside the quay.

## Environmental motion

- Build a water bead on a bent grass blade, let it grow until it rolls from the tip and make it hit the harbour. Use surface tension at this scale: a brief impact crown, a closing dimple and spreading damped rings.
- The small round coracle should rock as each ring reaches its hull. The mooring cord limits drift, and the blade rebounds from losing the weight of its bead. Pebble breakwaters interrupt the rings.

## Cinematic camera

Open above the coracle with the blade tip isolated against dark bark. On the back of the stump, a little root stair and drying racks should keep the village readable during the orbit.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Release dew bead”. The leaf must spring up before the boat moves. Behind a breakwater the same impact should produce much weaker rocking.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.