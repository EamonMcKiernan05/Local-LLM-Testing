# 024 — Kites over the Jute Bank

Build a miniature kite-flying common on a grassy river levee. Two handmade diamond kites work at very different heights over a bamboo washing platform.

## The miniature

Make a photorealistic real-time Three.js mini-world diorama. Give the bounded landscape a connected top, volumetric sides and a finished back. Compose it to fill roughly three quarters of the opening view. Use one daylight sun, soft sky fill and contact shadows consistent with terrain and structures. Arrange an earthen embankment as an elongated S. Put one flyer by a spool basket on the crest and another behind a jute screen on the lower berm. Give each kite a light paper skin, bowed spar and weighted cloth tail.

## Daylight and materials

Choose a fair afternoon with faint high cirrus and small hard-edged shadows on packed earth. Red and saffron paper should transmit sun when the kite tilts across it. The river below has a dull silver windward edge.

## Environmental motion

- Model kite lift from its relative airflow and tension from its bridle to the flyer. A moving gust first bends upwind grass and then lifts the kites. The lower one should respond later in the screen’s turbulent lee.
- Sag line segments under weight when slack and straighten them as tension builds. A tail follows a change of heading after the kite body. Keep both ends of each line visibly attached.

## Cinematic camera

Start broadside to the levee, separating the two kites against clear sky and the two flyers against grass. Set the orbit radius to fit both upper kite and the entire island at once.

Start with **Cinematic** on. Move the camera through a continuous **360° orbit** around a fixed point at the visual centre of the diorama, one full revolution about every 90 seconds. Use an elevated orthographic three-quarter view, stable radius, level horizon and constant angular speed through the loop seam. Keep the entire miniature framed with a little sky or breathing room on every bearing. Keep terrain, sunlight, weather and simulation in world coordinates.

Show a labelled **Cinematic** toggle. Dragging takes over with damped manual orbit. Wheel or pinch zooms within bounds. Re-enabling Cinematic eases back onto the circle from the current bearing. **Reset View** restores the opening composition. Camera controls must preserve the current physical state.

## Physics check

Add “Pay out line” for the lower flyer. More length first introduces slack, then permits a climb once tension returns. The other flyer keeps the original line length.

## Build and output

Deliver one self-contained HTML file that opens locally and works offline. Inline the actual Three.js runtime, scene code, shaders, UI and styles. Generate every mesh, texture, sky, reflection environment and particle in code. Use no external assets, runtime downloads, companion files or build step for the viewer.

Use a fixed seed for placement and repeatable forcing. Advance physics independently of render rate. Instance fine vegetation, reuse particles and cap pixel ratio. Start with the scene alive and demonstrate its main event automatically. Allow the viewer to repeat the physics check. If browser testing is available, inspect the event from both sides and run Cinematic through a complete revolution and a manual takeover. Return only the finished HTML.