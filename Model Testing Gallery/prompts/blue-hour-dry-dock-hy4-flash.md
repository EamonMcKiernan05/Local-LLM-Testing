 BLUE HOUR DRY DOCK

Create BLUE HOUR DRY DOCK: a photorealistic, real-time Three.js scene. A weathered ocean research vessel towers above a drained shipyard dock while a travelling inspection gantry passes beneath its hull. Make the opening frame feel like a carefully photographed place or physical object, with a clear focal point and convincing scale.

## DELIVERABLE & ASSET RULES

Deliver one HTML document containing the scene's JavaScript, shaders, CSS and UI inline. As in this single-file demo format, the only permitted external dependency is Three.js 0.160.0 and its matching official addons, using an import map with `three` mapped to `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` and `three/addons/` to `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/`. No other network requests, build tools or companion files. Generate every mesh, texture, environment map, particle and sound in code. Canvas textures and procedural shaders are allowed; downloaded images, HDRIs, models, fonts, samples and embedded copies of external art assets are forbidden. Use system fonts. Start the visuals automatically when the file opens.

## FRAMING & COMPOSITION

Shoot from low in the dock, looking along the keel toward the enormous stern propeller. Dock walls converge into blue evening haze; warm work lights provide a measured sense of scale.

## REQUIRED SCENE

- Model a coherent hull with bow flare, keel, rudder, propeller blades, railings and deck equipment; support it on regularly spaced keel blocks and side shores.
- Construct stepped concrete dock walls, ladders, service pipes, drainage channels, overhead cranes and a closed caisson gate at the far end.
- Add inspection platforms, coiled hoses and small puddles; keep walkways connected and leave a clear route for the moving gantry.

## MATERIALS & LIGHT

Separate matte antifouling paint, exposed steel, rust streaks, bronze propeller metal and damp concrete. Light the hull with broad work lamps rather than excessive emissive glow. Build detail at structural, surface and fine scales; use plausible roughness, thickness, contact shadows and reflected light. Keep highlights controlled and shadow detail readable. No voxel styling, faceted low-poly substitutes or uniformly glossy materials.

## MOTION & HERO MOMENT

- Move a wheeled inspection gantry slowly along its rails; its lamps sweep across weld seams and rivets as a cable reel turns at the correct rate.
- At the stern, a restrained welding burst on an elevated repair platform sends sparks down to a visible collection sheet; steam drifts from a drain.

## CAMERA & INTERACTION

Use a low 50-second tracking arc that passes the propeller without intersecting its blades or the support blocks. Begin in cinematic mode. Allow damped drag-to-orbit and wheel/pinch zoom within safe bounds; manual input takes control. Small CINEMATIC, RESET VIEW and PAUSE buttons restore the shot or freeze scene time. Keep camera movement available while paused. Use a restrained lower-left title and lower-right controls; fade the overlay after inactivity and restore it on pointer movement or keyboard focus.

## PROCEDURAL SOUND

Build quiet ventilation, a gantry motor and brief electrical crackle aligned with the repair activity. Synthesize it with Web Audio, initially muted; a SOUND button enables it after a user gesture. Keep levels comfortable, provide mute, and never gate the visuals behind audio permission.

## QUALITY & PERFORMANCE

The ship must feel supported and massive; no floating hull, tiny toy propeller or disconnected repair platform. Preserve genuine spatial depth during manual orbit; do not flatten the scene into a camera-facing illustration. Use deterministic generation with seed 1337 and frame-rate-independent motion; use fixed steps for simulated constraints. Target a steady 30–60 fps at 1080p, cap device pixel ratio, instance repeated details, pool particles and keep simulation counts bounded. Generate static maps once. Budget reflection, transmission and volumetric passes; reduce their resolution before sacrificing the hero geometry. Fill the viewport and handle resize. Avoid clipping, z-fighting, visible recycling and abrupt camera resets. If browser tools are available, inspect the rendered opening, hero moment, controls and any loop boundary and fix console errors; do not claim testing you could not perform.

## OUTPUT

Return only the finished HTML in one code block, with no prose, placeholders or unfinished features.
