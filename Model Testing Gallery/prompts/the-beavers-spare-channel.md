# 002 — The Beaver’s Spare Channel

Make a cutaway alder meadow where a little beaver lodge sits between two ponds. The star is an almost invisible side channel that wakes up when the upper pond fills.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Shape the land like a crooked figure eight. Show a dam woven from branches, a pale gnawed stump, a gravel inlet and a dry oxbow around one end of the dam. Give the lodge a low entrance just below the ordinary waterline.

## Daylight and materials

Use bright morning light through broken cumulus. The tawny dam casts thin branch shadows on silt. Willow shade cools the pond margins and underwater sticks lose contrast with depth.

## Environmental motion

- Feed water into the upper basin faster than it leaks between the sticks. The surface rises towards the saddle. At its low point a thin overflow joins into a stream down the dry oxbow and enters the lower pond off-centre.
- Let a floating aspen twig follow the current. It pauses in still water, spins where the overflow turns and drifts into sedges. Wet stems part at water level while the wind moves their upper tips independently.

## Cinematic camera

Open above the dam toe with both pond levels, lodge and saddle separated in depth. As the orbit rounds the dam, show the new stream joining the lower pond.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Spring pulse” to increase inlet flow briefly. Water reaches the relief channel only after the level reaches its lip. Closing the pulse leaves a shrinking thread and a dark strip of wet mud.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.