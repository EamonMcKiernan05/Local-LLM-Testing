 Create an interactive 3D scene in Three.js: a medieval village at golden hour.

Rules:

One HTML file, with no build step or server required — it must open by double-clicking. Three.js may be loaded from a CDN.
Do not download assets (models, textures, or HDRIs). Build every model in code and generate every texture procedurally (canvas or shader). Quality must come from code, not downloaded assets.
The village must include at least: 12 half-timbered houses with variation (size, floors, rotation, and colour), a church with a tower, a windmill with rotating blades, a central well in a stone plaza, market stalls with goods, a lake or river with animated reflective water, fences, trees, paths, and props (barrels, a cart, hay bales).
Life in the scene: simple villagers walking through the village, chimney smoke, rotating windmill blades, lit lanterns, birds, fireflies at dusk, and moving clouds. Motion should be subtle and believable.
Convincing procedural textures: plaster, wood grain, straw, roof tile, stone, and grass, with bump or normal detail rather than flat colour.
Golden-hour lighting: a low, warm sun with high-resolution soft shadows, atmospheric fog, a sunset-gradient sky, and a visible sun near the horizon.
Post-processing: at minimum, bloom (lit windows, lanterns, and the sun should glow) and cinematic tone mapping.
An orbital camera (mouse/trackpad) with a slow automatic tour until the user interacts.
Assume a powerful machine: thousands of instanced vegetation elements, 4K shadows, and dense geometry. Do not economize on detail; visual impact is an evaluation criterion.
Invest in art direction: a coherent palette, a believable village composition, and an appealing horizon silhouette.
You must test the actual rendered output in a **local headed Chromium**, using the browser MCP/Playwright tools. Do not rely on code inspection or unit tests. Do not claim a feature works unless you have seen it. Zero console errors.