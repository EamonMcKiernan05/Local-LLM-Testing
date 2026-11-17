 # 008 — MANGROVE AFTER DARK

Create MANGROVE AFTER DARK: a photorealistic, real-time Three.js scene. A narrow tropical creek glows only where moving water disturbs bioluminescent organisms beneath tangled mangrove roots. Make the opening frame feel like a carefully photographed place or physical object, with a clear focal point and convincing scale.

## DELIVERABLE & ASSET RULES

Deliver one HTML document containing the scene's JavaScript, shaders, CSS and UI inline. As in this single-file demo format, the only permitted external dependency is Three.js 0.160.0 and its matching official addons, using an import map with `three` mapped to `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` and `three/addons/` to `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/`. No other network requests, build tools or companion files. Generate every mesh, texture, environment map, particle and sound in code. Canvas textures and procedural shaders are allowed; downloaded images, HDRIs, models, fonts, samples and embedded copies of external art assets are forbidden. Use system fonts. Start the visuals automatically when the file opens.

## FRAMING & COMPOSITION

Position the camera just above the water, with arching roots in the foreground and a crescent moon reflected down the open channel. Keep most of the scene naturally dark.

## REQUIRED SCENE

- Generate branching trunks and stilt roots that enter the mud at believable angles; vary root thickness and avoid unsupported floating branches.
- Place waxy leaves, oyster clusters, exposed mud ridges and a half-submerged fallen branch across one side of the channel.
- Include a small school of slender fish and one slowly moving horseshoe crab on the visible muddy shelf.

## MATERIALS & LIGHT

Balance cool moonlight with restrained blue-green emission close to disturbed water. Wet bark should catch narrow highlights, while the foliage keeps a dense layered silhouette. Build detail at structural, surface and fine scales; use plausible roughness, thickness, contact shadows and reflected light. Keep highlights controlled and shadow detail readable. No voxel styling, faceted low-poly substitutes or uniformly glossy materials.

## MOTION & HERO MOMENT

- Fish leave short fading luminous wakes; ripples from falling droplets activate tiny rings of light that dissipate independently of the moon reflection.
- A gentle current pulse flows around the fallen branch, briefly revealing a branching network of glowing eddies before the creek returns to darkness.

## CAMERA & INTERACTION

Drift along a short collision-free path between roots, maintaining a low angle and letting luminous wakes pass beneath the lens. Begin in cinematic mode. Allow damped drag-to-orbit and wheel/pinch zoom within safe bounds; manual input takes control. Small CINEMATIC, RESET VIEW and PAUSE buttons restore the shot or freeze scene time. Keep camera movement available while paused. Use a restrained lower-left title and lower-right controls; fade the overlay after inactivity and restore it on pointer movement or keyboard focus.

## PROCEDURAL SOUND

Synthesize insects, isolated droplets and soft water movement; keep the night ambience spatially restrained. Synthesize it with Web Audio, initially muted; a SOUND button enables it after a user gesture. Keep levels comfortable, provide mute, and never gate the visuals behind audio permission.

## QUALITY & PERFORMANCE

Bioluminescence must follow disturbance and decay; the entire river must not become a uniformly emissive blue plane. Preserve genuine spatial depth during manual orbit; do not flatten the scene into a camera-facing illustration. Use deterministic generation with seed 1337 and frame-rate-independent motion; use fixed steps for simulated constraints. Target a steady 30–60 fps at 1080p, cap device pixel ratio, instance repeated details, pool particles and keep simulation counts bounded. Generate static maps once. Budget reflection, transmission and volumetric passes; reduce their resolution before sacrificing the hero geometry. Fill the viewport and handle resize. Avoid clipping, z-fighting, visible recycling and abrupt camera resets. If browser tools are available, inspect the rendered opening, hero moment, controls and any loop boundary and fix console errors; do not claim testing you could not perform.

## OUTPUT

Return only the finished HTML in one code block, with no prose, placeholders or unfinished features.
