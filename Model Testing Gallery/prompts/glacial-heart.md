# 007 — GLACIAL HEART

Create GLACIAL HEART: a photorealistic, real-time Three.js scene. Inside a translucent blue glacier, a meltwater stream runs beneath a vaulted tunnel filled with ancient air bubbles. Make the opening frame feel like a carefully photographed place or physical object, with a clear focal point and convincing scale.

## DELIVERABLE & ASSET RULES

Deliver one HTML document containing the scene's JavaScript, shaders, CSS and UI inline. As in this single-file demo format, the only permitted external dependency is Three.js 0.160.0 and its matching official addons, using an import map with `three` mapped to `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` and `three/addons/` to `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/`. No other network requests, build tools or companion files. Generate every mesh, texture, environment map, particle and sound in code. Canvas textures and procedural shaders are allowed; downloaded images, HDRIs, models, fonts, samples and embedded copies of external art assets are forbidden. Use system fonts. Start the visuals automatically when the file opens.

## FRAMING & COMPOSITION

Compose a low view along the stream toward a small white opening. Place a curved ice buttress close to the camera, revealing thickness, bubbles and layered internal fractures.

## REQUIRED SCENE

- Build an asymmetric ice tunnel with scalloped walls, overhangs, embedded dark sediment layers and hanging icicles of varied diameter.
- Route a shallow stream over rounded gravel with small waterfalls, undercut ice shelves and a narrow exposed gravel bank.
- Distribute trapped bubble strings and internal crack planes inside the ice volume; keep them beneath the surface rather than painted on it.

## MATERIALS & LIGHT

Use depth-dependent blue absorption and broad transmitted light. Put subtle moving caustic patterns on nearby ice while preserving fine frost on the driest ledges. Build detail at structural, surface and fine scales; use plausible roughness, thickness, contact shadows and reflected light. Keep highlights controlled and shadow detail readable. No voxel styling, faceted low-poly substitutes or uniformly glossy materials.

## MOTION & HERO MOMENT

- Animate downstream flow, little standing waves behind stones and drips that detach from icicle tips before making rings below.
- A bright patch of sunlight crosses the entrance, briefly lighting the interior bubble chains like a three-dimensional constellation.

## CAMERA & INTERACTION

Follow a very slow low glide along the gravel bank, with a restrained upward tilt during the transmitted-light reveal. Begin in cinematic mode. Allow damped drag-to-orbit and wheel/pinch zoom within safe bounds; manual input takes control. Small CINEMATIC, RESET VIEW and PAUSE buttons restore the shot or freeze scene time. Keep camera movement available while paused. Use a restrained lower-left title and lower-right controls; fade the overlay after inactivity and restore it on pointer movement or keyboard focus.

## PROCEDURAL SOUND

Create close drips, a thin stream and occasional quiet ice ticks with a long, soft echo. Synthesize it with Web Audio, initially muted; a SOUND button enables it after a user gesture. Keep levels comfortable, provide mute, and never gate the visuals behind audio permission.

## QUALITY & PERFORMANCE

The ice must read as a thick absorbing material, not transparent blue glass enclosing an empty room. Preserve genuine spatial depth during manual orbit; do not flatten the scene into a camera-facing illustration. Use deterministic generation with seed 1337 and frame-rate-independent motion; use fixed steps for simulated constraints. Target a steady 30–60 fps at 1080p, cap device pixel ratio, instance repeated details, pool particles and keep simulation counts bounded. Generate static maps once. Budget reflection, transmission and volumetric passes; reduce their resolution before sacrificing the hero geometry. Fill the viewport and handle resize. Avoid clipping, z-fighting, visible recycling and abrupt camera resets. If browser tools are available, inspect the rendered opening, hero moment, controls and any loop boundary and fix console errors; do not claim testing you could not perform.

## OUTPUT

Return only the finished HTML in one code block, with no prose, placeholders or unfinished features.
