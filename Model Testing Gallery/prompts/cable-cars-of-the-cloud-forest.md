# Cable Cars of the Cloud Forest

Create a full-scale cloud forest crossed by a passenger cable loop between a valley market and a ridge station. Below the line, a wide alpine reservoir disappears into forested ravines. A third station on a rocky spur gives the cables a triangular route.

## World and daylight

Build a full-scale, photorealistic Three.js scene in perspective. Space the named locations far enough apart for the viewer to travel through them. Give close objects backs and thickness, carry detail around bends and extend the landscape to the visible horizon in every direction the flight reveals.

Use early golden light with low banks of cloud almost level with the middle station. Give fog local depth, with the nearby trunks occasionally clear against luminous banks. Colour pasture grass warmer near the market and shadowed moss cooler near the ridge.

## Water and wind

One reservoir extends through all flooded ravines to a distant shore. The bright cloud reflection should disappear progressively under a forest overhang. Tree ferns at the water’s edge move in sheltered air while the ridge flags react more strongly to the same wind episode.

Use exactly one stationary water object for the entire scene, a single connected, indexed Three.js mesh with shared vertices. Fix its world transform, footprint and mean level. Extend it under the banks and beyond the longest view. Where it meets land, keep terrain and water overlapping even at maximum trough. Animate waves by bounded vertical displacement and surface shading. Paint foam and wakes on that same mesh. No separate tiles or water strips. At every phase there must be zero visible gaps at the shoreline or inside the water surface.

## People, wildlife and motion

Space the cabins on a closed haul-rope circuit with sensible sag and pulley turns, keeping cabins upright on hangers and clear of the tree canopy. A porter and market vendor walk independent concourse circuits outside the boarding threshold.

Choreograph every moving element on one fixed **96-second master loop**, driven by elapsed simulation time. At 96 seconds every actor, prop and effect must match its opening position, orientation, pose and velocity. Fit whole stride, wheel or wingbeat cycles to each applicable path. Make wind, vegetation, clouds, waves, wakes and shadows periodic too. Carry wake history across the seam. An actor that leaves the frame must physically complete its route.

## Cinematic flight

Leave the valley station, follow the ravine beneath the level of the cables, climb through an empty notch to the ridge, sweep behind the spur station and descend the uncovered hillside beside the market to the original platform view.

Start with **Cinematic** on. Fly the complete route on a smooth closed 3D path in one uninterrupted take. Use foreground parallax, changes of altitude and deliberate reveals. Match position, heading, speed, bank and lens across the seam. In Manual, keep the camera on its safe flight path while drag adjusts the view and wheel or pinch changes the lens. Re-enable Cinematic with a gentle return to the authored framing. **Pause** holds the master clock for inspection. **Reset View** restarts the complete take.

## What to check

Frame the middle part of the route so the viewer sees one cabin emerge from cloud while its reflection appears in a clear patch below. Apply collision checks to hung cabins at maximum sway and to the camera near the cable saddle.

Check the camera’s near plane at its widest lens and each actor’s full swept volume between waypoints, including the last-to-first segment. Test against solid terrain, trees, rocks, walls, buildings and the other actors at the same instant. Include limbs and carried gear. Keep intended contacts stable and reroute any segment that clips. Inspect the water at grazing angles at both crest and trough. Compare equivalent frames from two full laps and step through the seam.

## Output

Return only one complete, self-contained HTML file that opens locally and runs offline. Inline the actual Three.js runtime, JavaScript, shaders, styles and controls. Generate all meshes, textures, skies and any sound procedurally from a fixed seed. Use no external assets, downloads or companion files. Fill the window, handle resize, instance repeated details and cap pixel ratio for smooth playback.