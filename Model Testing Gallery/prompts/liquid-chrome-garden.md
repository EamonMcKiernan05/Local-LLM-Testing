# 017 — LIQUID CHROME GARDEN

Create LIQUID CHROME GARDEN: a photorealistic, real-time Three.js scene. Reflective liquid-metal droplets roll across a gently tilting ceramic tray, merging around sculptural stone islands. Make the opening frame feel like a carefully photographed place or physical object, with a clear focal point and convincing scale.

## DELIVERABLE & ASSET RULES

Deliver one HTML document containing the scene's JavaScript, shaders, CSS and UI inline. As in this single-file demo format, the only permitted external dependency is Three.js 0.160.0 and its matching official addons, using an import map with `three` mapped to `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` and `three/addons/` to `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/`. No other network requests, build tools or companion files. Generate every mesh, texture, environment map, particle and sound in code. Canvas textures and procedural shaders are allowed; downloaded images, HDRIs, models, fonts, samples and embedded copies of external art assets are forbidden. Use system fonts. Start the visuals automatically when the file opens.

## FRAMING & COMPOSITION

Use a macro landscape composition: large droplets in front, three dark islands in the middle and a luminous studio strip reflected across the liquid.

## REQUIRED SCENE

- Create a shallow off-white ceramic tray with a raised lip, subtle glaze imperfections and a visible pivoting support.
- Model rounded basalt islands embedded in the tray and a continuous liquid surface made from merging droplets with changing contact footprints.
- Add a few tiny satellite beads, but keep the total amount of liquid stable as large drops combine and divide.

## MATERIALS & LIGHT

Generate a studio environment in code with broad dark and bright panels. The metal needs sharp coherent reflections, while ceramic and stone remain materially distinct. Build detail at structural, surface and fine scales; use plausible roughness, thickness, contact shadows and reflected light. Keep highlights controlled and shadow detail readable. No voxel styling, faceted low-poly substitutes or uniformly glossy materials.

## MOTION & HERO MOMENT

- Tilt the tray slowly about two axes; droplets accelerate downhill, deform on contact and merge using a smooth implicit surface.
- At the hero moment, two large drops meet around opposite sides of an island and reconnect into a reflective horseshoe before separating.

## CAMERA & INTERACTION

Track the main droplet cluster with a gentle low orbit; never hide the tray's tilt or the islands' contact points. Begin in cinematic mode. Allow damped drag-to-orbit and wheel/pinch zoom within safe bounds; manual input takes control. Small CINEMATIC, RESET VIEW and PAUSE buttons restore the shot or freeze scene time. Keep camera movement available while paused. Use a restrained lower-left title and lower-right controls; fade the overlay after inactivity and restore it on pointer movement or keyboard focus.

## PROCEDURAL SOUND

Use quiet support-mechanism creaks and restrained low liquid movement. Synthesize it with Web Audio, initially muted; a SOUND button enables it after a user gesture. Keep levels comfortable, provide mute, and never gate the visuals behind audio permission.

## QUALITY & PERFORMANCE

Reflections must move continuously across merging surfaces; no sphere intersections, popping metaball seams or disappearing volume. Preserve genuine spatial depth during manual orbit; do not flatten the scene into a camera-facing illustration. Use deterministic generation with seed 1337 and frame-rate-independent motion; use fixed steps for simulated constraints. Target a steady 30–60 fps at 1080p, cap device pixel ratio, instance repeated details, pool particles and keep simulation counts bounded. Generate static maps once. Budget reflection, transmission and volumetric passes; reduce their resolution before sacrificing the hero geometry. Fill the viewport and handle resize. Avoid clipping, z-fighting, visible recycling and abrupt camera resets. If browser tools are available, inspect the rendered opening, hero moment, controls and any loop boundary and fix console errors; do not claim testing you could not perform.

## OUTPUT

Return only the finished HTML in one code block, with no prose, placeholders or unfinished features.
