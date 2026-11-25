# 007 — The Brook Beneath the Fold

Make a miniature limestone dale where a whole brook disappears beneath a sheep pasture and resurfaces under a ruined shepherd’s pen.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Slice the near face obliquely to show a vaulted underground passage. The top remains a continuous meadow of clover and cropped grass. Build a stone stile, hoof-scuffed chalk and a chalk-white sheep above the hidden stream.

## Daylight and materials

Use clean early-afternoon light. Keep the surface airy, cool the cut face with sky fill and send a narrow naturally lit patch into each cave mouth. Give submerged limestone a deeper grey.

## Environmental motion

- Split the inlet between gravel seepage and a narrow open throat. After a brief pulse, surface flow backs up at the throat while the underground passage carries a delayed rush to a lower spring.
- Make the spring disturb only its own pool at first. Downstream reed blades bend successively as the pulse travels. The topside pasture moves in wind independently of the water passing beneath it.

## Cinematic camera

Open with both the skylit meadow and the shadowed passage in view. Travel around the cut face until inlet, bend and spring can be read in sequence.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Release leaf boats” using three folded leaves. They vanish behind real rock where the passage turns, appear in the exposed section and emerge downstream in travel order.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.