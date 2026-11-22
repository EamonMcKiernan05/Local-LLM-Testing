# 011 — The Blossom Frost Pocket

Build a shallow pear orchard in blossom around one little brick frost fan. Early sun catches the upper branches while frost lingers in a grassy hollow.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Cut the orchard as a scalloped slice with three descending rows, an open gate at the low point and a wheelbarrow full of empty picking baskets. Curve the trunks with age and let the white blossom reveal the shape of each branch.

## Daylight and materials

Use low apricot morning light from the uphill side. Backlight the bare tips of frosted grass, make thawed blades dark green and leave the shadow beneath each crown cool. A clear sky suits this quiet morning.
a
## Environmental motion

- Pool a thin layer of cold mist in depressions using the ground height. The fan draws slightly warmer air down and mixes a widening patch through the mist. Let the cleared patch drift downslope with the weak ambient breeze.
- Fan wash reaches nearby grass before the most distant blossom. Frost thaws gradually in the mixed patch, leaving individual droplets. When a branch shakes, freed droplets fall vertically before their smallest spray drifts.

## Cinematic camera

Open from below the lowest row looking across the hollow at the fan blades. Arc towards the gate to show where the mist can drain away.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Start frost fan”. Look for expanding clearance and delayed thaw downwind. Frost under the stone wall’s lee should remain visible when the fan-side grass is already wet.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.