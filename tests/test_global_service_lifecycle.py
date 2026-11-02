import importlib.util
import sys
import types
from pathlib import Path


def load_service(monkeypatch, socket_server_type, observer_type):
    messages = []
    freecad = types.ModuleType("FreeCAD")

    class Console:
        @staticmethod
        def PrintMessage(message):
            messages.append(("message", message))

        @staticmethod
        def PrintError(message):
            messages.append(("error", message))

        @staticmethod
        def PrintWarning(message):
            messages.append(("warning", message))

    freecad.Console = Console()
    freecad.getUserAppDataDir = lambda: str(Path.cwd())
    gui = types.ModuleType("FreeCADGui")
    gui.Workbench = object
    gui.addWorkbench = lambda workbench: None
    gui.addCommand = lambda name, command: None

    socket_module = types.ModuleType("socket_server")
    socket_module.FreeCADSocketServer = socket_server_type
    observer_module = types.ModuleType("event_observer")
    observer_module.FreeCADEventObserver = observer_type

    monkeypatch.setitem(sys.modules, "FreeCAD", freecad)
    monkeypatch.setitem(sys.modules, "FreeCADGui", gui)
    monkeypatch.setitem(sys.modules, "socket_server", socket_module)
    monkeypatch.setitem(sys.modules, "event_observer", observer_module)

    path = Path(__file__).parents[1] / "AICopilot" / "InitGui.py"
    spec = importlib.util.spec_from_file_location("cadpilot_test_init_gui", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.GlobalAIService, freecad, messages


def test_observer_start_failure_does_not_leave_false_active_reference(monkeypatch):
    calls = []

    class SocketServer:
        def start_server(self):
            return True

        def stop_server(self):
            calls.append("socket_stop")

    class Observer:
        def start(self):
            calls.append("observer_start")
            raise RuntimeError("Qt observer unavailable")

        def stop(self):
            calls.append("observer_stop")

    service_type, freecad, messages = load_service(monkeypatch, SocketServer, Observer)
    service = service_type()

    assert service.start() is True
    assert service.is_running is True
    assert service.socket_server is not None
    assert service.event_observer is None
    assert not hasattr(freecad, "__ai_observer")
    assert "observer_stop" in calls
    assert any("remains active" in message for kind, message in messages if kind == "warning")


def test_shutdown_attempts_observer_cleanup_when_socket_shutdown_raises(monkeypatch):
    calls = []

    class SocketServer:
        def start_server(self):
            return True

        def stop_server(self):
            calls.append("socket_stop")
            raise RuntimeError("socket close failed")

    class Observer:
        def start(self):
            calls.append("observer_start")

        def stop(self):
            calls.append("observer_stop")

    service_type, freecad, messages = load_service(monkeypatch, SocketServer, Observer)
    service = service_type()
    assert service.start() is True

    service.stop()

    assert service.is_running is False
    assert service.socket_server is None
    assert service.event_observer is None
    assert calls.count("socket_stop") == 1
    assert calls.count("observer_stop") == 1
    assert not hasattr(freecad, "__ai_global_service")
    assert any("socket close failed" in message for kind, message in messages if kind == "error")
