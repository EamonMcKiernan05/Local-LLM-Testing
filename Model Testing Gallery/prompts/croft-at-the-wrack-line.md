# 001 — The Croft at the Wrack Line

Build a Manx-inspired croft perched on a wedge of folded slate. A single green comber sends seawater through a notch and almost reaches a pair of boots left on the steps.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Put a limewashed cottage and peat stack on the high shoulder. Curl a stone wall around a grassy yard, then drop a path through sea thrift to a shingle apron. Expose the folded bedding beneath it on the near face.

## Daylight and materials

Use a clear golden evening. Pick out blades with warm side light, keep the slate blue in the shade, and give damp shingle a narrower highlight than dry stones. A detached cloud throws a soft patch of shade offshore.

## Environmental motion

- Advance a swell train across a sloping seabed. Crests steepen at the shoal, spill against the ledge and feed a shallow tongue through the notch. Trace its highest reach with stranded flecks of wrack as the sheet drains.
- Drive grass with wind blowing inland. Tall seed stems bow over the exposed wall cap while short grass immediately behind it barely stirs. Spray starts at crest impact and falls downwind.

## Cinematic camera

Open from the seaward corner with both boots silhouetted against the pale step. Arc towards the gable until the notch and wet track make a continuous line.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Give the viewer a “Larger set” button. The next crest carries wrack one step higher. The cottage yard stays dry and the extra water finds its way back through the notch.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.