 # 005 — THE RAIN CATHEDRAL

Create THE RAIN CATHEDRAL: a photorealistic, real-time Three.js scene. A disused railway terminus becomes a monumental instrument of rain, with leaking roof bays and reflected iron arches. Make the opening frame feel like a carefully photographed place or physical object, with a clear focal point and convincing scale.

## DELIVERABLE & ASSET RULES

Deliver one HTML document containing the scene's JavaScript, shaders, CSS and UI inline. As in this single-file demo format, the only permitted external dependency is Three.js 0.160.0 and its matching official addons, using an import map with `three` mapped to `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` and `three/addons/` to `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/`. No other network requests, build tools or companion files. Generate every mesh, texture, environment map, particle and sound in code. Canvas textures and procedural shaders are allowed; downloaded images, HDRIs, models, fonts, samples and embedded copies of external art assets are forbidden. Use system fonts. Start the visuals automatically when the file opens.

## FRAMING & COMPOSITION

Look down the abandoned concourse from beneath one enormous arch. Alternate intact and broken roof bays so shafts of rain create rhythm, with a single warm maintenance room at the far end.

## REQUIRED SCENE

- Construct riveted lattice arches, purlins, cracked clerestory glass, old platform edges and buried rails, all following one believable structural grid.
- Add an unlit station clock, abandoned luggage trolley, peeling timetable boards drawn procedurally and weeds emerging from expansion joints.
- Shape puddles around floor unevenness and provide gutters, chains and broken downpipes that explain every concentrated stream of water.

## MATERIALS & LIGHT

Render chalky masonry, blackened steel, wet terrazzo and softly reflective puddles. Overcast daylight should remain luminous while deep roof pockets retain texture. Build detail at structural, surface and fine scales; use plausible roughness, thickness, contact shadows and reflected light. Keep highlights controlled and shadow detail readable. No voxel styling, faceted low-poly substitutes or uniformly glossy materials.

## MOTION & HERO MOMENT

- Rain falls through openings, hits the floor and produces expanding rings; runoff follows the roof and exits through the visible broken pipes.
- A gust pushes one dense rain curtain sideways, briefly clearing the distant clock and sending a wave of droplets along a hanging gutter chain.

## CAMERA & INTERACTION

Use a slow, near-symmetrical push down the concourse, with slight lateral drift to reveal the arch spacing. Begin in cinematic mode. Allow damped drag-to-orbit and wheel/pinch zoom within safe bounds; manual input takes control. Small CINEMATIC, RESET VIEW and PAUSE buttons restore the shot or freeze scene time. Keep camera movement available while paused. Use a restrained lower-left title and lower-right controls; fade the overlay after inactivity and restore it on pointer movement or keyboard focus.

## PROCEDURAL SOUND

Layer roof rain, distinct metal drips and spacious low-frequency room resonance. Synthesize it with Web Audio, initially muted; a SOUND button enables it after a user gesture. Keep levels comfortable, provide mute, and never gate the visuals behind audio permission.

## QUALITY & PERFORMANCE

Rain must not pass through intact roofing, and puddle reflections must track the roof rather than show a generic sky. Preserve genuine spatial depth during manual orbit; do not flatten the scene into a camera-facing illustration. Use deterministic generation with seed 1337 and frame-rate-independent motion; use fixed steps for simulated constraints. Target a steady 30–60 fps at 1080p, cap device pixel ratio, instance repeated details, pool particles and keep simulation counts bounded. Generate static maps once. Budget reflection, transmission and volumetric passes; reduce their resolution before sacrificing the hero geometry. Fill the viewport and handle resize. Avoid clipping, z-fighting, visible recycling and abrupt camera resets. If browser tools are available, inspect the rendered opening, hero moment, controls and any loop boundary and fix console errors; do not claim testing you could not perform.

## OUTPUT

Return only the finished HTML in one code block, with no prose, placeholders or unfinished features.
