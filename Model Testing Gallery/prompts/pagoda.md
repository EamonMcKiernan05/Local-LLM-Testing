# Pagoda — one-shot prompt

Captured from the DeepSeek Harness session log. Verbatim, as sent.

```text
Create one complete, self-contained HTML file for THE PAGODA, a photorealistic real-time 3D TINY WORLD in three.js: a Japanese-stye pagoda tower, with smaller and its courtyard on a chunk of land floating on a plain white page, in warm late-afternoon sun, as a self-running scene with no interaction, only camera movements.

THE FRAMING, the tiny world:
- One irregular, organic Island floats in the clear blue sky, **no clouds**, spanning about 75 percent of the frame width.
- A jagged, layered underside with visible depth, not a flat disc or a smooth blob.
- A top surface that reads as a Japanese garden: grass, moss, soil, stone paths, stone steps, planted areas, rocks, and a small courtyard/plaza.
- The island bobs very gently, as if floating.
- The default camera view is a FIXED ORTHOGRAPHIC ISOMETRIC view, about 30 degrees down and 45 degrees around.
- Orbit by dragging, zoom by scrolling. Smooth easing.
- Cinematic mode button: a slow, elegant orbit around the island.
- Reset view button: returns to the FIXED ORTHOGRAPHIC ISOMETRIC view.

THE LOOK: PHOTOREALISTIC, at full resolution.
- No pixelation and no dithering: realism changes the rendering, never the framing.
- Physically based wood, glass, mortar, slate and timber roofs, weathered oak, grass, soil and water.
- One low warm sun from the side with real soft shadows and contact shadows, and a soft sky fill so no shadow is ever black.
- No low-poly, flat shading, plastic surfaces or stained-glass look.

THE PAGODA is a real, convincing Japanese-style pagoda tower filling the island:
- One dominant Japanese-style pagoda or tower, multi-tiered, with eaves, railings, brackets, and a finial. It is the architectural hero.
- Warm interior lantern light, readable roof silhouettes, and believable tier stacking.
- A few smaller Japanese-style houses or huts around the garden, with pitched roofs, wooden walls, lit windows, and small verandas or porches.
- They must feel like part of the same village/temple complex, not random.
- A red/vermilion torii gate at the approach to the temple, with a plaque, ropes, and paper streamers.
- A stone path from the torii through the garden to the pagoda, with steps and a plaza.
- Stone lanterns and/or hanging paper lanterns along the path, with warm glow at night.
- A large cherry blossom tree on the island with a **detailed branching structure**: trunk, main limbs, forked branches, visible twigs.
- Petals drift all around the island and beyond it, originating from the tree, with variation in speed, height, and rotation.
- A pond with a stone rim/collar, lily pads, lotus flowers, reeds, and a few boulders.
- The pond surface must use **real-time reflections** of the island, sky, and lantern light. Not a flat sky tint.
- The reflective surface must cover the pond all the way to the stone rim. **No dark border, no uncovered strip of old water, no ring where the reflection stops.**
- Every part is physically connected and supported.

THE ISLAND AND ITS LIFE:
- Tiny PEOPLE go about their day: traditional Japanese-dressed women walking up and down the paths, a two Samurai guards pacing the plaza perimeter a child sat by the pond.
- A few chickens peck in the plaza, and ducks swim around the pond

THE LOOP: one seamless loop of about 24 seconds. Every motion is built from the loop time, so the last frame flows straight into the first with no jump.
- The people walk their routes and return to where they began.
- The pond water ripples, the ducks circle.
- Shadows agree with the sun.
- Nothing floats off the island except the falling crumbs and leaves.

Make it fill the window, resize cleanly, run smoothly at 15-30 fps and start with zero console errors. Draw everything in code; never fetch or hotlink an image, texture or model. Deliver it as a single self-contained HTML file; any libraries are allowed.

Add sound: a gentle original music track that suits the scene plus ambient sound and sound effects for the action, all synthesized in code, with a small 'click for sound' hint, starting on the first click. Log audio events to the console to confirm they fire, since you can't hear them.

UI
- Title in the **lower-left**: a large, elegant serif title, e.g. `SKY TEMPLE` (or your own evocative name), with a smaller subtitle/hint below it.
- Controls in the **lower-right**: CINEMATIC and RESET VIEW buttons. Keep them small, legible, and consistent.
- Hint: “Drag to orbit · Scroll to zoom”.
- UI fades out after ~10 seconds of inactivity and wakes on pointer movement. It must not block camera input.

TESTING PROTOCOL

You must test the actual rendered output in a **local headed Chromium**, using the browser MCP/Playwright tools. Do not rely on code inspection or unit tests. Do not claim a feature works unless you have seen it.
```
