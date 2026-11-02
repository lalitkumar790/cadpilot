"""Explicit PartDesign-workbench tools: sketches, pads, and dress-up features.

Fillet/chamfer/hole operations require an edge or face selection in FreeCAD;
the underlying socket server will return an ``awaiting_selection`` response
which freecad_mcp.server.dispatch converts into an interactive prompt. Follow
up with the continue_selection tool (see freecad_mcp.tools.selection).
"""
from __future__ import annotations

from freecad_mcp.server import dispatch, mcp_server


@mcp_server.tool()
def create_sketch(plane: str = "XY", name: str | None = None) -> str:
    """Create a new sketch on the given plane ('XY', 'XZ', or 'YZ')."""
    return dispatch("create_sketch", plane=plane, name=name)


@mcp_server.tool()
def pad(sketch_name: str, length: float = 10, name: str | None = None) -> str:
    """Extrude (pad) a sketch into a solid by `length`."""
    return dispatch("pad_sketch", sketch_name=sketch_name, length=length, name=name)


@mcp_server.tool()
def revolution(sketch_name: str, angle: float = 360, axis: str = "x", name: str | None = None) -> str:
    """Revolve a sketch around an axis to create a solid."""
    return dispatch("revolution", sketch_name=sketch_name, angle=angle, axis=axis, name=name)


@mcp_server.tool()
def loft(sketches: list[str], name: str | None = None) -> str:
    """Loft a solid through a sequence of sketch profiles."""
    return dispatch("loft_profiles", sketches=sketches, name=name)


@mcp_server.tool()
def sweep(profile_sketch: str, path_sketch: str, name: str | None = None) -> str:
    """Sweep a profile sketch along a path sketch."""
    return dispatch("sweep_path", profile_sketch=profile_sketch, path_sketch=path_sketch, name=name)


@mcp_server.tool()
def fillet(object_name: str, radius: float = 1, name: str | None = None) -> str:
    """Round selected edges of an object. Requires selecting edges in FreeCAD
    first (an interactive selection prompt is returned if none are selected)."""
    return dispatch("fillet_edges", object_name=object_name, radius=radius, name=name)


@mcp_server.tool()
def chamfer(object_name: str, distance: float = 1, name: str | None = None) -> str:
    """Bevel selected edges of an object. Requires selecting edges in FreeCAD
    first (an interactive selection prompt is returned if none are selected)."""
    return dispatch("chamfer_edges", object_name=object_name, distance=distance, name=name)


@mcp_server.tool()
def hole(
    object_name: str,
    diameter: float = 6,
    depth: float = 10,
    x: float = 0,
    y: float = 0,
    name: str | None = None,
) -> str:
    """Add a hole feature to a face. Requires selecting a face in FreeCAD first."""
    return dispatch("hole_wizard", object_name=object_name, diameter=diameter, depth=depth, x=x, y=y, name=name)


@mcp_server.tool()
def mirror_feature(object_name: str, plane: str = "YZ", name: str | None = None) -> str:
    """Mirror an object across a plane ('XY', 'XZ', or 'YZ')."""
    return dispatch("mirror_feature", object_name=object_name, plane=plane, name=name)


@mcp_server.tool()
def linear_pattern(
    object_name: str,
    count: int = 3,
    spacing: float = 10,
    axis: str = "x",
    name: str | None = None,
) -> str:
    """Create a linear pattern of a feature."""
    return dispatch("linear_pattern", object_name=object_name, count=count, spacing=spacing, axis=axis, name=name)


@mcp_server.tool()
def polar_pattern(
    object_name: str,
    count: int = 4,
    angle: float = 360,
    name: str | None = None,
) -> str:
    """Create a polar (circular) pattern of a feature."""
    return dispatch("polar_pattern", object_name=object_name, count=count, angle=angle, name=name)


@mcp_server.tool()
def shell_solid(object_name: str, thickness: float = 2, name: str | None = None) -> str:
    """Hollow out a solid, leaving a wall of the given thickness. Requires
    selecting the face(s) to remove in FreeCAD first."""
    return dispatch("shell_solid", object_name=object_name, thickness=thickness, name=name)
