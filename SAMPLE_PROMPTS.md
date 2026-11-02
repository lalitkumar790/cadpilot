# Sample prompts for CADPilot

Try these in Claude Desktop after `check_freecad_connection` reports `connected: true`.

## Beginner — Part workbench

1. Create a box with length 40 mm, width 30 mm, height 20 mm. Name it `BaseBlock`.
2. Create a cylinder with radius 6 mm and height 25 mm. Name it `Pin`.
3. Move `Pin` to X=20 mm, Y=15 mm, Z=20 mm.
4. Set the view to isometric and fit all objects.
5. List all objects in the current document.

## Boolean modelling

1. Create two overlapping boxes named `BlockA` and `BlockB`.
2. Create a Boolean union of `BlockA` and `BlockB`.
3. In a fresh document, create a base block and a cylinder that passes through it.
4. Subtract the cylinder from the base block using a Boolean cut.
5. Explain which objects remain after the operation. Do not delete anything unless I explicitly approve.

## PartDesign

1. Create a sketch on the XY plane.
2. Help me create a simple rectangular profile and pad it by 12 mm.
3. Explain which edges I need to select before applying a 2 mm fillet.
4. Wait for me to select the edges in FreeCAD before continuing.

## Inspection and export

1. List all objects and report their bounding-box dimensions.
2. Report the volume and centre of mass of `BaseBlock`.
3. Set the view to top, then return to isometric.
4. Save the active document.
5. Export `BaseBlock` as STEP to a path I specify. Ask me for the path if it is missing.

## Good prompting habits

- Give dimensions and units explicitly.
- Give every important object a unique name.
- Ask Claude to list objects before modifying an existing model.
- Ask it to explain a proposed destructive operation before executing it.
- Save a copy before major edits.
- Verify dimensions in FreeCAD's property panel and measure tools.
