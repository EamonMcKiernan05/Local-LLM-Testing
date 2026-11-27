# Bronze Grass at Crane Lake

Make a full-scale steppe basin where demoiselle cranes circle a long, shallow lake between grassland burial mounds. A felt camp and an old track sit a kilometre of blue haze away from the far escarpment.

## World and daylight

Build a full-scale, photorealistic Three.js scene in perspective. Space the named locations far enough apart for the viewer to travel through them. Give close objects backs and thickness, carry detail around bends and extend the landscape to the visible horizon in every direction the flight reveals.

Use clear morning light across the mounds. Build grass in patches of different height, pale at the tips and almost black on the lee side of a mound. Give the camp sewn fabric, bent poles and a tethered felt flap.

## Water and wind

One connected lake runs behind the nearest two mounds and laps the hard mud below the camp. A broad band of wind roughens it progressively from upwind to downwind. Grazed grass near the shore should respond less than tall feathergrass on the basin floor.

Use exactly one stationary water object for the entire scene, a single connected, indexed Three.js mesh with shared vertices. Fix its world transform, footprint and mean level. Extend it under the banks and beyond the longest view. Where it meets land, keep terrain and water overlapping even at maximum trough. Animate waves by bounded vertical displacement and surface shading. Paint foam and wakes on that same mesh. No separate tiles or water strips. At every phase there must be zero visible gaps at the shoreline or inside the water surface.

## People, wildlife and motion

A flock of seven cranes traces a long circuit with a banking turn above the lake and a lower return flight above the grass. Fix individual offsets and stagger wingbeats. Two horses graze within separate clear patches, raising their heads on different repeatable phases.

Choreograph every moving element on one fixed **96-second master loop**, driven by elapsed simulation time. At 96 seconds every actor, prop and effect must match its opening position, orientation, pose and velocity. Fit whole stride, wheel or wingbeat cycles to each applicable path. Make wind, vegetation, clouds, waves, wakes and shadows periodic too. Carry wake history across the seam. An actor that leaves the frame must physically complete its route.

## Cinematic flight

Begin on the old track, fly low between two mounds, skim the reed margin, climb along the inward-facing escarpment, cross behind the camp and descend to the track. Keep the crane corridor on the lakeward side of the flight.

Start with **Cinematic** on. Fly the complete route on a smooth closed 3D path in one uninterrupted take. Use foreground parallax, changes of altitude and deliberate reveals. Match position, heading, speed, bank and lens across the seam. In Manual, keep the camera on its safe flight path while drag adjusts the view and wheel or pinch changes the lens. Re-enable Cinematic with a gentle return to the authored framing. **Pause** holds the master clock for inspection. **Reset View** restarts the complete take.

## What to check

The bright bank of pale crane wings should move across a darker strip of hillside while the wind line below continues across the water. The two bands travel at different speeds and repeat at the same global phase.

Check the camera’s near plane at its widest lens and each actor’s full swept volume between waypoints, including the last-to-first segment. Test against solid terrain, trees, rocks, walls, buildings and the other actors at the same instant. Include limbs and carried gear. Keep intended contacts stable and reroute any segment that clips. Inspect the water at grazing angles at both crest and trough. Compare equivalent frames from two full laps and step through the seam.

## Output

Return only one complete, self-contained HTML file that opens locally and runs offline. Inline the actual Three.js runtime, JavaScript, shaders, styles and controls. Generate all meshes, textures, skies and any sound procedurally from a fixed seed. Use no external assets, downloads or companion files. Fill the window, handle resize, instance repeated details and cap pixel ratio for smooth playback.