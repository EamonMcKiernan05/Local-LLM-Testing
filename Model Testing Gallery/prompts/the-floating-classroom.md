# 029 — The Floating Classroom

Build a bright miniature lake village around a timber schoolhouse on a raft. A fixed flagpole on one bank gives the water level a reference as the floating buildings rise together.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Arrange a blue-roofed classroom, a little canoe landing, a separate toilet raft and a hinged gangplank between classroom and grassy levee. Include chalk marks on the pole, clay under the bank and exposed reed roots.

## Daylight and materials

Use hazy tropical morning sun softened by broad white clouds. Put real reflections of the roof and flagpole in sheltered water and break them into short strokes outside the reeds.

## Environmental motion

- Introduce a passing boat wave from one corner and a much slower seasonal lake rise in accelerated time. Allow rafts to pitch at different phases of the short wave but rise by the same long-term level.
- The gangplank pivots at its hinge and slides at its resting end. Its angle changes as the floating classroom approaches the high-water mark. A pair of moored canoes takes up slack before the lines pull taut.

## Cinematic camera

Start at the bank with the measured pole beside the classroom wall. As the camera circles, keep the gangplank slope and the extent of the water tile readable.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add a “Lake level” control that moves smoothly between two marks. The school and toilet raft should stay afloat at both levels while the bank pole and classroom floor have a different relative height.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.