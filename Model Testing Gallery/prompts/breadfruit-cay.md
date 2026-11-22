# 006 — Breadfruit Cay

Create a pocket coral cay with a crescent reef on one side and a completely sheltered landing beach on the other. Let the viewer follow one swell around both horns of the reef.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Build a raised sandy centre with two breadfruit trees, a woven fish basket, a palm-leaf shade and a dugout drawn above the wet line. Reveal the dark base of the reef under pale coral rubble in the side elevation.

## Daylight and materials

Use clear tropical daylight. Give deep water a blue-green body and shallow water the colour of its sandy bed. Sparse trade clouds move soft shadows across sea, treetops and beach in turn.

## Environmental motion

- Split incoming wave fronts around the reef. They break white on the exposed rim, lose amplitude over the crest and wrap towards the landing in two smaller trains. Give the meeting fronts a moving pattern of short peaks.
- Let buoyant seagrass fragments mark entry through one breach and return through a deeper gap. Fringing grass bends inland while the sheltered beach only receives a thin intermittent wash.

## Cinematic camera

Start off the broken reef rim, then arc to the lagoon side without losing either horn. Preserve the base silhouette against a pale sea-coloured backdrop.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Trace a wave” to tint a few short crest segments for one passage. They should separate at the reef and reach the beach at different times, with visibly less height.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.