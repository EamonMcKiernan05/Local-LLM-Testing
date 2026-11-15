# Liberty — one-shot prompt

Captured from the DeepSeek Harness session log. Verbatim, as sent.

```text
Build a single self-contained HTML file (three.js r160 from cdn.jsdelivr via importmap) that renders a detailed voxel diorama: "Liberty Island & New York, autumn 1886 — dedication day of the Statue of Liberty", as a floating island in a warm hazy sky.

STYLE
- Chunky voxels with slightly beveled (chamfered) edges, vertex colors with per-voxel color jitter and baked ambient occlusion.
- Golden-hour light: low warm sun (ACES tone mapping, soft PCF shadows), sky-dome gradient with a sun glow, warm haze fog, subtle bloom.
- Floating island: grassy rim, layered rock strata on the sides, a jagged rocky underside with hanging stalactites. Small floating islets with autumn trees drift around it, plus a few voxel clouds.

LAYOUT
- Center: Bedloe's Island with star-shaped Fort Wood (11 points, granite + red brick walls), autumn trees, a seawall, small piers.
- On it: the granite pedestal with its loggia openings, and THE STATUE (must be instantly recognizable): green patina, flowing robe with vertical folds and a diagonal sash, raised right arm holding a torch with a balcony and a glowing gold flame, a tablet in the left arm with "JULY IV MDCCLXXVI", a crown with 7 rays and windows, a broad face.
- Around it: a harbor ring of animated water with waves, a paddle-wheel ferry, a tugboat with smoke, and a three-masted sailing ship.
- Behind it: a crescent of 1886 Manhattan on a street grid. Brownstones, red-brick tenements with black iron fire escapes, cast-iron store buildings with striped awnings, waterfront warehouses, wooden water tanks on the rooftops, chimneys with smoke, gas lamps with warm glow, a few lit windows, a gothic Trinity-style church with a tall spire, a white New England steeple church, a Central-Park-style green with a pond and a bandstand, US flags on rooftops.
- A river channel cuts through the city to the island edge, with the Brooklyn Bridge over it: granite towers with twin gothic arches, 4 main cables, vertical suspenders and the diagonal stay web, carriages and pedestrians crossing.
- An elevated railway (the El) on iron columns along one avenue, with a small steam engine pulling 3 cars and puffing smoke.
- Waterfalls pour off the island rim where the water reaches the edge, with mist at the bottom.

LIFE (all deterministic, driven by time t)
- Hundreds of tiny voxel people: pedestrians on sidewalks, crowds on the waterfront and a dedication grandstand with red-white-blue bunting, some waving and some holding parasols.
- Horse-drawn cabs on the streets, waving flags, seagulls circling the statue, smoke and steam particles.

CAMERA & OUTPUT
- A 10-second slow orbit of about 100° around the whole island with a slight zoom-in, the island always fully in frame (like a turntable showcase shot).
- Expose window.renderAt(t) for frame-by-frame capture at 30 or 60 fps, canvas sized from URL params ?w=&h= (default 1920x1080).
- Performance: merge static voxels into chunked meshes, cull hidden faces, use instancing for people and particles, and render the static shadow map once.

TESTING PROTOCOL

You must test the actual rendered output in a **local headed Chromium**, using the browser MCP/Playwright tools. Do not rely on code inspection or unit tests. Do not claim a feature works unless you have seen it.
```
