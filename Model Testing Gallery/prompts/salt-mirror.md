 # 004 — SALT MIRROR

Create SALT MIRROR: a photorealistic, real-time Three.js scene. A geometric saltworks spreads across a coastal plain, its coloured evaporation ponds catching a moving gap in the clouds. Make the opening frame feel like a carefully photographed place or physical object, with a clear focal point and convincing scale.

## DELIVERABLE & ASSET RULES

Deliver one HTML document containing the scene's JavaScript, shaders, CSS and UI inline. As in this single-file demo format, the only permitted external dependency is Three.js 0.160.0 and its matching official addons, using an import map with `three` mapped to `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` and `three/addons/` to `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/`. No other network requests, build tools or companion files. Generate every mesh, texture, environment map, particle and sound in code. Canvas textures and procedural shaders are allowed; downloaded images, HDRIs, models, fonts, samples and embedded copies of external art assets are forbidden. Use system fonts. Start the visuals automatically when the file opens.

## FRAMING & COMPOSITION

Use an elevated oblique view with one foreground pond showing crystal detail and dozens of smaller basins leading to the sea. Break the geometry with a diagonal timber sluice channel.

## REQUIRED SCENE

- Create irregular rectangular basins separated by narrow earthen berms, with pink, ochre and pale turquoise brines at visibly different depths.
- Build wooden sluice gates, walkable boardwalks, small pumping wheels and crusted stakes; all water transfers must pass through actual openings.
- Place conical salt piles, rake marks, shallow drainage rivulets and polygonal crystals growing along exposed margins.

## MATERIALS & LIGHT

Use shallow translucent brine over granular beds, with rough salt rims and sharp reflections only on sheltered water. Thin clouds should cast broad, soft moving shadows. Build detail at structural, surface and fine scales; use plausible roughness, thickness, contact shadows and reflected light. Keep highlights controlled and shadow detail readable. No voxel styling, faceted low-poly substitutes or uniformly glossy materials.

## MOTION & HERO MOMENT

- A sluice periodically rises, releasing a narrow stream into the next basin; downstream ripples begin at the inflow and gradually decay.
- The hero moment is a cloud gap crossing the complex, making the mirror reflections illuminate sequentially while tiny salt crystals sparkle in the foreground.

## CAMERA & INTERACTION

Trace a slow high diagonal glide, keeping the sluice and the strongest reflection within the composition. Begin in cinematic mode. Allow damped drag-to-orbit and wheel/pinch zoom within safe bounds; manual input takes control. Small CINEMATIC, RESET VIEW and PAUSE buttons restore the shot or freeze scene time. Keep camera movement available while paused. Use a restrained lower-left title and lower-right controls; fade the overlay after inactivity and restore it on pointer movement or keyboard focus.

## PROCEDURAL SOUND

Generate trickling brine, light coastal wind and a subtle wooden gate creak. Synthesize it with Web Audio, initially muted; a SOUND button enables it after a user gesture. Keep levels comfortable, provide mute, and never gate the visuals behind audio permission.

## QUALITY & PERFORMANCE

Different pond colours must come from plausible depth and material variation; avoid opaque pastel tiles or uniformly glittering surfaces. Preserve genuine spatial depth during manual orbit; do not flatten the scene into a camera-facing illustration. Use deterministic generation with seed 1337 and frame-rate-independent motion; use fixed steps for simulated constraints. Target a steady 30–60 fps at 1080p, cap device pixel ratio, instance repeated details, pool particles and keep simulation counts bounded. Generate static maps once. Budget reflection, transmission and volumetric passes; reduce their resolution before sacrificing the hero geometry. Fill the viewport and handle resize. Avoid clipping, z-fighting, visible recycling and abrupt camera resets. If browser tools are available, inspect the rendered opening, hero moment, controls and any loop boundary and fix console errors; do not claim testing you could not perform.

## OUTPUT

Return only the finished HTML in one code block, with no prose, placeholders or unfinished features.
