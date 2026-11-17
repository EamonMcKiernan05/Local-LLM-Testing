 # 002 — THE BASALT ORGAN

Create THE BASALT ORGAN: a photorealistic, real-time Three.js scene. An immense coastal cave of columnar basalt breathes with the ocean, its dark interior briefly illuminated by reflected surf. Make the opening frame feel like a carefully photographed place or physical object, with a clear focal point and convincing scale.

## DELIVERABLE & ASSET RULES

Deliver one HTML document containing the scene's JavaScript, shaders, CSS and UI inline. As in this single-file demo format, the only permitted external dependency is Three.js 0.160.0 and its matching official addons, using an import map with `three` mapped to `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` and `three/addons/` to `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/`. No other network requests, build tools or companion files. Generate every mesh, texture, environment map, particle and sound in code. Canvas textures and procedural shaders are allowed; downloaded images, HDRIs, models, fonts, samples and embedded copies of external art assets are forbidden. Use system fonts. Start the visuals automatically when the file opens.

## FRAMING & COMPOSITION

Look out from a sheltered rock shelf toward a bright triangular cave mouth. Use irregular columns as foreground framing; preserve three depth layers and a small side opening high in the vault.

## REQUIRED SCENE

- Generate interlocking five-, six- and seven-sided columns with varied fracture heights, tilted fallen sections and convincing joints; avoid a perfect honeycomb grid.
- Build a submerged shelf, a central surge channel, barnacle bands and hanging wet ledges. The cave roof must connect structurally to the walls.
- Place rounded driftwood and a few shells on the protected shelf, with tiny nesting birds near the high opening for scale.

## MATERIALS & LIGHT

Wet basalt should be almost black at grazing angles but retain mineral detail. Use cool skylight, warm reflected sunlight and foam that is brightest near breaking crests. Build detail at structural, surface and fine scales; use plausible roughness, thickness, contact shadows and reflected light. Keep highlights controlled and shadow detail readable. No voxel styling, faceted low-poly substitutes or uniformly glossy materials.

## MOTION & HERO MOMENT

- Send long swells through the entrance, steepening in the narrowing channel and breaking against the back wall; foam should travel with the receding water.
- Every fourth surge drives a short spray plume through a fissure, briefly revealing a sunlit mist shaft before the cave darkens again.

## CAMERA & INTERACTION

Use a restrained lateral dolly along the shelf, with enough foreground parallax to reveal the cave's depth. Begin in cinematic mode. Allow damped drag-to-orbit and wheel/pinch zoom within safe bounds; manual input takes control. Small CINEMATIC, RESET VIEW and PAUSE buttons restore the shot or freeze scene time. Keep camera movement available while paused. Use a restrained lower-left title and lower-right controls; fade the overlay after inactivity and restore it on pointer movement or keyboard focus.

## PROCEDURAL SOUND

Synthesize low resonant surf, granular foam hiss and isolated drips with a cave-like echo. Synthesize it with Web Audio, initially muted; a SOUND button enables it after a user gesture. Keep levels comfortable, provide mute, and never gate the visuals behind audio permission.

## QUALITY & PERFORMANCE

Wave impact, foam and spray must share one timing source; no spray should appear before the water reaches the rock. Preserve genuine spatial depth during manual orbit; do not flatten the scene into a camera-facing illustration. Use deterministic generation with seed 1337 and frame-rate-independent motion; use fixed steps for simulated constraints. Target a steady 30–60 fps at 1080p, cap device pixel ratio, instance repeated details, pool particles and keep simulation counts bounded. Generate static maps once. Budget reflection, transmission and volumetric passes; reduce their resolution before sacrificing the hero geometry. Fill the viewport and handle resize. Avoid clipping, z-fighting, visible recycling and abrupt camera resets. If browser tools are available, inspect the rendered opening, hero moment, controls and any loop boundary and fix console errors; do not claim testing you could not perform.

## OUTPUT

Return only the finished HTML in one code block, with no prose, placeholders or unfinished features.
