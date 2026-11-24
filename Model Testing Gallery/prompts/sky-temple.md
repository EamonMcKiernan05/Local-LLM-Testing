Build one self-contained HTML file: a floating Japanese temple island in the sky, built from voxel cubes in real 3D with raw WebGL. No libraries, no images, no external anything — you write the matrices, the buffers and the shaders.

THE FRAME at t=0: golden hour. Perspective camera at (16, 11, 20) looking at (0, 3.4, 0), vertical fov 34°. The island sits slightly right of centre, entirely inside the frame with at least 8% empty margin on every edge, against a warm amber-to-rose sky. A five-tier pagoda on the highest ground is the silhouette anchor. Overlay the title "SKY TEMPLE" in the lower left with one line of hint text under it, as HTML on top of the canvas.

SCENE, built in this order
1. The island: an irregular floating mass of 1-unit cubes — grass on top with a ragged edge, soil and rock strata below, tapering to a torn point about 60-80 cubes deep. Not a circle, not a cylinder, and not flat: it has real thickness from every angle.
2. The pagoda: seven shrinking tiers, wide dark roofs with upturned corner cubes, a gold finial, standing on the highest ground.
3. A red torii at the head of a curving stone path, four stone lanterns with a warm glow, two small houses with lit windows.
4. One cherry tree with a pink cube canopy, a small pond that picks up and reflects the lantern light.
5. THE CLOUD SEA — a hero element, not background. At least three stacked layers of soft cloud below the island, filling the lower third of the opening frame and fading down into haze. The layers drift at different speeds so the parallax reads as real depth. The island casts a visible shadow onto the top layer. A flat gradient, or clouds built but never visible on screen, fails this test.
6. Sky: a gradient that follows the time of day, a sun disc (and a moon at night), stars that fade in after sunset.

DAY / NIGHT CYCLE — a hard requirement
- One continuous 60-second cycle: dawn → noon → golden hour → night → dawn. t=0 is golden hour.
- The sun and moon orbit the scene; the key light direction, colour and intensity follow them; sky gradient, horizon haze and fog colour shift with the time; lanterns and windows ramp up at dusk and glow through the night; stars fade in.
- Golden hour is the best beat in the cycle: long warm light, strong contrast, a rim on the pagoda.
- Controls: a "Pause time" toggle, and three preset buttons MORNING / GOLDEN / NIGHT that jump the cycle to that state.

CAMERA & CONTROLS
- The default view IS the frame above. Drag to orbit — yaw free, pitch clamped so the camera never goes under the island; scroll to zoom with the distance clamped; light damping on both. The camera must never pass inside the pagoda or through the geometry.
- A "Cinematic" toggle: a slow low-angle orbit, about 40 seconds per revolution, with a gentle vertical drift. Any drag cancels it and hands back free orbit.
- A "Reset view" button returns to the poster frame.

UI: title, one-line hint "Drag to orbit · Scroll to zoom", the Cinematic and Pause toggles, the three time presets, Reset view. Fades to low opacity after 10 seconds idle and returns on mouse move. Nothing else.

ART DIRECTION
- Palette by day: grass #4f7a3a with #86b05a sunlit tops; soil #5a4130; rock #4a4a52; roofs #2a2622; lanterns and windows #ffb469; torii #c8402f. At golden hour the sky runs amber to rose; at night it is deep indigo #1b1f3b with cool moonlight and warm lantern pools.
- Light: one warm directional key from the upper left, cool ambient from the right. Every cube face reads at a different brightness — top brightest, sides progressively darker.
- Mood: quiet, storybook, a place rather than a level.

3D RULES — this is the test
- Cubes are real 3D geometry on a real x/y/z grid. Bake all cube faces into ONE vertex buffer (positions, normals, per-vertex colour) and draw it in one or a few calls. Never one draw call per cube.
- Depth test on, back faces culled. Front cubes must hide rear ones and the camera must see the underside of the island.
- Shadows are computed, not painted: project the geometry along the sun onto the cloud plane with a flattened matrix, or run a small shadow-map pass. The shadow direction must follow the moving sun.
- Perspective camera, never orthographic. The cinematic orbit and the user orbit are the same real camera path, not a zoom trick.

MOTION: the island bobs ±0.1 units on a slow sine; cherry petals are small quads drifting and tumbling in 3D; cloud layers drift at different speeds; lantern glow pulses gently.

TECHNICAL — hard rules
- One .html file. No libraries, no CDN, no fonts, no images, no textures, no external request of any kind. It must open by double-click from file://.
- Raw WebGL1 or WebGL2. Write your own mat4 helpers — perspective, lookAt, multiply.
- Typed-array vertex buffers; a vertex shader that transforms by your matrices; a fragment shader with directional light, ambient and distance fog, all driven by a time uniform.
- Pointer and wheel input must update camera state only — never rebuild the geometry.
- Check shader compile and program link status. On failure, print the log into a visible DOM element — never a silent black canvas.

DO NOT: draw the scene with Canvas 2D and call it 3D; use an orthographic camera and call it isometric; a pagoda that is five stacked boxes; one flat colour per face; painter-sort polygons instead of using the depth buffer; clouds that never appear in frame; a day/night cycle that only recolours the sky and leaves the light static; camera controls that are just a zoom.

OUTPUT: return only the complete HTML file, no commentary. If you have file tools, write it as sky-temple-<model>.html on the desktop and reply DONE.