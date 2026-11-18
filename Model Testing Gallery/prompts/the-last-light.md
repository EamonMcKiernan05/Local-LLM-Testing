 Create one complete, self-contained HTML file for THE LAST LIGHT, a photorealistic real-time 3D scene in three.js: a weathered lighthouse on a rugged rocky island surrounded by an animated ocean. Waves roll in and break against the rocks, the lighthouse beam sweeps across the water, and a warm sunset gradually gives way to a star-filled night. The camera slowly orbits the island, with optional drag-to-orbit and scroll-to-zoom interaction.

THE FRAMING AND WORLD:
- One irregular, natural rocky island surrounded by open ocean stretching to the horizon. This is a real coastal landscape, not a floating island or miniature mounted on a disc.
- The island occupies roughly 60–70 percent of the frame width in the default view, leaving enough visible ocean to appreciate the waves, reflections, and sweeping light.
- Use a cinematic perspective camera with a slightly elevated viewpoint. Keep the lighthouse silhouette readable against the sky and the shoreline clearly visible.
- The island has believable depth and geology: jagged cliffs, fractured rock faces, ledges, crevices, and partially submerged boulders.
- The main landmass is one connected solid mesh, with additional rocks embedded naturally into the terrain.
- The upper surface includes weathered stone, patches of coastal grass, exposed soil, and a narrow winding path.
- The ocean meets a soft atmospheric horizon. No visible water-plane edges, empty background gaps, or obvious boundary between sky and sea.

THE LOOK: PHOTOREALISTIC AND ATMOSPHERIC.
- Physically based materials for rough stone, weathered painted masonry, timber, corroded metal, glass, grass, and water.
- Use procedural texture variation, surface roughness, and subtle normal detail so materials remain convincing at different viewing distances.
- Rocks near the waterline are darker, wetter, and more reflective than the dry upper cliffs.
- Begin with a low warm sun, long soft shadows, and cool sky fill. Shadows retain detail rather than becoming completely black.
- Use restrained bloom around bright lights, realistic exposure, and subtle distance haze.
- No low-poly appearance, flat shading, plastic surfaces, excessive bloom, pixelation, or dithering.

THE LIGHTHOUSE AND ITS SURROUNDINGS:
- One dominant lighthouse is the architectural hero: a tall, slightly tapered masonry tower with weathered off-white paint, a darker stone foundation, and subtle salt stains.
- Include a proper entrance, narrow inset windows, visible window frames, a maintenance balcony, metal railings, structural brackets, and a glazed lantern room beneath a metal roof.
- The lantern room contains a recognizable lamp and lens assembly. Its glass must remain transparent enough to reveal the mechanism.
- Architectural components are physically connected and supported. No floating railings, disconnected roofs, or doors opening into empty space.
- A small keeper’s cottage sits beside the lighthouse, with a pitched roof, chimney, timber door, and warm interior windows.
- A stone path connects the cottage, lighthouse entrance, and a modest landing reached by steps cut into the rock.
- Add a few purposeful coastal details: mooring posts, coiled rope, a weathered bench, and a low retaining wall. Keep the composition uncluttered.
- Everything belongs to the same exposed, weather-beaten island.

THE OCEAN AND BREAKING WAVES:
- The ocean must have actual animated surface displacement, not just scrolling texture.
- Combine broad rolling swells with smaller overlapping waves and fine surface ripples. Avoid obvious repeated patterns.
- Surface normals and reflections must respond to the displaced water.
- Waves travel coherently toward the island, steepen near the rocks, and produce localized white foam and spray when they strike.
- Breaking waves should read as a sequence: approaching swell, impact, upward splash, spreading foam, and retreating water.
- Foam collects briefly around rocks, stretches with the moving water, and gradually dissolves. Do not use a static white ring around the island.
- Generate occasional spray particles at actual impact locations. They rise, fall under gravity, and disappear naturally.
- Use believable shallow-water colour variation near submerged rocks, transitioning into deeper blue-green water offshore.
- Water must not visibly pass through the island, flood the cottage, or expose gaps beneath the shoreline.
- The water includes real-time reflections of the sky, island, lighthouse, and lights, distorted by the waves. A flat sky-coloured surface is insufficient.
- Sunlight produces a broken shimmering reflection across the moving sea, evolving naturally as the sun sets.

THE LIGHTHOUSE BEAM:
- The lamp rotates smoothly inside the lantern room, completing one revolution roughly every 10–14 seconds.
- The visible beam, lamp orientation, illumination on nearby surfaces, and moving reflection on the water must remain synchronized.
- Show a softly scattered shaft of light through sea haze, with gradual falloff and soft edges. It must not look like an opaque solid cone.
- The beam becomes increasingly visible as the sky darkens, while remaining subtle during sunset.
- As it sweeps over the ocean, create a moving, fragmented highlight that follows the wave surface.
- Nearby rocks and buildings respond to the light where appropriate. Solid terrain must occlude it rather than allowing it to shine through the island.
- Avoid sudden brightness changes, flickering, and hard-edged transparent geometry.

THE SKY AND SUNSET-TO-NIGHT TRANSITION:
- Start in warm late sunset, with an amber horizon, soft pink tones, and cooler blue overhead.
- Over approximately 90 seconds, transition smoothly through sunset, blue twilight, and deep night.
- Sun position, sky colour, ambient light, exposure, water reflections, and shadow direction evolve together.
- A few thin, distant clouds drift slowly and catch the changing light without obscuring the lighthouse.
- Stars fade in gradually as daylight disappears. Vary their brightness and size subtly; avoid uniform dots or exaggerated twinkling.
- A restrained moon and cool moonlight provide enough illumination to keep the island readable at night.
- Cottage windows and small path lights become noticeable as darkness falls.
- Once night is established, the scene continues indefinitely with moving waves, clouds, and the rotating beam. Do not abruptly reset to sunset.

THE ISLAND AND ITS LIFE:
- Coastal grasses bend gently in the prevailing wind.
- A few seabirds glide around the island during sunset, banking naturally and facing their direction of travel.
- Birds follow varied, smooth routes without clipping through the tower or repeatedly crossing the camera.
- Occasional low sea mist drifts near the shoreline, remaining subtle enough to preserve the scene’s detail.
- All motion uses elapsed time and remains consistent across different frame rates. No abrupt resets or synchronized mechanical movement.

CAMERA AND INTERACTION:
- Start with a slow, elegant cinematic orbit around the island.
- Dragging allows smooth manual orbiting; scrolling controls zoom with sensible minimum and maximum distances.
- Pause automatic orbiting during manual interaction and resume gently after a short period of inactivity when cinematic mode is enabled.
- Keep the camera above the water and prevent it from entering the terrain or lighthouse.
- A CINEMATIC button toggles automatic orbiting.
- A RESET VIEW button smoothly restores the opening framing without restarting the sky transition.
- Camera movement should feel calm and deliberate, with no sudden jumps or aggressive acceleration.

SOUND:
- Add a quiet original ambient music track suited to an isolated lighthouse at dusk, using restrained sustained tones and occasional gentle notes.
- Include continuous ocean wash, soft coastal wind, and individual wave impacts synchronized with visible shoreline splashes.
- All music, ambience, and sound effects must be synthesized in code. No external audio files.
- Start audio on the first user interaction, with a small “Click for sound” hint and a visible mute/unmute control.
- Fade audio in smoothly and keep the music below the environmental sounds.
- Log audio initialization and representative sound events to the console to confirm they fire. Do not flood the console every frame.

UI:
- Title in the lower-left: a large, elegant serif title, `THE LAST LIGHT`, with a small atmospheric subtitle.
- Below it, show: “Drag to orbit · Scroll to zoom”.
- Place CINEMATIC, RESET VIEW, and SOUND controls in the lower-right.
- Keep controls small, legible, and visually consistent, with restrained translucent backgrounds.
- UI fades out after roughly 10 seconds of inactivity and reappears on pointer movement.
- Only the actual buttons should capture pointer events; decorative overlays must not block camera input.

IMPLEMENTATION AND PERFORMANCE:
- Fill the browser window and resize cleanly without stretching, clipping, or losing the composition.
- Target smooth 30–60 fps on a typical desktop, using sensible geometry budgets, instancing, and efficient shaders.
- Prioritize the lighthouse silhouette, convincing water, coherent lighting, and smooth motion.
- Draw all geometry and generate all textures, sky effects, particles, and audio in code. Never fetch or hotlink an image, texture, model, or sound.
- Deliver one complete HTML file containing the application code, styles, shaders, and required library code so it works without a network connection.
- Start with zero console errors, missing resources, or unhandled exceptions.

TESTING PROTOCOL:
- Test the actual rendered output in a local headed Chromium using browser MCP or Playwright tools. Do not rely solely on code inspection or unit tests.
- Inspect the scene at sunset, twilight, and full night, including the beam, water reflections, breaking waves, and visibility of the island.
- Test cinematic mode, manual orbit, zoom limits, reset view, window resizing, UI fading, and audio activation.
- Inspect multiple camera angles for disconnected geometry, shoreline gaps, clipping, and incorrect reflections.
- Check the console for errors and confirm that audio events fire.
- Do not claim a feature works unless it has been verified. If the required browser testing is unavailable, state that clearly.