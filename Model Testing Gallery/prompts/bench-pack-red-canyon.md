# Red Canyon (raw WebGL, raymarched) — bench pack v3.4 prompt

From the one-shot demo bench pack. Verbatim.

```text
Build one self-contained HTML file: a raymarched alien canyon at golden hour, in three dimensions. One fullscreen fragment shader written against the browser's own WebGL API. No libraries, no external files. Everything is computed in GLSL and the camera moves through the scene.

THE FRAME at t=0: looking down the canyon. Layered sandstone mesas on both sides converging to a hazy horizon; a giant ringed planet low and left, partly behind haze; three black monoliths floating above the floor casting long shadows toward the camera; mist pooling on the canyon floor; sun glare from the right. It must read as a matte painting, not a shader demo.

ART DIRECTION
- Palette: ochre #c98a4b, rust #8f3f2a, amber highlights, violet shadows #3a2a4f, pale gold haze at the horizon.
- Light: low sun from the right, long soft shadows, aerial perspective — distance loses contrast and shifts violet.
- Surface: every surface shaded. No flat unlit patches, no visible banding.

SCENE (SDF raymarching)
1. Canyon: stratified plateaus and mesas, a dry riverbed floor, one arch for silhouette interest.
2. Ringed planet: banded sphere, ring system with the planet's shadow across the rings.
3. Three to five black monoliths floating and slowly rotating, casting shadows.
4. Sky: golden gradient, sun disc with glare, sparse stars high up, thin drifting cloud noise.
5. Ground mist and a still pool with a rough fresnel reflection of the sky.

TECHNIQUE: sphere tracing, soft shadows, ambient occlusion, fog. Dither the sky and fog to kill banding. Fixed hash noise — deterministic every load.

CAMERA: a slow 10-second looping dolly down the canyon in real 3D space, eye height about 2 units, so near mesas slide past far ones with correct parallax. Mouse adds at most 5 degrees of parallax lean. No free look.

PERFORMANCE: render at 0.75x device resolution, upscale with linear filtering; under 100 march steps per pixel. Compile the shader before the first visible frame.

TECHNICAL — hard rules
- One .html file, all JS inline. Raw WebGL1 or WebGL2, one fullscreen quad, your own shader source in a string. No three.js, no helpers, no assets, no CDN, no external request.
- Resolution and pause buttons: resolution cycles 0.5x / 0.75x / 1x.
- Zero console errors. Never show a black frame while compiling — draw the first frame only when the program has linked.
- If WebGL2 is unavailable, fall back to WebGL1 or print a visible message. A blank page is a failed test.

SIZE: aim for 400–800 lines.

DO NOT: a wall of noise where mesas should be; visible banding; a black frame at load; a camera that never moves in depth.

OUTPUT: return only the complete HTML file, no commentary. If you have file tools, write it as red-canyon-<model>.html and reply DONE.
```
