# 003 — The Swallowtail Hayfield

Build a triangular downland hayfield with a forked swallow’s tail of uncut grass around two old boundary stones. A gust writes its passage across a field half cut for hay.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Fit a hay wagon at the wide end, a field gate at the acute corner and a footpath between the stones. Work three distinct bands into the landform: standing fescue, stubble and loose windrows. Expose flint nodules in the chalk beneath.

## Daylight and materials

Choose late afternoon just before hay is gathered. Ripe heads catch ivory light, fresh stubble throws short pin shadows and individual flints cool to lavender in the wagon’s shadow.

## Environmental motion

- Run a finite gust diagonally uphill. Bend each stem from its anchored root with progressively more travel towards its weighted head. Tall patches respond visibly before the sheltered patch at the hedge gap.
- Give loose hay its own motion. A few strands peel off the top of a row, tumble over stubble and snag against the nearest stone. The dense windrow keeps its overall shape.

## Cinematic camera

Start at the low corner looking along the cut lines from high enough to read the gust as a diagonal band. Let the far side of the circuit reveal the windrows behind the stones.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Send a gust”. Watch the same band pass the two stones at different times. Afterward the uncut ears rebound once or twice, while detached hay stays where it landed.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.