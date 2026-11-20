# 004 — The Two Shores of Kettle Lake

Create a bowl of glacial gravel enclosing a small lake with two opposed jetties. A wind squall sets the sheltered lake rocking long after the surface chop has faded.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Build a steep wooded bank opposite a shallow grassy beach. Put a fishing creel and brass waterline marks on both jetties. The cutaway foreground exposes the basin profile and the submerged end of the beach steps.

## Daylight and materials

Use a breezy midsummer morning with broken high cloud. Keep the far grass silver-green, make the shallows pale over sand and show the shadow of each jetty below its planks.

## Environmental motion

- A wind pulse drives water towards the shallower end, then releases it. Superimpose a damped, basin-scale standing wave on the smaller wind ripples. The two ends rise and fall out of phase around a quieter centre.
- A moored canoe on the deep side pitches in short chop and rises more slowly with the local water level. Its loose line lifts off the water only as slack is taken up. Give the sheltered grass a delayed, smaller bend.

## Cinematic camera

Open high enough to see both marked posts. Choose the first quarter of the orbit to expose the basin profile and the opposite phases of the two waterlines.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Provide “End squall”. Short ripples should die away before the alternating wet bands on the two posts stop changing. The lake must retain its mean volume.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.