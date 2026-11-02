"""View, document, and object-management tools."""
from __future__ import annotations

from freecad_mcp.server import dispatch, mcp_server


@mcp_server.tool()
def capture_screenshot(width: int = 800, height: int = 600) -> str:
    """Capture a screenshot of the current FreeCAD 3D view."""
    return dispatch("get_screenshot", width=width, height=height)


@mcp_server.tool()
def set_view(view_type: str = "isometric") -> str:
    """Set the 3D view orientation. One of: top, front, left, right, isometric, axonometric."""
    return dispatch("set_view", view_type=view_type)


@mcp_server.tool()
def fit_all() -> str:
    """Zoom/fit the 3D view to show all objects."""
    return dispatch("fit_all")


@mcp_server.tool()
def save_document(filename: str | None = None) -> str:
    """Save the active FreeCAD document. Provide `filename` to Save As."""
    return dispatch("save_document", filename=filename)


@mcp_server.tool()
def export_step(object_name: str, filename: str) -> str:
    """Export an object to a STEP file (.step / .stp)."""
    return dispatch("execute_python", code=(
        "import Part, FreeCAD\n"
        f"obj = FreeCAD.ActiveDocument.getObject({object_name!r})\n"
        f"Part.export([obj], {filename!r})\n"
        f"'Exported {{}} to {filename}'.format(obj.Name) if obj else 'Object not found'"
    ))


@mcp_server.tool()
def export_stl(object_name: str, filename: str) -> str:
    """Export an object to an STL file, e.g. for 3D printing."""
    return dispatch("execute_python", code=(
        "import Mesh, FreeCAD\n"
        f"obj = FreeCAD.ActiveDocument.getObject({object_name!r})\n"
        f"Mesh.export([obj], {filename!r})\n"
        f"'Exported {{}} to {filename}'.format(obj.Name) if obj else 'Object not found'"
    ))


@mcp_server.tool()
def list_all_objects() -> str:
    """List all objects in the active FreeCAD document."""
    return dispatch("list_all_objects")


@mcp_server.tool()
def select_object(object_name: str) -> str:
    """Select an object in the FreeCAD 3D view."""
    return dispatch("select_object", object_name=object_name)


@mcp_server.tool()
def clear_selection() -> str:
    """Clear the current FreeCAD selection."""
    return dispatch("clear_selection")


@mcp_server.tool()
def hide_object(object_name: str) -> str:
    """Hide an object in the 3D view."""
    return dispatch("hide_object", object_name=object_name)


@mcp_server.tool()
def show_object(object_name: str) -> str:
    """Show a previously hidden object."""
    return dispatch("show_object", object_name=object_name)


@mcp_server.tool()
def delete_object(object_name: str) -> str:
    """Delete an object from the active document. This cannot be undone via MCP."""
    return dispatch("delete_object", object_name=object_name)


@mcp_server.tool()
def undo() -> str:
    """Undo the last operation in FreeCAD."""
    return dispatch("undo")


@mcp_server.tool()
def redo() -> str:
    """Redo the last undone operation in FreeCAD."""
    return dispatch("redo")


@mcp_server.tool()
def activate_workbench(workbench_name: str) -> str:
    """Switch the active FreeCAD workbench (e.g. 'PartDesignWorkbench', 'PartWorkbench')."""
    return dispatch("activate_workbench", workbench_name=workbench_name)


@mcp_server.tool()
def get_mass_properties(object_name: str) -> str:
    """Get volume, mass, and center of mass for an object."""
    return dispatch("get_mass_properties", object_name=object_name)


@mcp_server.tool()
def get_bounding_box(object_name: str) -> str:
    """Get the bounding box dimensions of an object."""
    return dispatch("get_bounding_box", object_name=object_name)
