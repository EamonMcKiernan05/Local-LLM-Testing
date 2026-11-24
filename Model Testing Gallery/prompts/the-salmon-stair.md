# 025 — The Salmon Stair

Build a sockeye stream compressed into a miniature of three basalt steps. Make the important sight a salmon entering the current, leaping a low lip and landing in the pool that supplied the water.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Nest an old fish-counting shelter against a grassy moraine and give the stream a deep takeoff pocket and a narrow landing pool. Put a white measuring board on the shelter’s shaded side so passing fish are legible.

## Daylight and materials

Use crisp northern daylight with cool overhead fill and warm light on the rocks. Fish backs darken underwater and brighten when they break the surface. Keep water clear enough to show the approach.

## Environmental motion

- Route the main jet around an upstanding rock, leaving a slower rest pocket behind it. Fish hold position by swimming into the local velocity, then move to the lip, launch on a gravity-driven arc and re-enter with a local splash.
- The landing sends ripples into an adjacent pool held behind a gravel sill. Foam travels downstream from the fall rather than following the fish. Alder leaves above the lip flutter in a light crosswind.

## Cinematic camera

Frame the steps in diagonal profile so a whole leap reads against the shelter’s dark boards. The opposite orbit angle should reveal the submerged approach lane.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Open side bypass”. Part of the discharge takes a lower route, narrowing the jet at the main lip. Salmon should adjust their holding positions before the next jump.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.