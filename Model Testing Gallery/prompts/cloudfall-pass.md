# 009 — CLOUDFALL PASS

Create CLOUDFALL PASS: a photorealistic, real-time Three.js scene. A sea of cloud spills over a mountain saddle like a slow white waterfall, revealing an isolated weather station on the ridge. Make the opening frame feel like a carefully photographed place or physical object, with a clear focal point and convincing scale.

## DELIVERABLE & ASSET RULES

Deliver one HTML document containing the scene's JavaScript, shaders, CSS and UI inline. As in this single-file demo format, the only permitted external dependency is Three.js 0.160.0 and its matching official addons, using an import map with `three` mapped to `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` and `three/addons/` to `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/`. No other network requests, build tools or companion files. Generate every mesh, texture, environment map, particle and sound in code. Canvas textures and procedural shaders are allowed; downloaded images, HDRIs, models, fonts, samples and embedded copies of external art assets are forbidden. Use system fonts. Start the visuals automatically when the file opens.

## FRAMING & COMPOSITION

Use a wide view across a dark foreground ridge toward the saddle, with the station offset against the brightest falling cloud. Leave clear sky above for scale and breathing room.

## REQUIRED SCENE

- Generate angular, eroded ridges with scree, exposed strata and a continuous saddle; the cloud must visibly cross a real terrain threshold.
- Build a small corrugated weather hut, guyed mast, rotating anemometer, solar panel and narrow stone access steps.
- Populate sheltered crevices with low grasses, snow remnants and scattered cairns rather than evenly spaced vegetation.

## MATERIALS & LIGHT

Use cool valley haze and a warm sunrise rim. Clouds need self-shaded folds, soft terrain intersections and gradual thinning as they descend into drier air. Build detail at structural, surface and fine scales; use plausible roughness, thickness, contact shadows and reflected light. Keep highlights controlled and shadow detail readable. No voxel styling, faceted low-poly substitutes or uniformly glossy materials.

## MOTION & HERO MOMENT

- Advect cloud mass over the saddle, forming slow curls on the leeward side; animate the anemometer and grasses with the same prevailing wind.
- At the hero moment, a gap in the cloud exposes the valley floor far below, then closes without a hard transparency fade.

## CAMERA & INTERACTION

Make a slow aerial arc around the station while preserving the direction of the cloud flow and the depth of the valley. Begin in cinematic mode. Allow damped drag-to-orbit and wheel/pinch zoom within safe bounds; manual input takes control. Small CINEMATIC, RESET VIEW and PAUSE buttons restore the shot or freeze scene time. Keep camera movement available while paused. Use a restrained lower-left title and lower-right controls; fade the overlay after inactivity and restore it on pointer movement or keyboard focus.

## PROCEDURAL SOUND

Create airy ridge wind, a faint mast-cable whistle and subtle hut panel vibration. Synthesize it with Web Audio, initially muted; a SOUND button enables it after a user gesture. Keep levels comfortable, provide mute, and never gate the visuals behind audio permission.

## QUALITY & PERFORMANCE

The cloudfall must descend and dissipate convincingly; avoid a flat fog sheet sliding horizontally across the landscape. Preserve genuine spatial depth during manual orbit; do not flatten the scene into a camera-facing illustration. Use deterministic generation with seed 1337 and frame-rate-independent motion; use fixed steps for simulated constraints. Target a steady 30–60 fps at 1080p, cap device pixel ratio, instance repeated details, pool particles and keep simulation counts bounded. Generate static maps once. Budget reflection, transmission and volumetric passes; reduce their resolution before sacrificing the hero geometry. Fill the viewport and handle resize. Avoid clipping, z-fighting, visible recycling and abrupt camera resets. If browser tools are available, inspect the rendered opening, hero moment, controls and any loop boundary and fix console errors; do not claim testing you could not perform.

## OUTPUT

Return only the finished HTML in one code block, with no prose, placeholders or unfinished features.
