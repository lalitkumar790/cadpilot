"""Explicit Part-workbench tools: primitives, booleans, and transforms.

Each tool maps 1:1 onto an existing explicit tool_name already handled by
AICopilot/socket_server.py on the FreeCAD side (create_box, fuse_objects,
move_object, etc.) — no changes to the FreeCAD-side code were required.
"""
from __future__ import annotations

from freecad_mcp.server import dispatch, mcp_server


@mcp_server.tool()
def create_box(
    length: float = 10,
    width: float = 10,
    height: float = 10,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    name: str | None = None,
) -> str:
    """Create a rectangular box solid in FreeCAD."""
    return dispatch("create_box", length=length, width=width, height=height, x=x, y=y, z=z, name=name)


@mcp_server.tool()
def create_cylinder(
    radius: float = 5,
    height: float = 10,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    name: str | None = None,
) -> str:
    """Create a cylinder solid in FreeCAD."""
    return dispatch("create_cylinder", radius=radius, height=height, x=x, y=y, z=z, name=name)


@mcp_server.tool()
def create_sphere(radius: float = 5, x: float = 0, y: float = 0, z: float = 0, name: str | None = None) -> str:
    """Create a sphere solid in FreeCAD."""
    return dispatch("create_sphere", radius=radius, x=x, y=y, z=z, name=name)


@mcp_server.tool()
def create_cone(
    radius1: float = 10,
    radius2: float = 3,
    height: float = 10,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    name: str | None = None,
) -> str:
    """Create a cone (or frustum) solid in FreeCAD."""
    return dispatch("create_cone", radius1=radius1, radius2=radius2, height=height, x=x, y=y, z=z, name=name)


@mcp_server.tool()
def create_torus(
    radius1: float = 10,
    radius2: float = 3,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    name: str | None = None,
) -> str:
    """Create a torus (donut) solid in FreeCAD."""
    return dispatch("create_torus", radius1=radius1, radius2=radius2, x=x, y=y, z=z, name=name)


@mcp_server.tool()
def create_wedge(
    length: float = 10,
    width: float = 10,
    height: float = 10,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    name: str | None = None,
) -> str:
    """Create a wedge solid in FreeCAD."""
    return dispatch("create_wedge", length=length, width=width, height=height, x=x, y=y, z=z, name=name)


@mcp_server.tool()
def boolean_union(objects: list[str], name: str | None = None) -> str:
    """Fuse (boolean union) two or more objects into one solid."""
    return dispatch("fuse_objects", objects=objects, name=name)


@mcp_server.tool()
def boolean_cut(base: str, tools: list[str], name: str | None = None) -> str:
    """Subtract `tools` objects from `base` (boolean cut)."""
    return dispatch("cut_objects", base=base, tools=tools, name=name)


@mcp_server.tool()
def boolean_intersection(objects: list[str], name: str | None = None) -> str:
    """Keep only the overlapping volume of the given objects (boolean common)."""
    return dispatch("common_objects", objects=objects, name=name)


@mcp_server.tool()
def move_object(object_name: str, x: float = 0, y: float = 0, z: float = 0) -> str:
    """Translate an object by (x, y, z)."""
    return dispatch("move_object", object_name=object_name, x=x, y=y, z=z)


@mcp_server.tool()
def rotate_object(object_name: str, axis: str = "z", angle: float = 90) -> str:
    """Rotate an object around the given axis ('x', 'y', or 'z') by angle in degrees."""
    return dispatch("rotate_object", object_name=object_name, axis=axis, angle=angle)


@mcp_server.tool()
def copy_object(object_name: str, name: str | None = None) -> str:
    """Duplicate an existing object."""
    return dispatch("copy_object", object_name=object_name, name=name)


@mcp_server.tool()
def array_object(
    object_name: str,
    count: int = 3,
    spacing: float = 10,
    axis: str = "x",
) -> str:
    """Create a linear array (pattern) of an object along an axis."""
    return dispatch("array_object", object_name=object_name, count=count, spacing=spacing, axis=axis)
